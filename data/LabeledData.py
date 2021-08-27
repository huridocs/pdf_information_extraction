from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class LabeledData(BaseModel):
    tenant: str
    template: str
    property_name: str
    xml_file_name: str
    language_iso: str
    label_text: str
    page_width: float
    page_height: float
    xml_segments_boxes: List[SegmentBox]
    label_segments_boxes: List[SegmentBox]
