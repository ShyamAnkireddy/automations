import pytest

pytestmark = pytest.mark.api


def test_get_post_by_id_returns_expected_fields(api_client, logger):
    response = api_client.get("/posts/1")
    logger.info("GET /posts/1 returned status=%s", response.status_code)

    assert response.status_code == 200
    payload = response.json()
    assert payload["userId"] == 1
    assert payload["id"] == 1
    assert isinstance(payload["title"], str) and payload["title"]
    assert isinstance(payload["body"], str) and payload["body"]


def test_post_creates_simulated_post(api_client, logger):
    request_body = {
        "title": "pytest demo post",
        "body": "Created by a safe API automation example",
        "userId": 1,
    }
    response = api_client.post("/posts", json=request_body)
    logger.info("POST /posts returned status=%s", response.status_code)

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == request_body["title"]
    assert payload["body"] == request_body["body"]
    assert payload["userId"] == request_body["userId"]
    assert "id" in payload
