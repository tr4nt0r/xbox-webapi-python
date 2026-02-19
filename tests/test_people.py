from httpx import Response
import pytest
from respx import MockRouter

from pythonxbox.api.client import XboxLiveClient
from tests.common import get_response_json


@pytest.mark.asyncio
async def test_people_friends_own(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://peoplehub.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_friends_own"))
    )
    ret = await xbl_client.people.get_friends_own()

    assert len(ret.people) == 2
    assert route.called


@pytest.mark.asyncio
async def test_people_friends_by_xuid(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://peoplehub.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_friends_by_xuid"))
    )
    ret = await xbl_client.people.get_friends_by_xuid("2669321029139235")

    assert len(ret.people) == 2
    assert route.called


@pytest.mark.asyncio
async def test_people_by_xuid_v5(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://peoplehub.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_friends_by_xuid_v5"))
    )
    ret = await xbl_client.people.get_friends_by_xuid("2669321029139235")

    assert len(ret.people) == 1
    assert ret.people[0].gamertag == "VolekTheFNDwarf"
    assert ret.people[0].is_friend is None  # This field is missing in v5
    assert route.called


@pytest.mark.asyncio
async def test_profiles_batch(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.post("https://peoplehub.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_batch"))
    )
    ret = await xbl_client.people.get_friends_own_batch(
        ["271958441785640", "277923030577271", "266932102913935"]
    )

    assert len(ret.people) == 3

    assert route.called


@pytest.mark.asyncio
async def test_people_recommendations(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://peoplehub.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_recommendations"))
    )
    ret = await xbl_client.people.get_friend_recommendations()

    assert ret.recommendation_summary.friend_of_friend == 20
    assert route.called


@pytest.mark.asyncio
async def test_people_summary_own(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://social.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_summary_own"))
    )
    await xbl_client.people.get_friends_summary_own()

    assert route.called


@pytest.mark.asyncio
async def test_people_summary_by_xuid(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://social.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_summary_by_xuid"))
    )
    await xbl_client.people.get_friends_summary_by_xuid("2669321029139235")

    assert route.called


@pytest.mark.asyncio
async def test_people_summary_by_gamertag(
    respx_mock: MockRouter, xbl_client: XboxLiveClient
) -> None:
    route = respx_mock.get("https://social.xboxlive.com").mock(
        return_value=Response(200, json=get_response_json("people_summary_by_gamertag"))
    )
    await xbl_client.people.get_friends_summary_by_gamertag("e")

    assert route.called
