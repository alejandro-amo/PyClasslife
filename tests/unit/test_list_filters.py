import json
import logging
from unittest.mock import Mock

import requests

from pyclasslife import DEFAULT_BASE_URL
from pyclasslife._response_handler import _ResponseHandler
from pyclasslife.resources.students import StudentsResource


def test_students_list_forwards_named_filters() -> None:
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(
        {
            "status": "ok",
            "data": {"total": 0, "page": 1, "limit": 500, "count": 0, "items": []},
        }
    ).encode()
    transport.request.return_value = response
    resource = StudentsResource(
        base_url=DEFAULT_BASE_URL,
        transport=transport,
        response_handler=_ResponseHandler(),
        logger=logging.getLogger("test"),
    )

    resource.list(student_name="Ada", student_email="example.invalid")

    transport.request.assert_called_once_with(
        method="GET",
        url=f"{DEFAULT_BASE_URL}students",
        params={
            "student_name": "Ada",
            "student_email": "example.invalid",
            "page": 1,
            "limit": 500,
        },
    )
