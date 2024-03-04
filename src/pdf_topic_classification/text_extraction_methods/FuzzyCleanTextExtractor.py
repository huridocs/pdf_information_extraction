from copy import deepcopy

from paragraph_extraction_trainer.PdfSegment import PdfSegment
from pdf_features.PdfToken import PdfToken
from rapidfuzz import fuzz

from pdf_topic_classification.TextExtractionMethod import TextExtractionMethod

ratio_threshold = 75


class FuzzyCleanTextExtractor(TextExtractionMethod):
    def get_pdf_tokens(self) -> list[PdfToken]:
        pdf_tokens = []
        for paragraph in self.pdf_paragraphs:
            pdf_segment = PdfSegment.from_pdf_tokens(paragraph.tokens)
            for option in self.options:
                ratio = fuzz.partial_ratio(option.lower(), pdf_segment.text_content.lower())
                if ratio >= ratio_threshold:
                    pdf_tokens.extend([self.clean_content_pdf_token(x) for x in paragraph.tokens])
                    break

        return pdf_tokens

    @staticmethod
    def clean_content_pdf_token(pdf_token):
        token_copy = deepcopy(pdf_token)
        words = list()
        for word in token_copy.content.split():
            clean_word = "".join([x for x in word if x.isalpha()])
            if clean_word:
                words.append(clean_word)
        token_copy.content = " ".join(words)
        return token_copy
