import cv2
import os
from typing import Any, Tuple
from ultralytics import YOLO

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/rubber-duck-model.pt")


class RubberDuckDetector:
    def __init__(self, model_path=MODEL_PATH):
        self.model = YOLO(model_path)

    def predict(self, image_path, conf_threshold=0.85) -> Tuple[bool, float, Any]:
        results = self.model.predict(image_path)
        boxes = results[0].boxes
        has_duck = len(boxes) > 0
        # Get max confidence score if any detection, else 0.0
        confidence = float(
            max([float(box.conf[0]) for box in boxes]) if has_duck else 0.0
        )
        if confidence < conf_threshold:
            has_duck = False
        return has_duck, confidence, results

    def draw_label(self, image_path, output_path=None) -> Any:
        results = self.model(image_path)
        # Draw labels on the image
        # If output_path is provided, save the image, else return the image object
        img_with_labels = results[0].plot()
        if output_path:
            cv2.imwrite(output_path, img_with_labels)
            return output_path
        return img_with_labels
