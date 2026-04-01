import os


class Settings:
    def __init__(self) -> None:
        self.database_url = self._get_required_env("DATABASE_URL")
        self.jwt_secret_key = self._get_required_env("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )

        if self.jwt_secret_key.lower() == "change_this_secret_key":
            raise ValueError("JWT_SECRET_KEY uses an insecure placeholder value")

    @staticmethod
    def _get_required_env(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value


settings = Settings()
