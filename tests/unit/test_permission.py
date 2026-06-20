"""
JM-Cosmos II 权限策略单元测试

覆盖 core.permission.evaluate_permission 的分层判定：
1. 管理员（admin_list / 平台 admin）始终放行
2. admin_only 严格模式
3. 非管理员私聊拒绝
4. 非管理员群聊按白名单放行
"""

from __future__ import annotations

from core.permission import (
    ERROR_GROUP_DISABLED,
    ERROR_PERMISSION,
    ERROR_PRIVATE_NON_ADMIN,
    evaluate_permission,
)


# ==================== 管理员覆盖测试 ====================


class TestAdminOverride:
    """管理员（任一来源）必须始终放行，覆盖所有其他规则"""

    def test_admin_list_member_passes_in_private_chat(self):
        """admin_list 成员在私聊放行"""
        result = evaluate_permission(
            is_in_admin_list=True,
            is_platform_admin=False,
            is_private_chat=True,
            admin_only=False,
            is_group_enabled=True,
        )
        assert result is None

    def test_admin_list_member_passes_in_non_whitelisted_group(self):
        """admin_list 成员在非白名单群依旧放行（覆盖群白名单）"""
        result = evaluate_permission(
            is_in_admin_list=True,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=False,
            is_group_enabled=False,
        )
        assert result is None

    def test_platform_admin_passes_in_private_chat(self):
        """平台 admin 在私聊放行"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=True,
            is_private_chat=True,
            admin_only=False,
            is_group_enabled=True,
        )
        assert result is None

    def test_platform_admin_passes_in_non_whitelisted_group(self):
        """平台 admin 在非白名单群依旧放行（覆盖群白名单）"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=True,
            is_private_chat=False,
            admin_only=False,
            is_group_enabled=False,
        )
        assert result is None

    def test_admin_overrides_strict_mode(self):
        """admin_only=True 时管理员依旧放行"""
        result = evaluate_permission(
            is_in_admin_list=True,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=True,
            is_group_enabled=False,
        )
        assert result is None


# ==================== 非管理员 + 私聊测试 ====================


class TestNonAdminPrivateChat:
    """非管理员私聊必须拒绝"""

    def test_non_admin_private_chat_denied_default_mode(self):
        """默认模式下，非管理员私聊被拒（用户报告的核心 bug）"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=True,
            admin_only=False,
            is_group_enabled=True,  # 私聊场景，此参数不影响判定
        )
        assert result == ERROR_PRIVATE_NON_ADMIN

    def test_non_admin_private_chat_denied_even_if_group_whitelist_empty(self):
        """非管理员私聊拒绝，与群白名单是否为空无关"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=True,
            admin_only=False,
            is_group_enabled=False,
        )
        assert result == ERROR_PRIVATE_NON_ADMIN


# ==================== 非管理员 + 群聊测试 ====================


class TestNonAdminGroupChat:
    """非管理员群聊按白名单放行"""

    def test_non_admin_whitelisted_group_passes(self):
        """非管理员在白名单群放行"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=False,
            is_group_enabled=True,
        )
        assert result is None

    def test_non_admin_non_whitelisted_group_denied(self):
        """非管理员在非白名单群被拒"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=False,
            is_group_enabled=False,
        )
        assert result == ERROR_GROUP_DISABLED


# ==================== admin_only 严格模式测试 ====================


class TestStrictMode:
    """admin_only=True 严格模式：拒绝所有非管理员"""

    def test_strict_mode_denies_non_admin_in_whitelisted_group(self):
        """严格模式下，非管理员即使在白名单群也被拒"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=True,
            is_group_enabled=True,
        )
        assert result == ERROR_PERMISSION

    def test_strict_mode_denies_non_admin_private_chat(self):
        """严格模式下，非管理员私聊被拒（错误类型为 permission 而非 private_non_admin）"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=True,
            admin_only=True,
            is_group_enabled=True,
        )
        # 严格模式优先级高于私聊规则
        assert result == ERROR_PERMISSION


# ==================== 全开放场景回归 ====================


class TestOpenDefault:
    """默认开放场景：admin_only=False + 空白名单（is_group_enabled=True）"""

    def test_non_admin_group_chat_open_by_default(self):
        """默认配置下（空白名单视为全开放），非管理员群聊可用"""
        result = evaluate_permission(
            is_in_admin_list=False,
            is_platform_admin=False,
            is_private_chat=False,
            admin_only=False,
            is_group_enabled=True,
        )
        assert result is None
