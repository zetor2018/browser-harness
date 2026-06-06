"""Sources package — registry of all data sources."""
from .nhsa import NhsaSource
from .gov import GovSource

REGISTRY = {
    "nhsa_list": NhsaSource,
    "gov_list": GovSource,
}

__all__ = ["REGISTRY", "NhsaSource", "GovSource"]
