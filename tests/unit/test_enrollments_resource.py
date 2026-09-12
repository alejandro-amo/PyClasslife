from unittest.mock import Mock
import logging

import requests

from pyclasslife._response_handler import _ResponseHandler
from pyclasslife import DEFAULT_BASE_URL
from pyclasslife.resources.enrollments import EnrollmentsResource


def test_list_groups_calls_paginated_endpoint() -> None:
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    response._content = (
        b'{"status":"ok","data":{"total":1,"page":1,"limit":500,'
        b'"count":1,"items":[{"enroll_group_id":123}]}}'
    )
    transport.request.return_value = response
    resource = EnrollmentsResource(
        base_url=DEFAULT_BASE_URL,
        transport=transport,
        response_handler=_ResponseHandler(),
        logger=logging.getLogger("test"),
    )

    result = resource.list_groups(page=2, limit=25)

    assert result.total == 1
    assert result.items == [{"enroll_group_id": 123}]
    transport.request.assert_called_once_with(
        method="GET",
        url=f"{DEFAULT_BASE_URL}enroll_groups",
        params={"page": 2, "limit": 25},
    )


def test_list_groups_forwards_named_filters() -> None:
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    response._content = (
        b'{"status":"ok","data":{"total":0,"page":1,"limit":500,'
        b'"count":0,"items":[]}}'
    )
    transport.request.return_value = response
    resource = EnrollmentsResource(
        base_url=DEFAULT_BASE_URL,
        transport=transport,
        response_handler=_ResponseHandler(),
        logger=logging.getLogger("test"),
    )

    resource.list_groups(degree_id=2, section_id=5)

    transport.request.assert_called_once_with(
        method="GET",
        url=f"{DEFAULT_BASE_URL}enroll_groups",
        params={"degree_id": 2, "section_id": 5, "page": 1, "limit": 500},
    )
