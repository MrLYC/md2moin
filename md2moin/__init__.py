#!/usr/bin/env python
# encoding: utf-8

from textwrap import dedent
import flask

from md2moin import markdown_to_moin

app = flask.Flask(__name__)
INDEXTPL = dedent(u'''
    <html>
        <head>
            <title>Markdown to moinmoin</title>
        </head>
        <body>
            <form action="/" method="POST">
                <textarea name="text" style="width: 100%; height: 90%">{{ text }}</textarea>
                <input type="submit" value="提交" />
            </form>
        </body>
    </html>
''')


@app.route("/", methods=["GET", "POST"])
def index():
    context = {}
    if flask.request.method == "POST":
        text = flask.request.form.get("text", "")
        context["text"] = markdown_to_moin("\n%s\n" % text)

    return flask.render_template_string(INDEXTPL, **context)


if __name__ == "__main__":
    import sys
    app.run("0.0.0.0", int(sys.argv[1]))
