# Repository audit

Run from the vault root:

```powershell
python main/tools/repository-audit/audit.py
python -m unittest discover -s main/tools/repository-audit -v
main/_verify.ps1 -RepositoryAudit
```

Use `--output <absolute-path-outside-vault.json>` for machine-readable evidence.
The audit reads Git candidate files, including untracked nested repositories,
and respects ignore policies. It checks Python AST, JSON and optional PyYAML
syntax, local Markdown references, Obsidian references to config/script files,
duplicate non-empty file hashes, missing tracked paths and private-key headers.
Dependency/build caches are not crawled. Maintained release copies are reported
as duplicates, not automatically deleted. Historical Markdown findings have
their own category; fenced examples are ignored. Link resolution is conservative
and does not check heading anchors, external URLs or Markdown reference-style
links. YAML syntax is not application-schema validation. Secret checks do not
prove an absence of embedded credentials.

Exit 1 means a syntax/readability finding; navigation, duplicate and deleted
working-file candidates require review and do not fail the command. The tool
does not run applications, deploy configuration, modify files or clean caches.
