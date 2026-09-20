# Changelog

## v0.1.0 — 2026-09-20

- `scripts/gate.py`: pre-ingest relevance gate — batch (`--batch` id<TAB>text
  TSV) and single (`--file`/stdin) modes, JSON-lines output, scriptable exit
  code. Env config `DECISION_GATE_URL` / `DECISION_GATE_MODEL` /
  `DECISION_GATE_API_KEY` with `OPENROUTER_API_KEY` + `~/.hermes/.env` fallbacks.
- `scripts/flatten_md.py`: transcript markdown flattener (MIT, ours).
- `SKILL.md`: generalized installs (Hermes, Claude Code, raw shell) + verbatim
  live-run lessons and anti-patterns from the original research-gate skill.
- Known limitation: local laya/oMLX endpoint is roadmap-only (in-process MLX
  library, no HTTP decisions contract yet).
