"""用户可见错误文本中的 URL/IP 脱敏测试。"""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock

import httpx

# 测试环境没有 AstrBot 运行时，导入 client/provider 前先 mock astrbot。
astrbot_api = MagicMock()
astrbot_api.logger = MagicMock()
sys.modules["astrbot"] = MagicMock()
sys.modules["astrbot.api"] = astrbot_api

from image2_core.api.client import GPTImageClient  # noqa: E402
from image2_core.privacy import redact_url_for_user  # noqa: E402
from image2_core.providers.manager import safe_markdown_preview  # noqa: E402


class TestUserVisibleUrlRedaction(unittest.TestCase):
    """用户可见文本不应暴露上游 host/IP/port。"""

    def test_redact_full_url_keeps_scheme_and_path_only(self):
        text = "url=http://192.0.2.10:8080/v1/images/generations；失败"

        result = redact_url_for_user(text)

        self.assertIn("url=http://***/v1/images/generations；失败", result)
        self.assertNotIn("192.0.2.10", result)
        self.assertNotIn("8080", result)

    def test_redact_bare_host_port(self):
        text = "connect tcp self-hosted.example.com:8443 failed"

        result = redact_url_for_user(text)

        self.assertIn("connect tcp *** failed", result)
        self.assertNotIn("self-hosted.example.com", result)
        self.assertNotIn("8443", result)

    def test_safe_markdown_preview_redacts_urls(self):
        text = "网络请求失败 url=https://10.0.0.8:3000/v1；detail=10.0.0.8:3000"

        result = safe_markdown_preview(text)

        self.assertIn("https://***/v1", result)
        self.assertNotIn("10.0.0.8", result)
        self.assertNotIn("3000", result)


class TestClientErrorRedaction(unittest.TestCase):
    """客户端构造的错误消息应在源头脱敏 URL。"""

    def setUp(self):
        self.client = GPTImageClient(
            api_key="test-key",
            base_url="http://192.0.2.10:8080/v1",
            model="gpt-image-2",
            responses_model="gpt-5.5",
        )

    def test_network_error_message_redacts_request_url_and_detail(self):
        error = httpx.ConnectError(
            "connect tcp 192.0.2.10:8080 failed for "
            "http://192.0.2.10:8080/v1/images/generations"
        )

        result = self.client._build_network_error_msg(
            error,
            url="http://192.0.2.10:8080/v1/images/generations",
            elapsed_ms=123,
        )

        self.assertIn("url=http://***/v1/images/generations", result)
        self.assertNotIn("192.0.2.10", result)
        self.assertNotIn("8080", result)

    def test_plain_text_http_error_preview_redacts_url(self):
        result = self.client._build_error_msg(
            502,
            "upstream http://192.0.2.10:8080/v1 failed",
        )

        self.assertIn("http://***/v1", result)
        self.assertNotIn("192.0.2.10", result)
        self.assertNotIn("8080", result)

    def test_sanitized_response_preview_redacts_url(self):
        preview, _ = GPTImageClient._sanitized_response_preview(
            "upstream https://self-hosted.example.com:8443/v1 failed"
        )

        self.assertIn("https://***/v1", preview)
        self.assertNotIn("self-hosted.example.com", preview)
        self.assertNotIn("8443", preview)
