"""Shared test helpers for API response format."""


def get_json(client, *args, **kwargs):
    response = client.get(*args, **kwargs)
    return response


def assert_api_success(response, status=200):
    assert response.status_code == status, response.get_data(as_text=True)
    body = response.get_json()
    assert body.get("success") is True, body
    assert "message" in body
    assert "data" in body
    return body["data"]


def assert_api_error(response, status):
    assert response.status_code == status, response.get_data(as_text=True)
    body = response.get_json()
    assert body.get("success") is False, body
    assert body.get("message")
