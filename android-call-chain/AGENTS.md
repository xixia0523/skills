# Repository Guidelines

## Project Structure & Module Organization

This directory contains the `android-call-chain` Codex skill, maintained as documentation and metadata.

- `SKILL.md`: invocation rules, required inputs, analysis workflow, and report requirements.
- `README.md`: installation and usage examples.
- `agents/openai.yaml`: display metadata, default prompt, and explicit-invocation policy.
- `references/`: installation, source routing, evidence standards, and source walkthrough guidance.
- `assets/call-chain-report-template.md`: reusable report structure and Mermaid examples.

Generated reports belong in the consuming workspace under `docs/call-chains/`; this directory currently has no application source or automated test suite.

## Build, Test, and Development Commands

No build step, dependency installation, or local server is required for documentation edits.

- `rg --files`: list skill files and locate related guidance.
- `git diff --check`: detect whitespace errors before committing.
- `git diff -- .`: review changes within this skill directory.

For a manual smoke check after installation, explicitly invoke `$android-call-chain` with an exact API and Android version, such as `Context.getSystemService(String)` on Android 16. Follow `references/install.md` when installing or updating; inspect the destination before downloading.

## Coding Style & Naming Conventions

Keep instructional content and report prose in Chinese, matching existing files; preserve source symbols verbatim. Use descriptive Markdown headings, relative links, fenced code blocks with language labels, and concise lists. Keep YAML indentation at two spaces.

Use descriptive lowercase, hyphen-separated names for reference and asset files. Report filenames follow `<api>-<variant>-<baseline>.md`. Keep workflow rules, reference documents, metadata, and template examples consistent. No formatter or linter configuration is currently included.

## Testing Guidelines

Validation is manual; no testing framework or coverage threshold is configured. Check relative links, Markdown tables, Mermaid rendering, and consistency between `SKILL.md` and the report template. For workflow changes, review missing-input handling, baseline selection, evidence gaps, and existing-report protection. Preserve `allow_implicit_invocation: false` and commit-pinned source evidence requirements.

## Commit & Pull Request Guidelines

Recent commits affecting this directory use short Chinese descriptions, such as `call-chain 规则修改` and `完善android-call-chain`. Follow that concise, descriptive style and keep each commit focused.

Pull requests should explain the affected rule or document, the resulting behavior, and validation performed. Link related issues when applicable; include rendered examples or screenshots when changing report layout or diagrams.
