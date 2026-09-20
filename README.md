# decision-gate


<p align="center"><img src="docs/demo.gif" alt="decision-gate demo" width="700"></p>

<p align="center"><img src="docs/demo-agent.gif" alt="agent loop with selective ingestion — 60% of search context gated out before reading" width="700"></p>

*The agent loop: search results are gated before reading — real Jev calls, 60% of context never ingested. See [`examples/`](examples/).*

**Drop-in agent skill: gate search/page ingestion through a cheap typed-decision
model (Jev) BEFORE reading — keep agent context healthy.**

Don't read into context what a 0.0001¢ classifier can judge first. Every
candidate page, search result, or snippet is one typed "noul" (yes/no
probability) question to Jev, batched into a single API call. Only `pass: true`
items get read into the agent's context.

## Measured before/after (live research run, 2026-09-20)

Source: gate report from a real multi-source research session (2026-09-20,
277 gate judgments / 97 passed, ~85K tokens kept out of context, ~$0.007 —
see REPORT.md §verification for the reproduced numbers).

| Metric | Without gate | With gate |
|---|---|---|
| Judgments | read everything | 277 gate judgments, 10 batched API requests |
| Passes | — | 97 passed (35%) → only those fetched/read |
| Spend | ~20 pages of raw HTML in context | **~$0.007** total |
| Tokens kept OUT of context | — | **~85K** (42 gated-out page bodies ≈ 336K chars, plus 61 gated-out HN comments/snippets) |
| Page-level read cut | — | ~70% |

| Engine | p50 latency | Accuracy (24 cases × 3 q) |
|---|---|---|
| Jev (API) | 0.468 s | 0.83–1.0 on 2 of 3 q types |
| Laya (local MLX clone) | **0.028 s** | 0.67–0.96 |

## Install

```bash
# Hermes
git clone https://github.com/nedzen/decision-gate ~/.hermes/skills/decision-gate

# Claude Code
git clone https://github.com/nedzen/decision-gate ~/.claude/skills/decision-gate

# Raw shell
git clone https://github.com/nedzen/decision-gate && ./decision-gate/scripts/gate.py --help
```

## Usage

```bash
# single text (stdin or --file); exit 0 = pass, 1 = fail
cat snippet.txt | python3 scripts/gate.py --question "is this about X?"

# batch: TSV lines id<TAB>text — all candidates, ONE API request
printf 'a1\tTitle: ...\n Snippet about transformers\na2\tTitle: ...\n Recipe blog\n' > cands.tsv
python3 scripts/gate.py --question "this text discusses transformer architecture or benchmarks" --batch cands.tsv --threshold 0.6
```

Output: JSON lines `{"id":"a1","score":0.93,"pass":true}`. Batch mode prints one
line per item; single mode prints one line and sets the exit code.

Also included: `scripts/flatten_md.py` — flattens word-wrapped transcript
markdown into paragraphs (handy for prepping text before gating).

## Configuration (env)

| Variable | Default | Meaning |
|---|---|---|
| `DECISION_GATE_URL` | `https://openrouter.ai/api/alpha/decisions` | decisions endpoint |
| `DECISION_GATE_MODEL` | `typesafe/jev-1.13` | model id |
| `DECISION_GATE_API_KEY` | falls back to `OPENROUTER_API_KEY` env, then an `OPENROUTER_API_KEY=` line in `~/.hermes/.env` | bearer key |

Jev pricing: **$0.042/MTok input, output free**, 70–500 ms latency, 64K request
/ 32K state context (docs.typesafe.ai). At ~2000 chars per candidate, a
300-item batch costs ~$0.0007.

## Local model (free + private)

A local Jev clone on Apple silicon is the free/private option: **Laya**
(`laya-typed-decisions-mlx`, MLX) measured p50 **0.028 s** per decision vs
0.468 s for the hosted API, with usable accuracy (0.67–0.96 across question
types) in our head-to-head bench.

**Status: roadmap, not shipped.** We verified that laya is currently an
in-process MLX Python library (`laya_mlx.Agent.predict(text, schema)`) — it does
not expose the HTTP `{model, state, questions} → {answers}` decisions contract
that `gate.py` speaks. Wiring it up needs a small localhost server adapter;
until that exists, `DECISION_GATE_URL` pointing at localhost is NOT supported.
PRs welcome.

## Limitations (honest)

- **The unsure band (0.3–0.6) is real.** Scores in that band are neither yes nor
  no; usually it means your question is badly phrased, not that the threshold
  is wrong. Rewrite the question instead of lowering the threshold.
- **Language mismatch dilutes scores.** Non-English text scored against an
  English question came back 0.45 and was the most relevant source of our run.
  Phrase the question in the source's language or describe content generically.
- **Extraction quality gates upstream of the gate.** Snippet passed 0.97 but the
  body failed 0.23 → that was a subscribe-wall extraction problem, not
  irrelevance. Check `len(content)` and header noise before trusting a low score.
- **Gate the atomic unit, not the container.** Whole HN thread pages score
  0.04–0.49; the same comments gated individually gave 4/65 sharp precision.
- Jev is a classifier, not a reasoner: decision-seam questions only ("can you
  write every possible answer before seeing the input?").

## CREDITS

This project stands on the shoulders of:

- **[uehaj/jev-semgrep](https://github.com/uehaj/jev-semgrep)** by Junji Uehara
  — grep-by-meaning with Jev, one file, zero dependencies, and the
  [Zenn article](https://zenn.dev/uehaj/articles/jev-semgrep-grep-by-meaning)
  that went viral on X. Our local environment-key overrides
  (`SEMGREP_URL`/`SEMGREP_MODEL`), a cost line, and `--hl` highlighting are
  being contributed **upstream as PRs** to that repo (fork after 14 days of no
  response — follow-up, not blocking this release).
- **TypeSafe** — Jev itself, and the
  [docs](https://docs.typesafe.ai) (typed questions, fan-out patterns,
  skill-suggestion cookbook) that define the decisions contract.
- **[classifier.dev](https://classifier.dev/)** — free zero-shot classification
  API built on Jev; their smart-tier benchmark ("re-ask only the unsure items:
  AG News 87.5% → 90.0%") is the best published calibration of the unsure band.

## License

MIT — see [LICENSE](LICENSE). Copyright 2026 nedzen.
uehaj/jev-semgrep is MIT by Junji Uehara; semgrep.mjs itself is NOT included in
this repo.
