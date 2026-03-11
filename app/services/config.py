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
        self.MAERSK_USER_ID = os.getenv("MAERSK_USER_ID")
        self.MAERSK_PASSWORD = os.getenv("MAERSK_PASSWORD")
        self.TARIFF_CODE = "ZEM"
        self.CONTROL_STATION = "GOP"
        self.PAY_TYPE = "ThirdParty"

        self.ACCESS_TOKEN_URL = "https://api.maersk.com/oauth2/access_token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(
            client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET
        )
        self.RATE_API_URL = "https://wsi.pilotdelivers.com/pilotapi/v1/Ratings"
        self.SHIPMENT_API_URL = (
            # "https://api-stage.maersk.com/mgf/public-gateway/shipments"
            "https://api.maersk.com/mgf/public-gateway/shipments"
        )
        self.SHIPMENT_VOID_API_URL = (
            # f"https://wsi.pilotdelivers.com/pilotapi/test/v1/Shipments/Void"
            "https://wsi.pilotdelivers.com/pilotapi/v1/Shipments/Void"
        )
        self.LABEL_API_URL = (
            # "https://pilotws.pilotdelivers.com/copilotforms_dev/wsforms.asmx"
            "https://pilotws.pilotdelivers.com/copilotforms/wsforms.asmx"
        )
        self.TRACKING_API_URL = (
            # "https://wsi.pilotdelivers.com/test/pilotpartnertracking.asmx"
            "https://wsi.pilotdelivers.com/pilotpartnertracking.asmx"
        )
        self.THIRD_PARTY = {
            "address": {
                "name": "ZEM LOGISTICS INC",
                "address1": "27 ENGELHARD AVE",
                "city": "AVENEL",
                "regionCode": "NJ",
                "postalCode": "07001",
                "countryCode": "US",
            }
        }


app_config = AppConfig()
