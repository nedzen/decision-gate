---
name: decision-gate
description: Pre-ingest relevance gate. Score search results/pages with a cheap typed-decision model (Jev) BEFORE reading them into context. Keeps agent context healthy during research.
---

# decision-gate

Don't read into context what a 0.0001¢ classifier can judge first. Every
fetched page, search result, or snippet is ONE noul question to the decision
model. Only PASS results get read.

## Install

```bash
# Hermes
git clone https://github.com/nedzen/decision-gate ~/.hermes/skills/decision-gate

# Claude Code
git clone https://github.com/nedzen/decision-gate ~/.claude/skills/decision-gate

# Raw shell (add scripts/ to PATH or call by path)
git clone https://github.com/nedzen/decision-gate && ./decision-gate/scripts/gate.py --help
```

Auth: `DECISION_GATE_API_KEY` env, else `OPENROUTER_API_KEY` env, else an
`OPENROUTER_API_KEY=` line in `~/.hermes/.env`. Endpoint/model are overridable
(`DECISION_GATE_URL`, `DECISION_GATE_MODEL`).

## The tool

```bash
# single text (stdin or --file); exit 0 = pass, 1 = fail
cat snippet.txt | python3 scripts/gate.py --question "<the question>"

# batch: TSV lines id<TAB>text, one API request for all
python3 scripts/gate.py --question "<the question>" --batch candidates.tsv
```

Output: JSON lines `{"score":0.93,"pass":true}`. Exit code is scriptable.

## Rules

1. **Gate BEFORE reading.** After a search, don't open pages. Write each
   candidate (title + snippet, or fetched text) to a TSV, gate the batch,
   then read only `pass: true` items.
2. **Phrase questions about observable content, not topic labels.** The model
   can't link "Laya" to "Jev" if the text never says Jev. BAD:
   "is this about the Jev ecosystem". GOOD: "this text discusses a specific
   model clone, its architecture, or benchmarks" — describe what the text
   would literally contain.
3. **One question per intent.** If you need two independent filters, run two
   gates (each is one request) and AND them yourself.
4. **Threshold**: default 0.5. Use `--threshold 0.6` when drowning in
   near-misses; 0.35 when starved. The 0.3–0.6 band is "unsure" — when unsure
   band is large, your question is badly phrased; rewrite it, don't lower it.
5. **Compound questions dilute.** "high confidence about revenue" matched
   everything-revenue at 0.3–0.5. Split compounds: gate twice, AND results.
6. **Cost**: ~$0.0007 per 300 lines. Batching is free efficiency — always
   prefer --batch over per-item calls.
7. **Search-tool rotation** (quota dies): on rate/quota errors rotate the
   search backend — tavily → exa → brave (keys in ~/.hermes/.env; set
   `hermes config set web.search_backend <x>` and restore after). Don't
   retry a dead backend more than twice.
8. **Report gating stats** in your final artifact: `gated: N considered,
   M passed (X%)`, plus ~tokens saved (gate only reads ~2000 chars/item vs
   full pages).

## Lessons from live runs (rule refinements — follow these)

- **Gate the atomic unit, not the container.** HN thread pages gated 0.04–0.49
  (nav + comment soup); the same comments gated individually produced sharp
  4/65 precision. Gate comments/items/sections, not page wrappers.
- **Distrust a low score when extraction is suspect.** If a snippet passed
  0.97 but the body fails 0.23, suspect the extraction (subscribe walls, nav),
  not the relevance. Check `len(content)` and header noise before believing a
  low score; strip boilerplate headers before gating page bodies.
- **Editorial/conceptual posts need meaning-questions.** "Contains code,
  benchmarks, cost numbers" scored a core taxonomy essay 0.42. For posts,
  gate with "explains where/why X should be used" style meanings.
- **Language mismatch dilutes scores.** A Japanese article scored 0.45 against
  an English question and was the single most relevant source of the run.
  For non-English sources, phrase the question in the source's language or
  describe content generically (URLs, names, numbers, code identifiers).
- **Snippet-pass/body-fail disagreement = extraction problem first.**

## Anti-patterns

- Never gate AFTER reading "just to check" — that's the cost you were avoiding.
- Never gate with a question containing the name of a thing the text might
  call something else (clones, codenames, translations). Describe features.
- Never paste whole gated-out texts into your context "for later".
