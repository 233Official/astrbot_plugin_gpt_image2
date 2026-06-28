"""Provider 手动优先级排序测试。"""

from __future__ import annotations

import json
import sys
import unittest
from unittest.mock import MagicMock

# 测试环境没有 AstrBot 运行时，导入 provider/manager 前先 mock astrbot。
astrbot_api = MagicMock()
astrbot_api.logger = MagicMock()
sys.modules["astrbot"] = MagicMock()
sys.modules["astrbot.api"] = astrbot_api

from image2_core.providers.manager import ProviderManager  # noqa: E402


def _base_config(fallback_api_providers: list[dict]) -> dict:
    return {
        "api_key": "primary-key",
        "base_url": "https://primary.example.com/v1",
        "model": "gpt-image-2",
        "responses_model": "gpt-5.5",
        "adaptive_provider_priority": True,
        "fallback_api_providers": json.dumps(fallback_api_providers),
    }


class TestProviderManualPriority(unittest.TestCase):
    """备用站点 priority 字段排序行为。"""

    def test_priority_group_precedes_adaptive_group(self) -> None:
        manager = ProviderManager(
            _base_config(
                [
                    {
                        "name": "auto-slow",
                        "base_url": "https://auto-slow.example.com/v1",
                    },
                    {
                        "name": "manual-10",
                        "base_url": "https://manual-10.example.com/v1",
                        "priority": 10,
                    },
                    {
                        "name": "manual-0",
                        "base_url": "https://manual-0.example.com/v1",
                        "priority": 0,
                    },
                    {
                        "name": "auto-fast",
                        "base_url": "https://auto-fast.example.com/v1",
                    },
                    {
                        "name": "manual-1",
                        "base_url": "https://manual-1.example.com/v1",
                        "priority": 1,
                    },
                ]
            ),
            "test-plugin",
        )
        manager._provider_stats_cache = {
            "version": 1,
            "providers": {
                "name:auto-fast": {"success_count": 10},
                "name:auto-slow": {"failure_count": 10},
            },
        }

        configs = manager.get_image_api_provider_configs()

        self.assertEqual(
            [config.name for config in configs],
            [
                "primary",
                "manual-0",
                "manual-1",
                "manual-10",
                "auto-fast",
                "auto-slow",
            ],
        )

    def test_same_priority_falls_back_to_configured_order(self) -> None:
        manager = ProviderManager(
            _base_config(
                [
                    {
                        "name": "manual-a",
                        "base_url": "https://manual-a.example.com/v1",
                        "priority": 5,
                    },
                    {
                        "name": "manual-b",
                        "base_url": "https://manual-b.example.com/v1",
                        "priority": 5,
                    },
                ]
            ),
            "test-plugin",
        )
        manager._provider_stats_cache = {"version": 1, "providers": {}}

        configs = manager.get_image_api_provider_configs()

        self.assertEqual(
            [config.name for config in configs],
            ["primary", "manual-a", "manual-b"],
        )

    def test_authoritative_fallback_ignores_priority_and_stays_last(self) -> None:
        manager = ProviderManager(
            _base_config(
                [
                    {
                        "name": "authoritative",
                        "base_url": "https://authoritative.example.com/v1",
                        "role": "authoritative_fallback",
                        "priority": -100,
                    },
                    {
                        "name": "manual",
                        "base_url": "https://manual.example.com/v1",
                        "priority": 1,
                    },
                    {"name": "auto", "base_url": "https://auto.example.com/v1"},
                ]
            ),
            "test-plugin",
        )
        manager._provider_stats_cache = {"version": 1, "providers": {}}

        configs = manager.get_image_api_provider_configs()

        self.assertEqual(
            [config.name for config in configs],
            ["primary", "manual", "auto", "authoritative"],
        )
        self.assertIsNone(configs[-1].priority)

    def test_invalid_priority_is_ignored(self) -> None:
        manager = ProviderManager(
            _base_config(
                [
                    {
                        "name": "invalid",
                        "base_url": "https://invalid.example.com/v1",
                        "priority": "not-an-int",
                    },
                    {
                        "name": "manual",
                        "base_url": "https://manual.example.com/v1",
                        "priority": 1,
                    },
                ]
            ),
            "test-plugin",
        )
        manager._provider_stats_cache = {"version": 1, "providers": {}}

        configs = manager.get_image_api_provider_configs()

        self.assertEqual(
            [config.name for config in configs],
            ["primary", "manual", "invalid"],
        )
        self.assertIsNone(configs[-1].priority)


if __name__ == "__main__":
    unittest.main()
