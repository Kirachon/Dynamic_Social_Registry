import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware


def _parse_origins(val: str | None) -> List[str]:
    if not val:
        return ["*"]
    parts = [p.strip() for p in val.split(",") if p.strip()]
    return parts or ["*"]


def apply_cors(app):
    origins = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS"))
    allow_all = origins == ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"] if allow_all else ["Authorization", "Content-Type"],
    )

