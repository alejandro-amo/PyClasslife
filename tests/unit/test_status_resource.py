from unittest.mock import Mock

import requests

from pyclasslife._response_handler import _ResponseHandler
from pyclasslife._response_handler import ClasslifeResponse
from pyclasslife.resources.status import StatusResource
from pyclasslife import DEFAULT_BASE_URL


def test_status_resource_calls_status_endpoint_and_handles_response() -> None:
    transport = Mock()
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"status":"ok","message":"ok","data":{"status":"up"}}'
    transport.request.return_value = response
    resource = StatusResource(
        base_url=DEFAULT_BASE_URL,
        transport=transport,
        response_handler=_ResponseHandler(),
    )

    assert resource.get() == ClasslifeResponse(
        status="ok", message="ok", data={"status": "up"}
    )
    transport.request.assert_called_once_with(
        method="GET", url=f"{DEFAULT_BASE_URL}status"
    )
