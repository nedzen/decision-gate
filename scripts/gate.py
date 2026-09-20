#!/usr/bin/env python3
"""gate.py — pre-ingest relevance gate. Scores a text against a question with a
typed-decision model (e.g. Jev) BEFORE the text is read into agent context.

Config (env, all optional):
  DECISION_GATE_URL      decisions endpoint (default: OpenRouter alpha decisions)
  DECISION_GATE_MODEL    model id (default: typesafe/jev-1.13)
  DECISION_GATE_API_KEY  bearer key; falls back to OPENROUTER_API_KEY env,
                         then a KEY= line in ~/.hermes/.env
  For a free+private local endpoint (laya/oMLX), set DECISION_GATE_URL to your
  localhost decisions URL and DECISION_GATE_MODEL to the local model id. See
  README.md -> "Local model".

Usage:
  echo "text..." | gate.py --question "is this about X?"
  gate.py --question "..." --file page.txt --threshold 0.6
  gate.py --question "..." --batch items.tsv   # lines: id<TAB>text (scores all, one request)

Output: single JSON line: {"score":0.87,"pass":true,"threshold":0.5}
Exit code: 0 pass / 1 fail (scriptable: `... || skip_reading`)
"""
import argparse, json, os, sys, urllib.request, urllib.error

URL = os.environ.get('DECISION_GATE_URL', 'https://openrouter.ai/api/alpha/decisions')
MODEL = os.environ.get('DECISION_GATE_MODEL', 'typesafe/jev-1.13')

def load_key():
    for var in ('DECISION_GATE_API_KEY', 'OPENROUTER_API_KEY'):
        k = os.environ.get(var)
        if k: return k
    env = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env):
        for line in open(env):
            if line.startswith('OPENROUTER_API_KEY='):
                return line.strip().split('=', 1)[1]
    return None

def score(items, question):
    """items: dict id->text. Returns dict id->p."""
    state = {i: t[:2000] for i, t in items.items()}
    questions = {f'{i}_0': {'type': 'noul', 'instructions': f'Does line {i} match the meaning: "{question}"?'} for i in items}
    body = json.dumps({'model': MODEL, 'state': state, 'questions': questions}).encode()
    key = load_key()
    req = urllib.request.Request(URL, data=body)
    req.add_header('Authorization', 'Bearer ' + (key or ''))
    req.add_header('Content-Type', 'application/json')
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            d = json.load(resp)
            return {i: d['answers'][f'{i}_0'].get('noul', 0) for i in items}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < 2:
                import time; time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f'gate HTTP {e.code}: {e.read()[:300].decode(errors="replace")}')
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < 2:
                import time; time.sleep(2 * (attempt + 1)); continue
            raise RuntimeError(f'gate connection failed after retries (DECISION_GATE_URL={URL}): {e}')
        except (KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f'gate got an unexpected response shape: {e!r}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--question', required=True)
    ap.add_argument('--file')
    ap.add_argument('--threshold', type=float, default=0.5)
    ap.add_argument('--batch')
    a = ap.parse_args()
    if a.batch:
        items = {}
        for line in open(a.batch, encoding='utf8'):
            if '\t' not in line: continue
            i, t = line.rstrip('\n').split('\t', 1)
            items[i] = t
        scores = score(items, a.question)
        for i, p in scores.items():
            print(json.dumps({'id': i, 'score': p, 'pass': p >= a.threshold}))
        return
    text = open(a.file, encoding='utf8').read() if a.file else sys.stdin.read()
    try:
        p = score({'T000': text}, a.question)['T000']
    except RuntimeError as e:
        print(f'decision-gate: {e}', file=sys.stderr)
        sys.exit(2)
    print(json.dumps({'score': p, 'pass': p >= a.threshold, 'threshold': a.threshold}))
    sys.exit(0 if p >= a.threshold else 1)

if __name__ == '__main__':
    main()
