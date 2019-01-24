import re as _re


def set_custom_boundaries(doc):
    for index, token in enumerate(doc[:-1]):
        if token.text == "[":
            doc[token.i].is_sent_start = True
        elif token.text == "]":
            doc[token.i + 1].is_sent_start = True
        elif _re.match(r"\.\.\.[\w]", token.text + doc[:-1][index + 1].text):
            doc[token.i + 1].is_sent_start = False
        elif token.text == "\n":
            doc[token.i].is_sent_start = True
            doc[token.i + 1].is_sent_start = True
        elif _re.match(r"(‘|“).*(’|”)", doc[:-1][index - 1].text + token.text):
            pass
        elif _re.match(r"^(‘|“).*$", token.text):
            doc[token.i].is_sent_start = True
            doc[token.i + 1].is_sent_start = False
        elif _re.match(r".*(’|”)$", token.text):
            doc[token.i].is_sent_start = False
            doc[token.i + 1].is_sent_start = True

    return doc
