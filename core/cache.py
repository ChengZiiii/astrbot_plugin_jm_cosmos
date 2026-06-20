"""
JMComic 缓存管理模块

提供下载缓存和打包文件缓存的统一管理。
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CacheResult:
    """缓存查询结果"""

    album_id: str
    save_path: Path  # 下载目录
    pack_path: Path | None = None  # 缓存打包文件路径（或 None）
    metadata: dict = field(default_factory=dict)  # info.json 内容
    password: str | None = None  # 加密密码（或 None）
    from_cache: bool = True


class JMCache:
    """JMComic 缓存管理器"""

    def __init__(self, download_dir: Path):
        """
        初始化缓存管理器

        Args:
            download_dir: 下载根目录
        """
        self.download_dir = download_dir

    def get_album_dir(self, album_id: str) -> Path:
        """获取漫画本地目录"""
        return self.download_dir / album_id

    def is_downloaded(self, album_id: str) -> bool:
        """
        检查漫画是否已下载到本地

        Args:
            album_id: 本子 ID

        Returns:
            True 如果目录存在且包含至少一个图片文件
        """
        album_dir = self.get_album_dir(album_id)
        if not album_dir.exists() or not album_dir.is_dir():
            return False

        # 遍历目录查找图片文件
        image_suffixes = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
        for path in album_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in image_suffixes:
                return True

        return False

    def is_packed(self, album_id: str, pack_format: str) -> Path | None:
        """
        检查是否已打包指定格式

        Args:
            album_id: 本子 ID
            pack_format: 打包格式 (zip/pdf/long_img/none)

        Returns:
            打包文件路径，如果不存在则返回 None
        """
        if pack_format == "none":
            return None

        album_dir = self.get_album_dir(album_id)
        pack_format = pack_format.lower()

        if pack_format == "zip":
            pack_path = album_dir / f"{album_id}.zip"
        elif pack_format == "pdf":
            pack_path = album_dir / f"{album_id}.pdf"
        elif pack_format == "long_img":
            pack_path = album_dir / f"{album_id}_long.png"
        else:
            return None

        if pack_path.exists():
            return pack_path
        return None

    def save_metadata(self, album_id: str, metadata: dict[str, Any]) -> None:
        """
        保存漫画元数据到 info.json

        Args:
            album_id: 本子 ID
            metadata: 元数据字典
        """
        album_dir = self.get_album_dir(album_id)
        album_dir.mkdir(parents=True, exist_ok=True)
        info_path = album_dir / "info.json"

        # 原子写入：先写临时文件再 rename
        tmp_path = info_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            tmp_path.replace(info_path)
        except Exception:
            # 清理临时文件
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def get_metadata(self, album_id: str) -> dict[str, Any] | None:
        """
        读取漫画元数据

        Args:
            album_id: 本子 ID

        Returns:
            元数据字典，如果不存在或解析失败则返回 None
        """
        album_dir = self.get_album_dir(album_id)
        info_path = album_dir / "info.json"

        if not info_path.exists():
            return None

        try:
            with open(info_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_password(self, album_id: str, password: str) -> None:
        """
        保存加密密码到 metadata

        Args:
            album_id: 本子 ID
            password: 加密密码
        """
        metadata = self.get_metadata(album_id) or {}
        metadata["password"] = password
        self.save_metadata(album_id, metadata)

    def get_password(self, album_id: str) -> str | None:
        """
        获取加密密码

        Args:
            album_id: 本子 ID

        Returns:
            密码字符串，如果不存在则返回 None
        """
        metadata = self.get_metadata(album_id)
        if metadata is None:
            return None
        return metadata.get("password")

    def invalidate(self, album_id: str, scope: str = "all") -> None:
        """
        使缓存失效

        Args:
            album_id: 本子 ID
            scope: 失效范围 ("all"/"download"/"pack")
        """
        album_dir = self.get_album_dir(album_id)
        if not album_dir.exists():
            return

        if scope == "all":
            # 删除整个目录
            shutil.rmtree(album_dir)
        elif scope == "pack":
            # 仅删除打包文件
            pack_suffixes = {".zip", ".pdf", ".png"}
            for path in album_dir.iterdir():
                if path.is_file() and path.suffix.lower() in pack_suffixes:
                    # 排除 info.json
                    if path.name != "info.json":
                        path.unlink()
        elif scope == "download":
            # 删除章节子目录，保留打包文件和 info.json
            for path in album_dir.iterdir():
                if path.is_dir():
                    shutil.rmtree(path)
