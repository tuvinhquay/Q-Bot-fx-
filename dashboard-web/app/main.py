import sys
from pathlib import Path

from fastapi import FastAPI

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

app = FastAPI(title="Q-Bot FX API")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "API running"}
