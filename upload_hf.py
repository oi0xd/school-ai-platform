import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from huggingface_hub import HfApi, create_repo
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
REPO_ID = "oi0xd/rag-embed-onnx"
FOLDER_PATH = "onnx_model"

print(f"Connecting to Hugging Face with account oi0xd...")
api = HfApi(token=HF_TOKEN)

print(f"Ensuring repository '{REPO_ID}' exists...")
try:
    create_repo(repo_id=REPO_ID, repo_type="model", token=HF_TOKEN, exist_ok=True)
    print("Repository ready.")
except Exception as e:
    print(f"Repo status: {e}")

print(f"Uploading files from '{FOLDER_PATH}' to '{REPO_ID}'...")
api.upload_folder(
    folder_path=FOLDER_PATH,
    repo_id=REPO_ID,
    repo_type="model",
    token=HF_TOKEN
)
print("All files from onnx_model uploaded successfully to Hugging Face!")
