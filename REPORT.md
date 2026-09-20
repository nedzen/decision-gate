# decision-gate v0.1.0 — release report (2026-09-20)

## Deliverables

- **Repo (public):** https://github.com/nedzen/decision-gate (MIT, 2026 nedzen)
  - `scripts/gate.py` — generalized from the research-gate skill's `jev_gate.py`;
    env config `DECISION_GATE_URL` / `DECISION_GATE_MODEL` / `DECISION_GATE_API_KEY`
    with fallbacks to `OPENROUTER_API_KEY` env and `~/.hermes/.env`.
  - `scripts/flatten_md.py` — as-is from ~/Projects/jev-semgrep + MIT header.
  - `SKILL.md` — Hermes / Claude Code / raw-shell installs; 5 live-run lessons and
    anti-patterns kept verbatim from research-gate.
  - `README.md` — measured before/after table (277 judgments / 97 passed / 35% /
    ~$0.007 / ~85K tokens kept out of context; jev-agent-hacks.md §4), prominent
    CREDITS (uehaj/jev-semgrep + Zenn, TypeSafe docs, classifier.dev), honest
    limitations (unsure band, language mismatch, extraction-quality dependence).
  - `LICENSE`, `CHANGELOG.md`, `.gitignore`.
- **Upstream PRs to uehaj/jev-semgrep:**
  - PR 1 (env overrides + OPENROUTER key fallback + cost line): https://github.com/uehaj/jev-semgrep/pull/4
  - PR 2 (`--hl` sentence highlighting, separate clean diff): https://github.com/uehaj/jev-semgrep/pull/5
  - Fork: https://github.com/nedzen/jev-semgrep. No fork-based divergent copy
    shipped; follow-up note: fork only if no maintainer response in 14 days.

## Test result (real API, OpenRouter decisions, typesafe/jev-1.13)

3-line TSV batch, question: "this text discusses a specific decision-model clone,
its architecture, or benchmark numbers":

```
{"id": "t1", "score": 0.98, "pass": true}    # laya/MLX clone + benchmarks
{"id": "t2", "score": 0.01, "pass": false}   # sourdough recipe
{"id": "t3", "score": 0.94, "pass": true}    # decision-model benchmark numbers
EXIT=0
```

Single-mode stdin check: `{"score": 0.98, "pass": true, "threshold": 0.5}` —
perfect separation, scriptable exit codes work.

## Local (laya/oMLX) endpoint verdict

Verified against `~/Projects/jev-decisions/src/agent.py`: laya is an **in-process
MLX library** (`laya_mlx.Agent.predict(text, schema)`, model dir on
/Volumes/ext), NOT an HTTP decisions endpoint — no `{model, state, questions} →
{answers}` server exists, so it is not drop-in compatible with gate.py's HTTP
client. Documented in README as roadmap (needs a small localhost adapter);
no broken config shipped. Free/private angle noted with measured numbers:
laya p50 0.028 s vs Jev 0.468 s (jev_report.md).

## Notes / caveats

- Delegation was attempted to an existing OMP worker but HQ corrected: worker
  was reaped; work executed in-session instead. No sub-agents used.
- README's gate-report source link is generic (repo-relative); the measured
  numbers come from the local research run (jev-agent-hacks.md §2+§4).
- `usedCost` in PR 4 estimates with SEMGREP_PRICE_PER_M (default 0.042/MTok)
  when the API doesn't report usage.cost.
