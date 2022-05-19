from typing import List

import numpy as np

import lightgbm as lgb
from sklearn.metrics import f1_score

from src.PdfFeatures.PdfFeatures import PdfFeatures
from src.methods.lightgbm_stack_not_complementary_models.SegmentLightgbmStackNotComplementaryModels import (
    SegmentLightgbmStackNotComplementaryModels,
)


TRAINING_CUTS = [16, 27, 71, 78]


class LightgbmStackNotComplementaryModels:
    def __init__(self, property_name: str, method: str):
        self.property_name = property_name
        self.segments: List[SegmentLightgbmStackNotComplementaryModels] = list()
        self.model_path = f"models/{property_name}/{method}/model.model"

        self.model = None
        self.best_cut = 0

    def create_model(self, training_pdfs_features: List[PdfFeatures]):
        self.set_segments(training_pdfs_features)

        if len(self.segments) == 0:
            return False, "No labeled data to create model"

        self.run_light_gbm()

        return self.model

    def set_model(self, x_train, y_train):
        parameters = dict()
        parameters["num_leaves"] = 70
        parameters["feature_fraction"] = 0.9
        parameters["bagging_fraction"] = 0.9
        parameters["bagging_freq"] = 0
        parameters["objective"] = "binary"
        parameters["learning_rate"] = 0.05
        parameters["metric"] = "binary_logloss"
        parameters["verbose"] = -1
        parameters["boosting_type"] = "gbdt"

        train_data = lgb.Dataset(x_train, y_train)
        num_round = 3000
        light_gbm_model = lgb.train(parameters, train_data, num_round)

        return light_gbm_model

    def run_light_gbm(self):
        x_train, y_train = self.get_training_data()

        best_performance = 0

        if x_train.shape[0] < 200:
            self.model = self.set_model(x_train[:, : TRAINING_CUTS[0]], y_train)
            return

        training_rows_number = int(x_train.shape[0] * 0.7)
        for training_cut in TRAINING_CUTS:
            model = self.set_model(x_train[:training_rows_number, :training_cut], y_train[:training_rows_number])
            predictions = model.predict(x_train[training_rows_number:, :training_cut])
            performance = self.get_performance(predictions, y_train[training_rows_number:])
            if best_performance < performance:
                best_performance = performance
                self.best_cut = training_cut

        self.model = self.set_model(x_train[:, : self.best_cut], y_train)

    def get_training_data(self):
        y = np.array([])
        x_rows = []
        for segment in self.segments:
            x_rows.append(segment.get_features_array())
            y = np.append(y, segment.pdf_segment.ml_label)

        X = np.zeros((len(x_rows), len(x_rows[0]) if x_rows else 0))
        for i, v in enumerate(x_rows):
            X[i] = v

        return X, y

    def set_segments(self, pdfs_features: List[PdfFeatures]):
        self.segments = list()
        for pdf_features in pdfs_features:
            self.segments.extend(SegmentLightgbmStackNotComplementaryModels.from_pdf_features(pdf_features))

    def predict(self, model, testing_pdfs_features: List[PdfFeatures]):
        self.set_segments(testing_pdfs_features)
        x, y = self.get_training_data()
        x = x[:, : model.num_feature()]
        predictions = model.predict(x)
        titles = [x.previous_title_segment.text_content if x.previous_title_segment else "" for x in self.segments]
        return predictions, titles

    @staticmethod
    def get_performance(predictions, y_truth):
        return f1_score(y_truth, [prediction > 0.5 for prediction in predictions])
