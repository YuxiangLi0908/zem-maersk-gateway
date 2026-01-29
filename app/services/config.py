import os


class AppConfig:
    def __init__(self) -> None:
        # For Rating API, LOCATION_ID and ADDRESS_ID need to be switched
        self.LOCATION_ID = os.getenv("LOCATION_ID")
        self.ADDRESS_ID = os.getenv("ADDRESS_ID")
        self.TARIFF_HEADER_ID = os.getenv("TARIFF_HEADER_ID")
        self.MAERSK_API_KEY = os.getenv("MAERSK_API_KEY")
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")

        self.RATE_API_URL = "https://wsi.pilotdelivers.com/pilotapi/test/v1/Ratings"

app_config = AppConfig()