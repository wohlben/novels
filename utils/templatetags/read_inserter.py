from django import template  # pragma: no cover
from lxml import html
from lxml.etree import tostring
from django.urls import reverse

register = template.Library()  # pragma: no cover


@register.filter(name="read_inserter")
def read_inserter(html_string, chapter_id):

    content = ""
    tree = html.fromstring(html_string)
    if tree.text is not None and tree.text.strip() != "":
        content += tree.text
    for index, element in enumerate(tree.getchildren()):
        content += tostring(element).decode("unicode-escape")
        url = reverse(
            "profiles:reading-progress",
            kwargs={"chapter_id": chapter_id, "progress": index},
        )
        if index % 10 == 0:
            content += f'<div id="progress-{index}" ic-get-from="{url}" ic-trigger-on="scrolled-into-view" ic-replace-target="true"></div>'
    return content
