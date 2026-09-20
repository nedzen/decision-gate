#!/usr/bin/env python3
"""agent_loop.py — a minimal, honest demonstration of selective ingestion
with decision-gate: search results are gated BEFORE reading; only passing
pages enter the (simulated) agent context. A running token counter makes
context preservation visible.

Real Jev gate calls; page bodies are cached text (from a real research run).
This is an agent loop, simplified for demonstration.

Usage: agent_loop.py --results results.tsv --pages pages/ --task "..."
  results.tsv lines: id<TAB>title
  pages/<id>.txt contains the page body (what WOULD be ingested)
"""
import argparse, glob, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, '..', 'scripts', 'gate.py')
GREEN, DIM, BLUE, RESET, YELLOW = '\033[1;32m', '\033[2m', '\033[1;34m', '\033[0m', '\033[33m'

def tok(s): return max(1, len(s) // 4)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True)
    ap.add_argument('--pages', required=True)
    ap.add_argument('--task', required=True)
    ap.add_argument('--threshold', type=float, default=0.5)
    a = ap.parse_args()

    results = []
    for line in open(a.results, encoding='utf8'):
        if '\t' in line:
            i, t = line.rstrip('\n').split('\t', 1)
            results.append((i, t))
    pages = {}
    for f in glob.glob(os.path.join(a.pages, '*.txt')):
        i = os.path.splitext(os.path.basename(f))[0]
        pages[i] = open(f, encoding='utf8').read()

    context, saved, n_pass = 0, 0, 0
    print(f'{BLUE}$ agent research --task "{a.task}"{RESET}')
    print(f'[search] {len(results)} results returned')
    print(f'[gate]   {len(results)} candidates → 1 batched Jev call… (not ingesting yet)')

    # gate everything in one call (batch TSV: id + title + snippet preview)
    batch = os.path.join(a.pages, '..', '.gate_batch.tsv')
    with open(batch, 'w', encoding='utf8') as f:
        for i, t in results:
            body = pages.get(i, '')
            f.write(f'{i}\t{t} {body[:600]}\n')
    out = subprocess.run([sys.executable, GATE, '--question',
        'this text describes a concrete technique for using a small classification model inside an AI agent workflow',
        '--batch', os.path.abspath(batch), '--threshold', str(a.threshold)],
        capture_output=True, text=True)
    verdicts = {}
    for line in out.stdout.splitlines():
        try:
            d = json.loads(line); verdicts[d['id']] = d
        except Exception: pass

    print()
    for i, t in results:
        v = verdicts.get(i, {'score': 0, 'pass': False})
        p = pages.get(i, '')
        if v['pass']:
            n_pass += 1
            context += tok(p) + tok(t)
            print(f"{GREEN}PASS  {v['score']:.2f}  {t[:64]}{RESET}")
            print(f'{GREEN}      → ingest page ({tok(p)} tok)      context: {context} tok{RESET}')
        else:
            saved += tok(p) + tok(t)
            print(f"{DIM}SKIP  {v['score']:.2f}  {t[:64]}")
            print(f'      → never read          saved: {saved} tok{RESET}')
    print()
    print(f'{YELLOW}[ingest] {n_pass}/{len(results)} pages read → context: {context} tok{RESET}')
    print(f'{YELLOW}[skipped] {len(results)-n_pass} pages → {saved} tok never entered context{RESET}')
    print(f'{YELLOW}[budget] context {context} tok instead of {context+saved} tok  ({100*saved//(context+saved)}% saved){RESET}')

import json  # noqa: E402  (after prints imported above)
if __name__ == '__main__':
    main()
