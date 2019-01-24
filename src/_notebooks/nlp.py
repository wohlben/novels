import os
import django
from lxml import html
import unicodedata
import unidecode
import spacy
import re as witchcraft
from operator import itemgetter
from novels.processing import TextRanker

spacy.prefer_gpu()
nlp = spacy.load('en_core_web_sm')

def set_custom_boundaries(doc):
    for index, token in enumerate(doc[:-1]):
        if token.text == '[':
            doc[token.i].is_sent_start = True
        elif token.text == ']':
            doc[token.i+1].is_sent_start = True
        elif witchcraft.match(r"\.\.\.[\w]", token.text + doc[:-1][index+1].text):
            doc[token.i+1].is_sent_start = False
        elif token.text == '\n':
            doc[token.i].is_sent_start = True
            doc[token.i+1].is_sent_start = True
        elif witchcraft.match(r"(‘|“).*(’|”)", doc[:-1][index-1].text + token.text):
            pass
        elif witchcraft.match(r"^(‘|“).*$", token.text):
            doc[token.i].is_sent_start = True
            doc[token.i+1].is_sent_start = False
        elif witchcraft.match(r".*(’|”)$", token.text):
            doc[token.i].is_sent_start = False
            doc[token.i+1].is_sent_start = True

    return doc

nlp.add_pipe(set_custom_boundaries, before='parser')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from novels.models import Fiction, Chapter

fic = Fiction.objects.get(title="Azarinth Healer")

chap = Chapter.objects.exclude(content=None)[2]
chap = fic.chapter_set.date_sorted("").all()[0]

chap_content = html.fromstring(chap.content).text_content().strip()
chap_text = unidecode.unidecode(chap_content)

chap_text = unicodedata.normalize("NFKD", chap_content)

doc = nlp(chap_text)
ranker = TextRanker()
occurences = ranker._count_occurrences(doc)
occurences

all_acteurs = list(set([ent.text.lower() for ent in doc.ents]))
ranked_acteurs =

ranked_acteurs.sort(key=itemgetter(1))
ranked_acteurs
highlighted_acteurs = list()
for acteur, rank in reversed(ranked_acteurs):
     if rank > ranked_acteurs[-1][1]/2:
         highlighted_acteurs.append(acteur)
     else:
         break

highlighted_acteurs


sents = [i.text for i in doc.sents if i.text != '\n']
sent = nlp(sents[1])
sent
sent.print_tree()

[token for token in sents[186]]

sentences = [i.text for i in doc.sents if i.text != '\n']

[ i for i in doc]
