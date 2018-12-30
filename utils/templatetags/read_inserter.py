from django import template  # pragma: no cover
from lxml import html
from lxml.etree import tostring
from django.urls import reverse

register = template.Library()  # pragma: no cover


def div_builder(progress, chapter_id):
    url = reverse(
        "profiles:reading-progress",
        kwargs={"chapter_id": chapter_id, "progress": progress},
    )
    div = f'<div id="progress-{progress}" ic-get-from="{url}" ic-trigger-on="scrolled-into-view" ic-replace-target="true"></div>'
    return div


@register.filter(name="read_inserter")
def read_inserter(html_string, chapter_id):

    content = ""
    tree = html.fromstring(html_string)
    for anchor in tree.xpath("//a"):
        anchor.drop_tag()
    for script in tree.xpath("//script"):
        script.drop_tag()
    for span in tree.xpath("//*[@lang]"):
        span.drop_tag()
    if tree.text is not None and tree.text.strip() != "":
        content += tree.text
    children = tree.getchildren()
    for index, element in enumerate(children, 1):
        content += tostring(element).decode("unicode-escape")
        if index % 10 == 0:
            content += div_builder(index, chapter_id)
    return content
