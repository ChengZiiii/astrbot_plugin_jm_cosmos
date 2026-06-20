"""
缓存管理器测试 (TDD RED 阶段)

测试 core/cache.py 中的 JMCache 类和 CacheResult 数据类。
此文件为 TDD RED 阶段 — core/cache.py 尚未实现，所有测试预期失败。
"""

import pytest
from pathlib import Path


class TestJMCacheIsDownloaded:
    """下载缓存检查测试"""

    def test_returns_false_when_dir_missing(self, tmp_path):
        """缓存目录不存在时返回 False"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        assert cache.is_downloaded("123456") is False

    def test_returns_false_when_dir_empty(self, tmp_path):
        """缓存目录存在但为空时返回 False"""
        from core.cache import JMCache

        (tmp_path / "123456").mkdir()
        cache = JMCache(tmp_path)
        assert cache.is_downloaded("123456") is False

    def test_returns_true_when_images_exist(self, tmp_path):
        """存在图片文件时返回 True"""
        from core.cache import JMCache

        album_dir = tmp_path / "123456" / "1"
        album_dir.mkdir(parents=True)
        (album_dir / "00001.jpg").touch()
        cache = JMCache(tmp_path)
        assert cache.is_downloaded("123456") is True

    def test_handles_partial_download(self, tmp_path):
        """部分下载（有部分图片）仍返回 True"""
        from core.cache import JMCache

        (tmp_path / "123456" / "1").mkdir(parents=True)
        (tmp_path / "123456" / "1" / "00001.jpg").touch()
        cache = JMCache(tmp_path)
        assert cache.is_downloaded("123456") is True


class TestJMCacheIsPacked:
    """打包缓存检查测试"""

    def test_returns_none_when_no_file(self, tmp_path):
        """打包文件不存在时返回 None"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        assert cache.is_packed("123456", "zip") is None

    def test_returns_path_for_zip(self, tmp_path):
        """ZIP 文件存在时返回对应路径"""
        from core.cache import JMCache

        zip_file = tmp_path / "123456" / "123456.zip"
        zip_file.parent.mkdir(parents=True)
        zip_file.touch()
        cache = JMCache(tmp_path)
        result = cache.is_packed("123456", "zip")
        assert result is not None
        assert result.name == "123456.zip"

    def test_returns_path_for_pdf(self, tmp_path):
        """PDF 文件存在时返回对应路径"""
        from core.cache import JMCache

        pdf_file = tmp_path / "123456" / "123456.pdf"
        pdf_file.parent.mkdir(parents=True)
        pdf_file.touch()
        cache = JMCache(tmp_path)
        result = cache.is_packed("123456", "pdf")
        assert result is not None
        assert result.name == "123456.pdf"

    def test_returns_path_for_long_img(self, tmp_path):
        """长图文件存在时返回对应路径"""
        from core.cache import JMCache

        img_file = tmp_path / "123456" / "123456_long.png"
        img_file.parent.mkdir(parents=True)
        img_file.touch()
        cache = JMCache(tmp_path)
        result = cache.is_packed("123456", "long_img")
        assert result is not None
        assert result.name == "123456_long.png"


class TestJMCacheMetadata:
    """元数据保存与读取测试"""

    def test_save_metadata_creates_info_json(self, tmp_path):
        """保存元数据后创建 info.json"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        (tmp_path / "123456").mkdir()
        cache.save_metadata("123456", {"title": "Test"})
        assert (tmp_path / "123456" / "info.json").exists()

    def test_get_metadata_returns_saved_data(self, tmp_path):
        """读取元数据返回已保存的内容"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        (tmp_path / "123456").mkdir()
        cache.save_metadata("123456", {"title": "Test"})
        result = cache.get_metadata("123456")
        assert result["title"] == "Test"

    def test_get_metadata_includes_password_when_encrypted(self, tmp_path):
        """加密漫画的元数据包含密码"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        (tmp_path / "123456").mkdir()
        cache.save_metadata("123456", {"title": "Test"})
        cache.save_password("123456", "abcd")
        result = cache.get_metadata("123456")
        assert result["password"] == "abcd"


class TestJMCacheInvalidate:
    """缓存失效测试"""

    def test_removes_package_files(self, tmp_path):
        """失效范围为 pack 时删除打包文件"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()
        (album_dir / "123456.zip").touch()
        cache.invalidate("123456", scope="pack")
        assert not (album_dir / "123456.zip").exists()

    def test_preserves_download_dir(self, tmp_path):
        """失效范围为 pack 时保留下载目录"""
        from core.cache import JMCache

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()
        (album_dir / "123456.zip").touch()
        (album_dir / "1").mkdir()
        (album_dir / "1" / "00001.jpg").touch()
        cache.invalidate("123456", scope="pack")
        assert (album_dir / "1" / "00001.jpg").exists()


class TestCacheResult:
    """CacheResult 数据类测试"""

    def test_combines_save_path_and_pack_path(self):
        """CacheResult 正确组合各字段"""
        from core.cache import CacheResult

        result = CacheResult(
            album_id="123456",
            save_path=Path("/tmp/123456"),
            pack_path=Path("/tmp/123456.zip"),
            metadata={"title": "Test"},
            password=None,
            from_cache=True,
        )
        assert result.album_id == "123456"
        assert result.save_path == Path("/tmp/123456")
        assert result.pack_path == Path("/tmp/123456.zip")
