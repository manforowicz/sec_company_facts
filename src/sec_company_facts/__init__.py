"""
A minimal Python library for fetching yearly 10-K company facts from data.sec.gov in dictionary or Pandas DataFrame format.

Only supports 10-K reports.
"""

from .core import Company, get_cik_from_ticker

__all__ = ["Company", "get_cik_from_ticker"]
