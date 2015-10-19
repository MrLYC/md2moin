#!/usr/bin/env python
# encoding: utf-8

import re
from collections import deque
import os
from codecs import open


def rotate_state(states):
    rotate_states = deque(states)
    while True:
        yield rotate_states[0]
        rotate_states.rotate()


def markdown_to_moin(text):
    text = "\n" + text.replace("\r\n", "\n").replace("\r", "\n")
    title_repl = [
        ("#####", "====="),
        ("####", "===="),
        ("###", "==="),
        ("##", "=="),
        ("#", "="),
    ]
    for i, repl in title_repl:
        text_blocks = []
        for s, t in zip(
            rotate_state(["text", "title"]),
            re.split(r"\n%s\s*([^\n]+?)\n" % i, text)
        ):
            if s == "text":
                text_blocks.append(t)
            else:
                title = "\n%s %s %s\n" % (repl, t, repl)
                text_blocks.append(title)
        text = "".join(text_blocks)

    sub_rex = [
        (re.compile(r"(?<!\*)\*\*(?!\*)"), "'''"),
        (re.compile(r"(?<!\*)\*(?!\*)"), "''"),
        (re.compile(r"(?<!`)`(?!`)"), "'''''"),
        (re.compile(r"(?<=\n)\s*[\-\+](?![\-\+])"), "*"),
        (re.compile(r"\n+(\|[\s\:]*(\-)+[\s\:]*\|?)+\n+"), "\n"),
        (re.compile(r"(?<!\|)\|(?!\|)"), "||"),
    ]
    text_blocks = []
    for s, b in zip(
        rotate_state(["text", "code"]),
        re.split(r"(```[^\n]*.*?```)", text, flags=re.M | re.S | re.I),
    ):
        if s == "text":
            for rex, repl in sub_rex:
                b = rex.sub(repl, b)
            else:
                text_blocks.append(b)
        elif s == "code":
            text_blocks.append(
                "{{{\n%s\n}}}" % "\n".join(
                    i
                    for i in b.split("\n")[1:-1]
                )
            )
    text = "\n".join(text_blocks)
    return text.replace("\n", os.linesep).strip()


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "rt") as fp:
        print markdown_to_moin(fp.read())
