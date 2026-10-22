#!/usr/bin/env python3
"""Generate images through a configured OpenAI-compatible Images API."""

from __future__ import annotations

import argparse
import base64
import errno
import getpass
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import ProxyHandler, Request, build_opener, getproxies


DEFAULT_MODEL_TIMEOUT = 30
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "medium"
DEFAULT_FORMAT = "png"
DEFAULT_OUTPUT = "output/custom-imagegen/output.png"
MAX_RESPONSE_BYTES = 100 * 1024 * 1024
EXIT_PERMISSION_REQUIRED = 3


class ConfigError(Exception):
    pass


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def is_permission_denial(error: BaseException) -> bool:
    if isinstance(error, HTTPError):
        return False
    if isinstance(error, PermissionError):
        return True
    if isinstance(error, OSError) and error.errno in {errno.EACCES, errno.EPERM, errno.EROFS}:
        return True
    if isinstance(error, URLError):
        reason = error.reason
        if isinstance(reason, BaseException):
            return is_permission_denial(reason)
        if isinstance(reason, str):
            return any(message in reason.lower() for message in (
                "operation not permitted", "permission denied", "read-only file system",
            ))
    return False


def permission_required(operation: str) -> None:
    die(
        f"PERMISSION_REQUIRED: {operation} encountered a local permission denial. "
        "The calling agent must request access through the host's approval mechanism "
        "unless current host instructions explicitly prohibit it, then resume after approval. "
        "This error does not establish that approval requests are forbidden. "
        "Before resubmitting generation, confirm the previous request was never submitted.",
        EXIT_PERMISSION_REQUIRED,
    )


def default_config_path() -> Path:
    override = os.getenv("CUSTOM_IMAGEGEN_CONFIG", "").strip()
    if override:
        return Path(override).expanduser()
    config_home = os.getenv("XDG_CONFIG_HOME", "").strip()
    root = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return root / "custom-imagegen" / ".env"


def config_path(raw: str | None) -> Path:
    return Path(raw).expanduser() if raw else default_config_path()


def parse_env(path: Path, *, required: bool = True) -> dict[str, str]:
    try:
        contents = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        if required:
            raise ConfigError(f"configuration file not found: {path}")
        return {}

    values: dict[str, str] = {}
    for line_no, raw in enumerate(contents.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ConfigError(f"invalid configuration line {line_no} in {path}")
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[name] = value
    return values


def normalize_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigError("base URL must be an absolute HTTP(S) URL")
    path = parsed.path.rstrip("/")
    if not path.endswith("/v1"):
        path += "/v1"
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def load_config(path: Path) -> tuple[str, str, str]:
    values = parse_env(path, required=False)
    api_key = (
        os.getenv("CUSTOM_IMAGEGEN_API_KEY", "").strip()
        or values.get("OPENAI_API_KEY", "").strip()
        or values.get("OPENAI_IMAGE_API_KEY", "").strip()
        or os.getenv("OPENAI_IMAGE_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
    )
    base_url = (
        os.getenv("CUSTOM_IMAGEGEN_BASE_URL", "").strip()
        or values.get("AI_BASE_URL", "").strip()
        or values.get("OPENAI_IMAGE_BASE_URL", "").strip()
        or values.get("OPENAI_BASE_URL", "").strip()
        or os.getenv("AI_BASE_URL", "").strip()
        or os.getenv("OPENAI_IMAGE_BASE_URL", "").strip()
        or os.getenv("OPENAI_BASE_URL", "").strip()
    )
    missing = []
    if not api_key:
        missing.append("API key")
    if not base_url:
        missing.append("base URL")
    if missing:
        configure = Path(__file__).resolve()
        raise ConfigError(
            f"missing {' and '.join(missing)}; run `python3 {configure} configure` "
            f"or provide a config file at {path}"
        )
    source = str(path) if path.is_file() else "environment variables"
    return api_key, normalize_base_url(base_url), source


def safe_value(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise ConfigError(f"{label} must not be empty")
    if "\n" in value or "\r" in value:
        raise ConfigError(f"{label} must be a single line")
    return value


def write_config(path: Path, api_key: str, base_url: str) -> None:
    api_key = safe_value(api_key, "API key")
    base_url = normalize_base_url(safe_value(base_url, "base URL"))
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    temporary = path.with_name(path.name + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"OPENAI_API_KEY={api_key}\n")
            handle.write(f"AI_BASE_URL={base_url}\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def command_configure(args: argparse.Namespace) -> None:
    destination = config_path(args.config)
    existing = parse_env(destination, required=False)
    imported: dict[str, str] = {}
    if args.from_env_file:
        imported = parse_env(Path(args.from_env_file).expanduser())

    base_url = (
        args.base_url
        or imported.get("AI_BASE_URL")
        or imported.get("OPENAI_IMAGE_BASE_URL")
        or imported.get("OPENAI_BASE_URL")
        or existing.get("AI_BASE_URL")
        or existing.get("OPENAI_BASE_URL")
        or ""
    )
    api_key = (
        imported.get("OPENAI_API_KEY")
        or imported.get("OPENAI_IMAGE_API_KEY")
        or imported.get("CUSTOM_IMAGEGEN_API_KEY")
        or existing.get("OPENAI_API_KEY")
        or ""
    )
    if args.api_key_env:
        api_key = os.getenv(args.api_key_env, "").strip()
        if not api_key:
            raise ConfigError(f"environment variable {args.api_key_env} is missing or empty")

    noninteractive_complete = bool(base_url and api_key) and bool(
        args.from_env_file or args.api_key_env
    )
    if not noninteractive_complete:
        if not sys.stdin.isatty():
            raise ConfigError(
                "interactive input is unavailable; use --from-env-file PATH, or "
                "use --base-url URL together with --api-key-env VARIABLE"
            )
        base_hint = f" [{base_url}]" if base_url else ""
        entered_base = input(f"OpenAI-compatible base URL{base_hint}: ").strip()
        if entered_base:
            base_url = entered_base
        key_hint = " (press Enter to keep the existing key)" if api_key else ""
        entered_key = getpass.getpass(f"API key{key_hint}: ").strip()
        if entered_key:
            api_key = entered_key

    write_config(destination, api_key, base_url)
    _, normalized, _ = load_config(destination)
    parsed = urlsplit(normalized)
    print(json.dumps({
        "config": str(destination),
        "permissions": "0600",
        "api_key": "set",
        "api_host": parsed.hostname,
        "api_path": parsed.path,
    }, ensure_ascii=False, indent=2))


def safe_proxy_handler() -> ProxyHandler:
    proxies = {}
    for scheme, url in getproxies().items():
        if scheme not in {"http", "https"}:
            continue
        if url.lower().startswith(("http://", "https://")):
            proxies[scheme] = url
    return ProxyHandler(proxies)


def read_limited(response: Any) -> bytes:
    data = response.read(MAX_RESPONSE_BYTES + 1)
    if len(data) > MAX_RESPONSE_BYTES:
        die("API response exceeded the 100 MiB safety limit")
    return data


def request_json(
    url: str,
    api_key: str,
    payload: dict[str, Any] | None,
    timeout: int,
    *,
    operation: str = "Image API",
    attempts: int = 3,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "codex-custom-imagegen/2.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        url,
        data=body,
        method="POST" if body is not None else "GET",
        headers=headers,
    )
    opener = build_opener(safe_proxy_handler())
    for attempt in range(1, attempts + 1):
        try:
            with opener.open(request, timeout=timeout) as response:
                raw = read_limited(response)
            result = json.loads(raw.decode("utf-8"))
            if not isinstance(result, dict):
                die(f"{operation} returned an unexpected JSON response")
            return result
        except HTTPError as exc:
            detail = exc.read(8192).decode("utf-8", errors="replace")
            detail = detail.replace(api_key, "<redacted>")
            detail = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+", "Bearer <redacted>", detail)
            if (exc.code == 429 or 500 <= exc.code < 600) and attempt < attempts:
                delay = min(8, 2**attempt)
                print(f"Transient HTTP {exc.code}; retrying in {delay}s.", file=sys.stderr)
                time.sleep(delay)
                continue
            die(f"{operation} returned HTTP {exc.code}: {detail[:1000]}")
        except OSError as exc:
            if is_permission_denial(exc):
                permission_required(operation)
            if attempt < attempts:
                delay = min(8, 2**attempt)
                print(f"Network error; retrying in {delay}s.", file=sys.stderr)
                time.sleep(delay)
                continue
            die(f"{operation} request failed: {exc}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            die(f"{operation} returned invalid JSON")
    die(f"{operation} request failed after retries")
    return {}


def fetch_image_models(api_key: str, base_url: str, timeout: int) -> list[str]:
    result = request_json(
        base_url + "/models",
        api_key,
        None,
        timeout,
        operation="Image model discovery",
        attempts=1,
    )
    data = result.get("data")
    if not isinstance(data, list):
        die("could not read image models: /models returned an invalid model list; generation stopped")
    model_ids = set()
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            die("could not read image models: /models returned an invalid model entry; generation stopped")
        model_id = item["id"]
        if model_id.startswith("gpt-image-") and model_id != "gpt-image-":
            model_ids.add(model_id)
    if not model_ids:
        die("server returned no supported gpt-image-* image models; generation stopped")
    return sorted(model_ids)


def download_image(url: str, api_key: str, timeout: int) -> bytes:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        die("API returned an unsupported image URL")
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "codex-custom-imagegen/2.0",
        },
    )
    try:
        with build_opener(safe_proxy_handler()).open(request, timeout=timeout) as response:
            return read_limited(response)
    except HTTPError as exc:
        die(f"failed to download generated image: {exc}")
    except OSError as exc:
        if is_permission_denial(exc):
            permission_required("Generated image download")
        die(f"failed to download generated image: {exc}")
    return b""


def decode_images(result: dict[str, Any], api_key: str, timeout: int) -> list[bytes]:
    data = result.get("data")
    if not isinstance(data, list) or not data:
        error = result.get("error")
        die(f"API response contained no images: {error or 'unknown response shape'}")

    images: list[bytes] = []
    for index, item in enumerate(data, 1):
        if not isinstance(item, dict):
            die(f"image item {index} has an unexpected response shape")
        encoded = item.get("b64_json")
        image_url = item.get("url")
        if isinstance(encoded, str) and encoded:
            try:
                images.append(base64.b64decode(encoded, validate=True))
            except ValueError:
                die(f"image item {index} contained invalid base64 data")
        elif isinstance(image_url, str) and image_url:
            images.append(download_image(image_url, api_key, timeout))
        else:
            die(f"image item {index} contained neither b64_json nor url")
    return images


def image_kind(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    return None


def output_paths(raw: str, count: int, output_format: str) -> list[Path]:
    path = Path(raw)
    if not path.suffix:
        path = path.with_suffix("." + output_format)
    if count == 1:
        return [path]
    return [path.with_name(f"{path.stem}-{index}{path.suffix}") for index in range(1, count + 1)]


def write_images(images: list[bytes], paths: list[Path], force: bool) -> None:
    for image, path in zip(images, paths):
        if image_kind(image) is None:
            die("API returned data that is not a recognized PNG, JPEG, or WebP image")
        if path.exists() and not force:
            die(f"output already exists: {path} (choose a new name or use --force)")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".part")
        temporary.write_bytes(image)
        os.replace(temporary, path)
        print(f"Wrote {path}")


def command_check(args: argparse.Namespace) -> None:
    path = config_path(args.config)
    _, base_url, source = load_config(path)
    parsed = urlsplit(base_url)
    print(json.dumps({
        "config_source": source,
        "api_key": "set",
        "api_host": parsed.hostname,
        "api_path": parsed.path,
    }, ensure_ascii=False, indent=2))


def command_models(args: argparse.Namespace) -> None:
    api_key, base_url, _ = load_config(config_path(args.config))
    models = fetch_image_models(api_key, base_url, args.timeout)
    print(json.dumps({
        "endpoint": base_url + "/models",
        "models": models,
    }, ensure_ascii=False, indent=2))


def command_generate(args: argparse.Namespace) -> None:
    path = config_path(args.config)
    api_key, base_url, _ = load_config(path)
    if not args.prompt.strip():
        die("prompt must not be empty")
    if not args.model.startswith("gpt-image-") or args.model == "gpt-image-":
        die("model must be a GPT Image model")
    if not 1 <= args.n <= 10:
        die("n must be between 1 and 10")

    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt.strip(),
        "n": args.n,
        "size": args.size,
        "quality": args.quality,
        "output_format": args.output_format,
    }
    paths = output_paths(args.out, args.n, args.output_format)
    public_request = {
        "endpoint": base_url + "/images/generations",
        "outputs": [str(item) for item in paths],
        **payload,
    }
    if args.dry_run:
        print(json.dumps(public_request, ensure_ascii=False, indent=2))
        return

    for output in paths:
        if output.exists() and not args.force:
            die(f"output already exists: {output} (choose a new name or use --force)")

    models = fetch_image_models(api_key, base_url, min(args.timeout, DEFAULT_MODEL_TIMEOUT))
    if args.model not in models:
        die(
            f"selected model {args.model!r} is not in the server's current image model list; "
            "generation stopped. Run `models` and ask the user to select again"
        )

    print("Calling configured Image API. Generation may take several minutes.", file=sys.stderr)
    started = time.monotonic()
    result = request_json(base_url + "/images/generations", api_key, payload, args.timeout)
    images = decode_images(result, api_key, args.timeout)
    if len(images) != len(paths):
        die(f"API returned {len(images)} image(s), expected {len(paths)}")
    write_images(images, paths, args.force)
    print(f"Completed in {time.monotonic() - started:.1f}s.", file=sys.stderr)


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        help="configuration file (default: CUSTOM_IMAGEGEN_CONFIG or ~/.config/custom-imagegen/.env)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images through a configured OpenAI-compatible endpoint"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    configure = commands.add_parser("configure", help="create or import configuration")
    add_config_argument(configure)
    configure.add_argument("--from-env-file", help="import OPENAI_API_KEY and AI_BASE_URL")
    configure.add_argument("--base-url", help="OpenAI-compatible API base URL")
    configure.add_argument(
        "--api-key-env",
        help="read the API key from this environment variable (the value is never printed)",
    )
    configure.set_defaults(func=command_configure)

    check = commands.add_parser("check", help="validate configuration without an API call")
    add_config_argument(check)
    check.set_defaults(func=command_check)

    models = commands.add_parser("models", help="query the server for supported image models")
    add_config_argument(models)
    models.add_argument("--timeout", type=int, default=DEFAULT_MODEL_TIMEOUT)
    models.set_defaults(func=command_models)

    generate = commands.add_parser("generate", help="generate a new image")
    add_config_argument(generate)
    generate.add_argument("--prompt", required=True)
    generate.add_argument("--model", required=True, help="exact model ID explicitly selected by the user")
    generate.add_argument("--size", default=DEFAULT_SIZE)
    generate.add_argument(
        "--quality", choices=("low", "medium", "high", "auto"), default=DEFAULT_QUALITY
    )
    generate.add_argument(
        "--output-format", choices=("png", "jpeg", "webp"), default=DEFAULT_FORMAT
    )
    generate.add_argument("--n", type=int, default=1)
    generate.add_argument("--out", default=DEFAULT_OUTPUT)
    generate.add_argument("--timeout", type=int, default=300)
    generate.add_argument("--force", action="store_true")
    generate.add_argument("--dry-run", action="store_true")
    generate.set_defaults(func=command_generate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "timeout", 1) < 1:
        die("timeout must be at least 1 second")
    try:
        args.func(args)
    except ConfigError as exc:
        die(str(exc), 2)
    except OSError as exc:
        if is_permission_denial(exc):
            permission_required("Local file access")
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
