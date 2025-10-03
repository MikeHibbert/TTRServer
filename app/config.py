import os
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./eom.db")
    redis_url: str | None = os.getenv("REDIS_URL")
    elevenlabs_api_key: str | None = os.getenv("ELEVENLABS_API_KEY")
    hf_token: str | None = os.getenv("HF_TOKEN")
    rate_limit_3d_per_min: int = int(os.getenv("RATE_LIMIT_3D_PER_MIN", "1"))

    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL")
    s3_access_key: str | None = os.getenv("S3_ACCESS_KEY")
    s3_secret_key: str | None = os.getenv("S3_SECRET_KEY")
    s3_bucket: str | None = os.getenv("S3_BUCKET")


settings = Settings()