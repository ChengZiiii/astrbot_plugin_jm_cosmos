"""
文件名生成器模块
"""

import time


def generate_album_filename(
    album_id: str,
    chapter_idx: int | None = None,
) -> str:
    """
    生成下载文件名

    Args:
        album_id: 本子ID
        chapter_idx: 章节序号 (仅章节下载时传入)

    Returns:
        生成的文件名 (不含扩展名)
    """
    timestamp = int(time.time())

    # 基础格式: ID_timestamp 或 ID_chN_timestamp
    if chapter_idx is not None:
        name = f"{album_id}_Ch{chapter_idx}_{timestamp}"
    else:
        name = f"{album_id}_{timestamp}"

    return name
