import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.common import rating
from app.api.common.carriers import Carrier


class MultiCarrierRatingTests(unittest.IsolatedAsyncioTestCase):
    async def test_legacy_maersk_request_still_defaults_to_maersk(self):
        request = {
            "shipDate": "08/26/2026",
            "origin_zip": "07001",
            "dest_zip": "08817",
            "lineItems": [
                {
                    "description": "Pallet",
                    "pieces": 1,
                    "length": 48,
                    "width": 40,
                    "height": 48,
                    "weight": 500,
                }
            ],
            "liftgate": "false",
        }
        maersk_mock = AsyncMock(return_value={"quotes": [{"TotalQuote": 99.50}]})
        with patch.object(rating, "get_maersk_rating", maersk_mock):
            response = await rating.get_rating(request, db=object())

        self.assertEqual(response["quotes"][0]["TotalQuote"], 99.50)
        maersk_request = maersk_mock.await_args.args[0]
        self.assertEqual(maersk_request.dest_zip, "08817")

    async def test_all_uses_each_carriers_own_payload(self):
        request = {
            "carrier": "all",
            "carrierPayloads": {
                "maersk": {
                    "shipDate": "08/26/2026",
                    "origin_zip": "07001",
                    "dest_zip": "08817",
                    "lineItems": [
                        {
                            "description": "Pallet",
                            "pieces": 1,
                            "length": 48,
                            "width": 40,
                            "height": 48,
                            "weight": 500,
                        }
                    ],
                    "liftgate": "false",
                },
                "kakas": {
                    "quoteType": 1,
                    "pickupDate": "2026-08-26",
                    "iu": 0,
                    "originalMsg": {
                        "type": 1,
                        "city": "Avenel",
                        "state": "NJ",
                        "postCode": "07001",
                        "country": "US",
                    },
                    "destinationMsg": {
                        "type": 1,
                        "city": "Edison",
                        "state": "NJ",
                        "postCode": "08817",
                        "country": "US",
                    },
                    "commodityList": [
                        {
                            "describe": "Pallet",
                            "commodityNum": 1,
                            "commodityUnit": 11,
                            "consignNum": 1,
                            "palletType": 1,
                            "length": 48,
                            "width": 40,
                            "height": 48,
                            "weight": 500,
                            "declaredValue": 1000,
                            "freightClass": "100",
                        }
                    ],
                },
            },
        }

        maersk_mock = AsyncMock(return_value={"quotes": [{"TotalQuote": 101.25}]})
        kakas_mock = AsyncMock(return_value={"code": "200", "data": "quote-uuid"})
        abf_mock = AsyncMock(side_effect=HTTPException(status_code=501, detail="not ready"))

        handlers = {
            Carrier.MAERSK: rating.get_maersk_rating,
            Carrier.KAKAS: kakas_mock,
            Carrier.ABF: abf_mock,
        }
        with patch.object(rating, "get_maersk_rating", maersk_mock), patch.object(
            rating, "RATING_HANDLERS", handlers
        ):
            response = await rating.get_rating(request, db=object())

        self.assertEqual(response["carrier"], Carrier.ALL)
        self.assertEqual(response["results"]["maersk"]["status"], "success")
        self.assertEqual(response["results"]["kakas"]["status"], "success")
        self.assertEqual(response["results"]["abf"]["status"], "not_configured")
        self.assertEqual(response["freightClass"], "100")
        self.assertEqual(response["freightClasses"], ["100"])

        maersk_request = maersk_mock.await_args.args[0]
        self.assertEqual(maersk_request.origin_zip, "07001")
        self.assertFalse(hasattr(maersk_request, "quoteType"))

        kakas_payload = kakas_mock.await_args.args[0]
        self.assertEqual(kakas_payload["carrier"], "kakas")
        self.assertEqual(kakas_payload["pickupDate"], "2026-08-26")
        self.assertNotIn("origin_zip", kakas_payload)


if __name__ == "__main__":
    unittest.main()
