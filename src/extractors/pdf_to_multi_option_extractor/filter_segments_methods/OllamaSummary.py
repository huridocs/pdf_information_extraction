from copy import deepcopy

import ollama
from ml_cloud_connector.MlCloudConnector import MlCloudConnector
from ollama import Client
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.TokenType import TokenType

from data.PdfDataSegment import PdfDataSegment
from extractors.pdf_to_multi_option_extractor.FilterSegmentsMethod import FilterSegmentsMethod

ip_address = MlCloudConnector().get_ip()


class OllamaSummary(FilterSegmentsMethod):
    valid_types = [TokenType.SECTION_HEADER, TokenType.TITLE, TokenType.TEXT, TokenType.LIST_ITEM]

    def get_first_tokens(self, pdf_data_segments: list[PdfDataSegment], text_length: int) -> list[PdfDataSegment]:
        total_text = ""
        filtered_segments: list[PdfDataSegment] = list()
        for pdf_data_segment in [x for x in pdf_data_segments if x.segment_type in self.valid_types]:
            pdf_data_segment_copy = self.clean_content_pdf_token(pdf_data_segment, text_length - len(total_text))

            if not pdf_data_segment_copy:
                break

            if pdf_data_segment_copy.text_content and "." == pdf_data_segment.text_content[-1]:
                pdf_data_segment_copy.text_content += "."

            total_text += " " + pdf_data_segment_copy.text_content
            filtered_segments.append(pdf_data_segment_copy)

        if not pdf_data_segments or "".join([x.text_content.strip() for x in filtered_segments]) == "":
            return [PdfDataSegment(1, Rectangle(0, 0, 0, 0), "no text")]

        return filtered_segments

    @staticmethod
    def clean_content_pdf_token(pdf_data_segment: PdfDataSegment, character_limit: int):
        if character_limit <= 0:
            return None

        pdf_data_segment.ml_label = 1
        pdf_data_segment_copy = deepcopy(pdf_data_segment)
        words = list()
        text = ""
        for word in pdf_data_segment_copy.text_content.split():
            clean_word = "".join([x for x in word if x.isalpha()])

            if len(text + " " + clean_word) > character_limit:
                break

            if clean_word:
                words.append(clean_word)
                text += " " + word

        pdf_data_segment_copy.text_content = " ".join(words)
        return pdf_data_segment_copy

    def filter_segments(self, pdf_data_segments: list[PdfDataSegment]) -> list[PdfDataSegment]:
        # if exists(Path(ROOT_PATH, "data", "translated_summarized_data", )):
        text = " ".join([x.text_content for x in self.get_first_tokens(pdf_data_segments, 1500)])


        translation = self.translate_text(text)

        response = ollama.chat(
            model="llama3.1:latest",
            messages=[
                {
                    "role": "user",
                    "content": f"Select three sentences that captures the topic of the following document: {translation}",
                }
            ],
            keep_alive=-1
        )
        print("summarization finished")

        return [PdfDataSegment(1, Rectangle(0, 0, 0, 0), response["message"]["content"])]

    @staticmethod
    def translate_text(text: str) -> str:
        client = Client(host=f"http://{ip_address}:11434", timeout=10000)

        content = f"""Please translate the following text into English. Follow these guidelines:
1. Maintain the original layout and formatting.
2. Translate all text accurately without omitting any part of the content.
3. Preserve the tone and style of the original text.
4. Do not include any additional comments, notes, or explanations in the output; provide only the translated text.

Here is the text to be translated:
"""
        content += "\n\n" + text

        response = client.chat(
            model="aya:35b",
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ]
        )
        print("translation finished")
        return response["message"]["content"]


