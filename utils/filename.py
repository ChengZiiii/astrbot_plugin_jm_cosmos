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


def generate_cached_filename(
    album_id: str,
    pack_format: str = "zip",
) -> str | None:
    """
    Generate fixed filename for cached packages (no timestamp).

    Args:
        album_id: The album ID
        pack_format: Pack format (zip/pdf/long_img/none)

    Returns:
        Fixed filename like "123456.zip" or None for "none" format
    """
    pack_format = pack_format.lower()

    if pack_format == "zip":
        return f"{album_id}.zip"
    elif pack_format == "pdf":
        return f"{album_id}.pdf"
    elif pack_format == "long_img":
        return f"{album_id}_long.png"
    elif pack_format == "none":
        return None
    else:
        # Default to zip for unknown formats
        return f"{album_id}.zip"
