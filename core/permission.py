"""
JM-Cosmos II 分层权限策略

将"管理员 / 严格模式 / 私聊 / 群白名单"四层判定收敛为纯函数，
便于单测覆盖，并与老插件 astrbot_plugin_jmcomic 的语义对齐：

1. 管理员（插件 admin_list 或平台 admins_id）始终放行，覆盖群白名单
2. admin_only 严格模式：拒绝所有非管理员
3. 非管理员私聊：拒绝（仅管理员可私聊使用）
4. 非管理员群聊：按 enabled_groups 白名单放行；空白名单视为全部放行
"""

from __future__ import annotations

from typing import Optional


# 错误类型常量，对应 utils/formatter.py 中 MessageFormatter.format_error 的键
ERROR_PERMISSION = "permission"
ERROR_PRIVATE_NON_ADMIN = "private_non_admin"
ERROR_GROUP_DISABLED = "group_disabled"


def evaluate_permission(
    *,
    is_in_admin_list: bool,
    is_platform_admin: bool,
    is_private_chat: bool,
    admin_only: bool,
    is_group_enabled: bool,
) -> Optional[str]:
    """分层权限判定。

    Args:
        is_in_admin_list: 调用者是否在插件 admin_list 中
        is_platform_admin: 调用者是否为 AstrBot 平台 admins_id（event.is_admin()）
        is_private_chat: 当前会话是否为私聊（无 group_id）
        admin_only: 插件 admin_only（严格模式）开关
        is_group_enabled: 群是否在 enabled_groups 白名单中；
            私聊场景调用方可直接传 True（不会被命中）

    Returns:
        None  → 放行
        str   → 拒绝，值为错误类型（用于 MessageFormatter.format_error）
    """
    # 1. 管理员始终放行（覆盖群白名单与严格模式之外的所有分支）
    if is_in_admin_list or is_platform_admin:
        return None

    # 2. 严格模式：非管理员一律拒绝
    if admin_only:
        return ERROR_PERMISSION

    # 3. 非管理员私聊：拒绝（仅管理员可私聊使用）
    if is_private_chat:
        return ERROR_PRIVATE_NON_ADMIN

    # 4. 非管理员群聊：按群白名单放行
    if not is_group_enabled:
        return ERROR_GROUP_DISABLED

    return None
