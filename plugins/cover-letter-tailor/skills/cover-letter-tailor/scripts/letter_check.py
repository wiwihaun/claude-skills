#!/usr/bin/env python3
"""Mechanical half of Mode 1's self-check: length, language, verbatim JD overlap.

Usage:
    python3 -I letter_check.py <jd.md> <cover_letter.md> [--limit N] [--lang zh|en] [--n 8]

A token is one CJK character or one Latin word/number.
- Chinese length = CJK characters + Latin words (each English word or number counts as one 字).
- English length = Latin words.
- Overlap = every run of N or more consecutive tokens (default 8) that the letter
  shares with the JD, merged into maximal spans. Company name, job title and bare
  tool names may legitimately repeat; anything else flagged should be rewritten.

Exit code 0 when length, language and overlap all pass; 1 otherwise. Reads the
two files only; writes nothing.
"""
import argparse
import re
import sys

CJK_RANGES = "㐀-䶿一-鿿豈-﫿"
CJK = re.compile("[" + CJK_RANGES + "]")
TOKEN = re.compile("[" + CJK_RANGES + "]|[A-Za-z0-9]+(?:['’.\\-][A-Za-z0-9]+)*")


def prose(text):
    """Drop markdown syntax that is not part of the letter's wording."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"[*_`>]", "", text)
    return text


def tokens(text):
    return TOKEN.findall(text)


def join(toks):
    out = ""
    for t in toks:
        if out and not (CJK.fullmatch(t) and CJK.fullmatch(out[-1])):
            out += " "
        out += t
    return out


def overlaps(jd_toks, letter_toks, n):
    jd_low = [t.lower() for t in jd_toks]
    lt_low = [t.lower() for t in letter_toks]
    grams = {tuple(jd_low[i:i + n]) for i in range(len(jd_low) - n + 1)}
    spans = []
    for i in range(len(lt_low) - n + 1):
        if tuple(lt_low[i:i + n]) in grams:
            if spans and i <= spans[-1][1]:
                spans[-1][1] = i + n
            else:
                spans.append([i, i + n])
    return [join(letter_toks[a:b]) for a, b in spans]


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("jd")
    p.add_argument("letter")
    p.add_argument("--limit", type=int, help="length limit (字 for zh, words for en)")
    p.add_argument("--lang", choices=["zh", "en"], help="expected letter language")
    p.add_argument("--n", type=int, default=8, help="minimum shared run length in tokens")
    a = p.parse_args()

    with open(a.jd, encoding="utf-8") as f:
        jd = prose(f.read())
    with open(a.letter, encoding="utf-8") as f:
        letter = prose(f.read())

    lt = tokens(letter)
    cjk = sum(1 for t in lt if CJK.fullmatch(t))
    latin = len(lt) - cjk
    detected = "zh" if cjk > latin else "en"
    lang = a.lang or detected
    length = cjk + latin if lang == "zh" else latin
    unit = "字" if lang == "zh" else "words"

    ok = True
    print("length: %d %s (CJK %d + Latin %d)" % (length, unit, cjk, latin))
    if a.limit is not None:
        if length > a.limit:
            ok = False
            print("  OVER LIMIT by %d (limit %d)" % (length - a.limit, a.limit))
        else:
            print("  within limit %d" % a.limit)

    print("language: detected %s" % detected)
    if a.lang and a.lang != detected:
        ok = False
        print("  MISMATCH: expected %s" % a.lang)

    hits = overlaps(tokens(jd), lt, a.n)
    if hits:
        ok = False
        print("verbatim runs of %d+ tokens shared with the JD: %d" % (a.n, len(hits)))
        for h in hits:
            print("  - " + h)
    else:
        print("verbatim runs of %d+ tokens shared with the JD: none" % a.n)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
