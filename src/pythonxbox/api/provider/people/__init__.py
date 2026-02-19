"""
People - Access friendlist from own profiles and others
"""

from typing import TYPE_CHECKING, ClassVar

from pythonxbox.api.provider.people.models import (
    PeopleDecoration,
    PeopleResponse,
    PeopleSummaryResponse,
)
from pythonxbox.api.provider.ratelimitedprovider import RateLimitedProvider

if TYPE_CHECKING:
    from pythonxbox.api.client import XboxLiveClient


class PeopleProvider(RateLimitedProvider):
    SOCIAL_URL = "https://social.xboxlive.com"
    HEADERS_SOCIAL: ClassVar = {"x-xbl-contract-version": "2"}
    PEOPLE_URL = "https://peoplehub.xboxlive.com"
    # Contract v7 provides full relationship fields (isFriend, canBeFriended, etc), but only works for
    # get_friends_own, not get_friends_by_xuid
    HEADERS_PEOPLE_V7: ClassVar = {
        "x-xbl-contract-version": "7",
        "Accept-Language": "overwrite in __init__",
    }
    # Contract v5 works for all endpoints including get_friends_by_xuid
    HEADERS_PEOPLE_V5: ClassVar = {
        "x-xbl-contract-version": "5",
        "Accept-Language": "overwrite in __init__",
    }
    SEPERATOR = ","

    # NOTE: Rate Limits are noted for social.xboxlive.com ONLY
    RATE_LIMITS: ClassVar = {"burst": 10, "sustain": 30}

    client: "XboxLiveClient"

    def __init__(self, client: "XboxLiveClient") -> None:
        """
        Initialize Baseclass, set 'Accept-Language' header from client instance

        Args:
            client (:class:`XboxLiveClient`): Instance of client
        """
        super().__init__(client)
        # Headers for endpoints that work with v7 (provides more fields)
        self._headers_v7 = {**self.HEADERS_PEOPLE_V7}
        self._headers_v7.update({"Accept-Language": self.client.language.locale})
        # Headers for endpoints that require v5 (get_friends_by_xuid)
        self._headers_v5 = {**self.HEADERS_PEOPLE_V5}
        self._headers_v5.update({"Accept-Language": self.client.language.locale})

    async def get_friends_own(
        self, decoration_fields: list[PeopleDecoration] | None = None, **kwargs
    ) -> PeopleResponse:
        """
        Get friendlist of own profile

        Returns:
            :class:`PeopleResponse`: People Response
        """
        if not decoration_fields:
            decoration_fields = [
                PeopleDecoration.PREFERRED_COLOR,
                PeopleDecoration.DETAIL,
                PeopleDecoration.MULTIPLAYER_SUMMARY,
                PeopleDecoration.PRESENCE_DETAIL,
            ]
        decoration = self.SEPERATOR.join(decoration_fields)

        url = f"{self.PEOPLE_URL}/users/me/people/friends/decoration/{decoration}"
        resp = await self.client.session.get(url, headers=self._headers_v7, **kwargs)
        resp.raise_for_status()
        return PeopleResponse.model_validate_json(resp.text)

    async def get_friends_by_xuid(
        self,
        xuid: str,
        decoration_fields: list[PeopleDecoration] | None = None,
        **kwargs,
    ) -> PeopleResponse:
        """
        Get friendlist of a user by their XUID

        Args:
            xuid: XUID of the user to get friends from

        Returns:
            :class:`PeopleResponse`: People Response
        """
        if not decoration_fields:
            decoration_fields = [
                PeopleDecoration.PREFERRED_COLOR,
                PeopleDecoration.DETAIL,
                PeopleDecoration.MULTIPLAYER_SUMMARY,
                PeopleDecoration.PRESENCE_DETAIL,
            ]
        decoration = self.SEPERATOR.join(decoration_fields)

        url = f"{self.PEOPLE_URL}/users/xuid({xuid})/people/social/decoration/{decoration}"
        # Use v5 headers - contract v7 returns empty people list for other users
        resp = await self.client.session.get(url, headers=self._headers_v5, **kwargs)
        resp.raise_for_status()
        return PeopleResponse.model_validate_json(resp.text)

    async def get_friends_own_batch(
        self,
        xuids: list[str],
        decoration_fields: list[PeopleDecoration] | None = None,
        **kwargs,
    ) -> PeopleResponse:
        """
        Get friends metadata by providing a list of XUIDs

        Args:
            xuids: List of XUIDs

        Returns:
            :class:`PeopleResponse`: People Response
        """
        if not decoration_fields:
            decoration_fields = [
                PeopleDecoration.PREFERRED_COLOR,
                PeopleDecoration.DETAIL,
                PeopleDecoration.MULTIPLAYER_SUMMARY,
                PeopleDecoration.PRESENCE_DETAIL,
            ]
        decoration = self.SEPERATOR.join(decoration_fields)

        url = f"{self.PEOPLE_URL}/users/me/people/batch/decoration/{decoration}"
        resp = await self.client.session.post(
            url, json={"xuids": xuids}, headers=self._headers_v7, **kwargs
        )
        resp.raise_for_status()
        return PeopleResponse.model_validate_json(resp.text)

    async def get_friend_recommendations(
        self, decoration_fields: list[PeopleDecoration] | None = None, **kwargs
    ) -> PeopleResponse:
        """
        Get recommended friends

        Returns:
            :class:`PeopleResponse`: People Response
        """
        if not decoration_fields:
            decoration_fields = [PeopleDecoration.DETAIL]
        decoration = self.SEPERATOR.join(decoration_fields)

        url = (
            f"{self.PEOPLE_URL}/users/me/people/recommendations/decoration/{decoration}"
        )
        resp = await self.client.session.get(url, headers=self._headers_v7, **kwargs)
        resp.raise_for_status()
        return PeopleResponse.model_validate_json(resp.text)

    async def get_friends_summary_own(self, **kwargs) -> PeopleSummaryResponse:
        """
        Get friendlist summary of own profile

        Returns:
            :class:`PeopleSummaryResponse`: People Summary Response
        """
        url = self.SOCIAL_URL + "/users/me/summary"
        resp = await self.client.session.get(
            url, headers=self.HEADERS_SOCIAL, rate_limits=self.rate_limit_read, **kwargs
        )
        resp.raise_for_status()
        return PeopleSummaryResponse.model_validate_json(resp.text)

    async def get_friends_summary_by_xuid(
        self, xuid: str, **kwargs
    ) -> PeopleSummaryResponse:
        """
        Get friendlist summary of user by xuid

        Args:
            xuid: XUID to request summary from

        Returns:
            :class:`PeopleSummaryResponse`: People Summary Response
        """
        url = self.SOCIAL_URL + f"/users/xuid({xuid})/summary"
        resp = await self.client.session.get(
            url, headers=self.HEADERS_SOCIAL, rate_limits=self.rate_limit_read, **kwargs
        )
        resp.raise_for_status()
        return PeopleSummaryResponse.model_validate_json(resp.text)

    async def get_friends_summary_by_gamertag(
        self, gamertag: str, **kwargs
    ) -> PeopleSummaryResponse:
        """
        Get friendlist summary of user by gamertag

        Args:
            gamertag: Gamertag to request friendlist from

        Returns:
            :class:`PeopleSummaryResponse`: People Summary Response
        """
        url = self.SOCIAL_URL + f"/users/gt({gamertag})/summary"
        resp = await self.client.session.get(
            url, headers=self.HEADERS_SOCIAL, rate_limits=self.rate_limit_read, **kwargs
        )
        resp.raise_for_status()
        return PeopleSummaryResponse.model_validate_json(resp.text)
