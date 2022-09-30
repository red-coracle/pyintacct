from pydantic import BaseSettings


class TestSettings(BaseSettings):
    SENDER_ID: str
    SENDER_PASSWORD: str
    COMPANY_ID: str
    USER_ID: str
    USER_PASSWORD: str

config = TestSettings()
