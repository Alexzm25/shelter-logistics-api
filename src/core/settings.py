import os
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    def __init__(self) -> None:
        self.database_url = self._get_required_env("DATABASE_URL")
        self.jwt_secret_key = self._get_required_env("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.groq_api_key = self._get_required_env("GROQ_API_KEY")
        self.groq_model = self._get_required_env("GROQ_MODEL")
        self.groq_base_url = self._get_required_env("GROQ_BASE_URL")
        self.groq_timeout_seconds = float(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))
        self.cloudinary_cloud_name = self._get_required_env("CLOUDINARY_CLOUD_NAME")
        self.cloudinary_api_key = self._get_required_env("CLOUDINARY_API_KEY")
        self.cloudinary_api_secret = self._get_required_env("CLOUDINARY_API_SECRET")
        self.cloudinary_secure = self._get_bool_env("CLOUDINARY_SECURE", True)

        if self.jwt_secret_key.lower() == "change_this_secret_key":
            raise ValueError("JWT_SECRET_KEY uses an insecure placeholder value")

    @staticmethod
    def _get_required_env(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value

    @staticmethod
    def _get_bool_env(name: str, default: bool) -> bool:
        raw_value = os.getenv(name)
        if raw_value is None:
            return default

        normalized = raw_value.strip().lower()
        if normalized in ("1", "true", "t", "yes", "y", "on"):
            return True
        if normalized in ("0", "false", "f", "no", "n", "off"):
            return False
        raise ValueError(f"Invalid boolean value for {name}: {raw_value}")


settings = Settings()
