import sys
from src.infer import RubberDuckDetector

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python infer.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    model = RubberDuckDetector()
    has_duck, confidence, results = model.predict(image_path)
    if has_duck:
        print(f"Rubber duck detected in {image_path} with confidence {confidence}")
        model.draw_label(image_path, output_path=output_path)
    else:
        print(f"No rubber duck detected in {image_path}")
