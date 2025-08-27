import shutil
import os
import uuid
import atexit
import glob

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.infer import RubberDuckDetector


app = FastAPI()

detector = RubberDuckDetector()
UPLOAD_DIR = "app/uploads"
RESULT_DIR = "app/results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# Cleanup function to remove all uploaded files on app shutdown
def cleanup_all_files():
    for file_path in glob.glob(os.path.join(UPLOAD_DIR, "*")):
        try:
            os.remove(file_path)
        except:
            pass
    for file_path in glob.glob(os.path.join(RESULT_DIR, "*")):
        try:
            os.remove(file_path)
        except:
            pass


# Register cleanup function to run on app shutdown
atexit.register(cleanup_all_files)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def get_status():
    return {"status": "Motion Coach API is up and running!"}


@app.post("/predict")
def predict_duck(file: UploadFile = File(...)):
    # Generate unique filename to avoid conflicts
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    has_duck, confidence, _ = detector.predict(file_path)
    return {
        "duck_detected": has_duck,
        "confidence": confidence,
        "filename": unique_filename,
    }


@app.get("/result/{filename}")
def get_result_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    result_path = os.path.join(RESULT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    detector.draw_label(file_path, result_path)
    return FileResponse(result_path, media_type="image/jpeg")


@app.delete("/cleanup/{filename}")
def cleanup_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    result_path = os.path.join(RESULT_DIR, filename)

    files_removed = 0
    if os.path.exists(file_path):
        os.remove(file_path)
        files_removed += 1
    if os.path.exists(result_path):
        os.remove(result_path)
        files_removed += 1

    return {"message": f"Cleaned up {files_removed} files", "filename": filename}
