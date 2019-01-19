import en_core_web_sm as _en_core_web_sm
from operator import itemgetter as _itemgetter
from lxml import html as _html
from novels.models import Chapter as _Chapter, Highlight as _Highlight
import logging as _logging


class TextRanker(object):
    def __init__(self, target_sentences=3, logger="novels.tasks"):
        self.nlp = _en_core_web_sm.load()
        self.target_sentences = target_sentences
        self._logger = _logging.getLogger(logger)

    def extract_highlights(self, chapter_id, delete_existing=True, normalize=False):
        self._logger.info(
            f"extracting highlights for {chapter_id} with normalize {normalize}"
        )
        try:
            chapter = _Chapter.objects.get(id=chapter_id)
            text = _html.fromstring(chapter.content).text_content().strip()
            document = self.nlp(text)
            highlights = self._score_sentences(document, normalize)

            if delete_existing:
                removed_highlights = _Highlight.objects.filter(
                    chapter=chapter
                ).delete()[0]
                if removed_highlights > 0:
                    self._logger.info(f"removed {removed_highlights} old highlights")
            new_highlights = []
            for sentence in highlights:
                new_highlights.append(
                    _Highlight.objects.create(chapter=chapter, sentence=sentence).id
                )
            self._logger.info(
                f"created the highlights {new_highlights} for {chapter.id}"
            )
        except Exception:
            self._logger.exception(f"failed to extract highlights from {chapter_id}")
            raise

    def _score_sentences(self, document, normalize):
        # heavy biased toward long sentences without normalization, kinda terrible with it enabled though...
        occurrences = self._count_occurrences(document)
        highlights = list()
        lowest = -1

        for sentence in document.sents:
            sentence_length = len(sentence)
            word_score = 0
            for word in sentence:
                if self._is_irrelevant(word):
                    continue
                word_score += occurrences.get(word.lemma_.strip(), 0)

            if word_score is 0:
                continue
            if normalize:
                score = word_score / sentence_length
            else:
                score = word_score
            if score > lowest:
                highlights.append((sentence.text.strip(), score))
                highlights.sort(key=_itemgetter(1))
                if len(highlights) > self.target_sentences:
                    del highlights[0]
                    lowest = highlights[0][1]
        return [i[0] for i in highlights]

    def _count_occurrences(self, document):
        occurrences = dict()
        for word in document:
            if self._is_irrelevant(word):
                continue
            occurrences[word.lemma_.strip()] = 1 + occurrences.get(
                word.lemma_.strip(), 0
            )
        return occurrences

    @staticmethod
    def _is_irrelevant(word):
        if (
            word.pos_ is "PUNCT"
            or len(word.text.strip()) < 3
            or len(word.lemma_.strip()) < 3
        ):
            return True
        return False
