"""Carrier identifiers accepted by the public gateway."""

from enum import Enum


class Carrier(str, Enum):
    ALL = "all"
    MAERSK = "maersk"
    KAKAS = "kakas"
    ABF = "abf"


DIRECT_CARRIERS = (Carrier.MAERSK, Carrier.KAKAS, Carrier.ABF)

