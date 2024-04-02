from pydantic import BaseModel

from data.Option import Option
from data.SegmentBox import SegmentBox


class LabeledData(BaseModel):
    tenant: str = ""
    id: str = ""
    xml_file_name: str = ""
    language_iso: str = ""
    label_text: str = ""
    values: list[Option] = list()
    source_text: str = ""
    page_width: float = 0
    page_height: float = 0
    xml_segments_boxes: list[SegmentBox] = list()
    label_segments_boxes: list[SegmentBox] = list()

    def to_dict(self):
        labeled_data_dict = self.model_dump()
        labeled_data_dict["xml_segments_boxes"] = [x.to_dict() for x in self.xml_segments_boxes]
        labeled_data_dict["label_segments_boxes"] = [x.to_dict() for x in self.label_segments_boxes]
        return labeled_data_dict

    def scale_down_labels(self):
        for label in self.label_segments_boxes:
            label.scale_down()

        return self
