#!/usr/bin/env python3
# flatten_md.py — flatten word-wrapped transcript markdown into paragraphs.
# Copyright 2026 nedzen — MIT License (see LICENSE in the repo root).
"""Flatten yt-qmd transcripts_md files: join word-wrapped caption lines into
complete sentences/cues, strip [music] noise and timestamp-link lines.
Output: one paragraph per cue block, blank-line separated. Usage:
  flatten_md.py IN.md [OUT.md]   (or stdin → stdout)"""
import re, sys

def flatten(text):
    out = []
    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            if out and out[-1] != '':
                out.append('')
            continue
        if line.startswith(('#', 'Video:', '[')) or line.startswith('>'):
            # keep headers and timestamp refs on their own line
            out.append(line)
            continue
        out.append(line)
    # join consecutive prose lines into one paragraph
    result, buf = [], []
    for line in out:
        if line == '':
            if buf:
                result.append(' '.join(buf)); buf = []
            result.append('')
        elif line.startswith(('#', 'Video:', '[', '>')):
            if buf:
                result.append(' '.join(buf)); buf = []
            result.append(line)
        else:
            line = re.sub(r'\[(music|applause|laughter|noise)\]', '', line, flags=re.I)
            line = re.sub(r'\s+', ' ', line).strip()
            if line: buf.append(line)
    if buf: result.append(' '.join(buf))
    return '\n'.join(result)

if __name__ == '__main__':
    src = open(sys.argv[1], encoding='utf8').read() if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(flatten(src))
