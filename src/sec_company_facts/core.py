"""
A minimal Python library for fetching yearly 10-K company facts from data.sec.gov in dictionary or Pandas DataFrame format.

Only supports 10-K reports.
"""

import sys
import threading
import time
from typing import Self
import requests
import pandas as pd

_next_allowed_time_lock = threading.Lock()
_next_allowed_time = 0.0
_INTERVAL = 0.1


def _wait_on_rate_limit() -> None:
    """
    If necessary, waits to avoid exceeding global rate limit
    of 1 request every 0.1 seconds.
    """
    global _next_allowed_time

    with _next_allowed_time_lock:
        now = time.monotonic()
        if now < _next_allowed_time:
            time.sleep(_next_allowed_time - now)
        _next_allowed_time = time.monotonic() + _INTERVAL


class Company:
    """
    Company data downloaded from
    data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json

    Use `Company.from_ticker()` or `Company.from_cik()` to
    to create a `Company` from SEC data.
    """

    def __init__(self, data: dict):
        """
        Use `Company.from_ticker()` or `Company.from_cik()` to
        to create a `Company` from SEC data.
        """
        # Dictionary from JSON downloaded from data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
        self.data: dict = data

    @classmethod
    def from_ticker(
        cls, ticker: str, user_agent: str = "Your Name (your@email.com)"
    ) -> Self:
        """
        From data.sec.gov returns a `Company` for this ticker.

        This function is internally rate-limited to 1 request per 0.1 seconds.
        """
        cik = get_cik_from_ticker(ticker, user_agent)
        return cls.from_cik(cik)

    @classmethod
    def from_cik(cls, cik: str, user_agent: str = "Your Name (your@email.com)") -> Self:
        """
        From data.sec.gov returns a `Company` for this CIK.

        This function is internally rate-limited to 1 request per 0.1 seconds.
        """
        headers = {"User-Agent": user_agent}
        cik = cik.zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        _wait_on_rate_limit()
        response = requests.get(url, headers=headers)
        data = response.json()
        return cls(data)

    def get_yearly(self, tag: str | list[str]) -> dict[int, int]:
        """
        Returns a dictionary that maps from year to that year's `tag` value,
        for all available years.

        Data taken from 10-K forms, with US-GAAP and USD units.
        Depending on company, the year may be calendar or financial.

        If `tag` is a list, tries elements in order until an existing tag is found.
        If none of the given tags exist, prints a warning, and returns an empty dict.

        The list of tags you can use is specified by `get_available_tags()`.
        """
        if isinstance(tag, str):
            tag_options = [tag]
        elif isinstance(tag, list):
            tag_options = tag
        else:
            raise TypeError("Expected str or list[str]")

        data = self.data["facts"]["us-gaap"]

        # Find a tag that exists in the data
        good_tag = None
        for tag in tag_options:
            if tag in data:
                good_tag = tag
                break
        if good_tag == None:
            print(
                f"Warning, none of these tags were valid: {tag_options}. Returning an empty dict.",
                file=sys.stderr,
            )
            return {}

        facts = data[good_tag]["units"]["USD"]
        annual_map = {}
        for f in facts:
            # SEC adds a 'frame' field to the final version of each 10-K form.
            # The `frame` field has a format like "FY2022" or "CY2022".
            if f.get("form") == "10-K" and len(f.get("frame", "")) == 6:
                year = int(f["frame"][2:])
                annual_map[year] = f["val"]

        return annual_map

    def get_yearly_dataframe(self, tags: list[str | list[str]]) -> pd.DataFrame:
        """
        Returns a DataFrame with a column for each element in `tags`.
        Each column contains its tag's values for available years.
        Missing entries are filled with 0.0.

        Data taken from 10-K forms, with US-GAAP and USD units.
        Depending on company, the year may be calendar or financial.

        If an element of `tags` is a list, tries elements in order until an existing tag is found.
        The DataFrame column's name will always be the very first element in the list.

        The list of tags you can use is specified by `get_available_tags()`.
        """
        data = {}
        for tag in tags:
            if isinstance(tag, str):
                name = tag
            elif isinstance(tag, list):
                name = tag[0]
            else:
                raise TypeError("Expected tag to be str or list[str]")

            data[name] = self.get_yearly(tag)

        df = pd.DataFrame.from_dict(data, orient="columns").fillna(0.0).sort_index()

        return df

    def get_available_tags(self) -> list[str]:
        """
        Returns a list of tags that are accessible in US-GAAP for
        this company.
        """
        return list(self.data["facts"]["us-gaap"].keys())

    def get_entity_name(self) -> str:
        """
        Returns the name of the company.
        """
        return self.data["entityName"]

    def get_cik(self) -> str:
        """
        Returns the CIK of the company.
        """
        return str(self.data["cik"])

    def get_tag_label(self, tag: str) -> str:
        """
        Returns a human-readable label of the given `tag`.
        """
        return self.data["facts"]["us-gaap"][tag]["label"]

    def get_tag_description(self, tag: str) -> str:
        """
        Returns a human-readable description of the given `tag`.
        """
        return self.data["facts"]["us-gaap"][tag]["description"]


def get_cik_from_ticker(
    ticker: str, user_agent: str = "Your Name (your@email.com)"
) -> str:
    """
    Uses sec.gov to determine the CIK of `ticker`.

    This function is internally rate-limited to 1 request per 0.1 seconds.
    """
    ticker = ticker.upper().strip()
    headers = {"User-Agent": user_agent}
    url = "https://www.sec.gov/files/company_tickers.json"
    _wait_on_rate_limit()
    response = requests.get(url, headers=headers)
    ticker_data = response.json()

    # The JSON is formatted as a dict of dicts:
    # {"0": {"cik_str": 320193, "ticker": "AAPL", ... }, "1": ... }
    for entry in ticker_data.values():
        if entry["ticker"] == ticker:
            return str(entry["cik_str"])

    raise RuntimeError(f"no ticker '{ticker}' found")
