from urllib.parse import urlparse

import requests

from common.api.api_constants import (
    DEFAULT_ALLOWED_HOSTS,
    DEFAULT_API_BASE_URL,
    DEFAULT_API_TIMEOUT_SECONDS,
)


class APIClient:
    """Small safe-by-default JSON API client.

    Only HTTPS endpoints on explicitly allowed hostnames are accepted. The default
    allowlist is JSONPlaceholder. Override API_BASE_URL and API_ALLOWED_HOSTS locally
    when intentionally testing another trusted API.
    """

    def __init__(
        self,
        base_url=DEFAULT_API_BASE_URL,
        allowed_hosts=DEFAULT_ALLOWED_HOSTS,
        timeout=DEFAULT_API_TIMEOUT_SECONDS,
        session=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.allowed_hosts = {host.lower() for host in allowed_hosts}
        self.timeout = timeout
        self.session = session or requests.Session()
        self._validate_url(self.base_url)

    def _validate_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError("API requests must use HTTPS.")
        if not parsed.hostname or parsed.hostname.lower() not in self.allowed_hosts:
            raise ValueError(
                f"Host is not in API_ALLOWED_HOSTS: {parsed.hostname!r}"
            )
        if parsed.username or parsed.password:
            raise ValueError("Credentials must not be embedded in URLs.")
        return url

    def _request(self, method, endpoint, *, params=None, json=None, headers=None):
        # Restrict endpoints to paths beneath the configured base URL.
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = self.base_url + endpoint
        self._validate_url(url)
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            headers=headers,
            timeout=self.timeout,
            allow_redirects=False,
        )
        return response

    def get(self, endpoint, *, params=None, headers=None):
        return self._request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint, *, json=None, headers=None):
        return self._request("POST", endpoint, json=json, headers=headers)

    def put(self, endpoint, *, json=None, headers=None):
        return self._request("PUT", endpoint, json=json, headers=headers)

    def patch(self, endpoint, *, json=None, headers=None):
        return self._request("PATCH", endpoint, json=json, headers=headers)

    def delete(self, endpoint, *, headers=None):
        return self._request("DELETE", endpoint, headers=headers)

    def close(self):
        self.session.close()
