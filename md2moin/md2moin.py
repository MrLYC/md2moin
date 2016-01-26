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
        rotate_states.rotate(1)


class Const(object):
    title_repl = [
        (re.compile(r"\n%s\s*([^\n]+?)\n" % i), repl)
        for i, repl in [
            ("#####", "====="),
            ("####", "===="),
            ("###", "==="),
            ("##", "=="),
            ("#", "="),
        ]
    ]
    sub_rex = [
        (re.compile(r"(?<!\*)\*\*(?!\*)"), "'''"),
        (re.compile(r"(?<!\*)\*(?!\*)"), "''"),
        (re.compile(r"(?<!\+)\+\+(?!\+)"), "__"),
        (re.compile(r"(?<!`)`(?!`)"), "'''''"),
        (re.compile(r"(?<=\n)\s*[\-\+](?![\-\+])"), "\n*"),
        (re.compile(r"\n(?=\d)"), "\n\n"),
        (re.compile(r"\n+(\|[\s\:]*(\-)+[\s\:]*\|?)+\n+"), "\n"),
        (re.compile(r"(?<!\|)\|(?!\|)"), "||"),
    ]
    lnk_rex = re.compile(r"\[(.*?)\]\((.+?)\)")
    code_rex = re.compile(r"(```[^\n]*.*?```)", flags=re.M | re.S | re.I)


def convert_link(text):
    parts = []
    link_text = None
    t = 0
    for i in Const.lnk_rex.split(text):
        if t == 0:
            parts.append(i)
        elif t == 1:
            link_text = i
        elif t == 2:
            parts.append("[[%s|%s]]" % (i, link_text))
        t = (t + 1) % 3
    return "".join(parts)


def markdown_to_moin(text):
    text = "\n" + text.replace("\r\n", "\n").replace("\r", "\n")
    title_repl = Const.title_repl
    for rex, repl in title_repl:
        text_blocks = []
        for s, t in zip(
            rotate_state(["text", "title"]),
            rex.split(text)
        ):
            if s == "text":
                text_blocks.append(t)
            else:
                title = "\n%s %s %s\n" % (repl, t, repl)
                text_blocks.append(title)
        text = "".join(text_blocks)

    sub_rex = Const.sub_rex
    text_blocks = []
    for s, b in zip(
        rotate_state(["text", "code"]),
        Const.code_rex.split(text),
    ):
        if s == "text":
            for rex, repl in sub_rex:
                b = rex.sub(repl, b)
            else:
                text_blocks.append(convert_link(b))
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
