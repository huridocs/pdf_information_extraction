from unittest import TestCase
from data.ExtractionIdentifier import ExtractionIdentifier
from data.Option import Option
from metadata_extraction.PdfData import PdfData
from multi_option_extraction.data.MultiOptionData import MultiOptionData
from multi_option_extraction.data.MultiOptionSample import MultiOptionSample
from multi_option_extraction.filter_segments_methods.CleanBeginningDigits3000 import CleanBeginningDigits3000
from multi_option_extraction.filter_segments_methods.CleanBeginningDot1000 import CleanBeginningDot1000
from multi_option_extraction.filter_segments_methods.CleanBeginningDot250 import CleanBeginningDot250
from multi_option_extraction.filter_segments_methods.CleanEndDot1000 import CleanEndDot1000
from multi_option_extraction.filter_segments_methods.CleanEndDot250 import CleanEndDot250


class TestFilterSegments(TestCase):
    TENANT = "multi_option_extraction_test"
    extraction_id = "extraction_id"

    def get_data(self):
        extraction_identifier = ExtractionIdentifier(run_name=self.TENANT, extraction_name=self.extraction_id)
        options = [Option(id="1", label="1"), Option(id="2", label="2"), Option(id="3", label="3")]

        pdf_data_1 = PdfData.from_texts(["point 1"])
        pdf_data_2 = PdfData.from_texts(["point 2", "point 2"])
        pdf_data_3 = PdfData.from_texts(["point 3", "point 3", "point 3"])

        samples = [
            MultiOptionSample(pdf_data_1, [options[0]], "en"),
            MultiOptionSample(pdf_data_2, [options[1]], "en"),
            MultiOptionSample(pdf_data_3, [options[2]], "en"),
        ]

        multi_option_data = MultiOptionData(
            multi_value=False, options=options, samples=samples, extraction_identifier=extraction_identifier
        )

        return multi_option_data

    def get_empty_segments(self):
        extraction_identifier = ExtractionIdentifier(run_name=self.TENANT, extraction_name=self.extraction_id)
        options = [Option(id="1", label="1"), Option(id="2", label="2"), Option(id="3", label="3")]

        pdf_data_1 = PdfData.from_texts([""])

        samples = [
            MultiOptionSample(pdf_data_1, [options[0]], "en"),
        ]

        multi_option_data = MultiOptionData(
            multi_value=False, options=options, samples=samples, extraction_identifier=extraction_identifier
        )
        return multi_option_data

    def get_no_segments(self):
        extraction_identifier = ExtractionIdentifier(run_name=self.TENANT, extraction_name=self.extraction_id)
        options = [Option(id="1", label="1"), Option(id="2", label="2"), Option(id="3", label="3")]

        pdf_data_1 = PdfData(pdf_features=None)

        samples = [
            MultiOptionSample(pdf_data_1, [options[0]], "en"),
        ]

        multi_option_data = MultiOptionData(
            multi_value=False, options=options, samples=samples, extraction_identifier=extraction_identifier
        )
        return multi_option_data

    def test_filters(self):
        methods = [CleanBeginningDigits3000(),
                   CleanBeginningDot250(),
                   CleanEndDot250(),
                   CleanBeginningDot1000(),
                   CleanEndDot1000()]

        for method in methods:
            multi_option_data_filtered = method.filter(self.get_data())
            first_pdf_data_segments = multi_option_data_filtered.samples[0].pdf_data.pdf_data_segments
            second_pdf_data_segments = multi_option_data_filtered.samples[1].pdf_data.pdf_data_segments
            third_pdf_data_segments = multi_option_data_filtered.samples[2].pdf_data.pdf_data_segments

            self.assertEqual(3, len(multi_option_data_filtered.samples))
            self.assertEqual(1, len(first_pdf_data_segments))
            self.assertEqual(2, len(second_pdf_data_segments))
            self.assertEqual(3, len(third_pdf_data_segments))
            self.assertTrue(first_pdf_data_segments[0].text_content in ["point 1", "point"])
            self.assertTrue(second_pdf_data_segments[0].text_content in ["point 2", "point"])
            self.assertTrue(third_pdf_data_segments[0].text_content in ["point 3", "point"])

    def test_empty_text(self):
        methods = [CleanBeginningDigits3000(),
                   CleanBeginningDot250(),
                   CleanEndDot250(),
                   CleanBeginningDot1000(),
                   CleanEndDot1000()]

        for method in methods:
            multi_option_data_filtered = method.filter(self.get_empty_segments())
            first_pdf_data_segments = multi_option_data_filtered.samples[0].pdf_data.pdf_data_segments

            self.assertEqual(1, len(multi_option_data_filtered.samples))
            self.assertEqual(1, len(first_pdf_data_segments))
            self.assertEqual("no text", first_pdf_data_segments[0].text_content)

    def test_no_segments(self):
        methods = [CleanBeginningDigits3000(),
                   CleanBeginningDot250(),
                   CleanEndDot250(),
                   CleanBeginningDot1000(),
                   CleanEndDot1000()]

        for method in methods:
            multi_option_data_filtered = method.filter(self.get_no_segments())
            first_pdf_data_segments = multi_option_data_filtered.samples[0].pdf_data.pdf_data_segments

            self.assertEqual(1, len(multi_option_data_filtered.samples))
            self.assertEqual(1, len(first_pdf_data_segments))
            self.assertEqual("no text", first_pdf_data_segments[0].text_content)