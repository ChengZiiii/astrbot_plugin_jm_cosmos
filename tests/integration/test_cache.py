"""
缓存功能集成测试

测试 JMCache 的端到端缓存流程，包括下载缓存、打包缓存、
失效机制、密码持久化和自动清理功能。
"""

import pytest
from pathlib import Path

pytestmark = [pytest.mark.integration]


@pytest.fixture
def mock_plugin():
    """模拟插件实例（占位，供集成测试签名统一）"""
    return None


class TestCacheIntegration:
    """缓存端到端集成测试"""

    def test_full_download_cache_flow(self, mock_plugin, tmp_path):
        """测试完整的下载 → 缓存 → 复用流程"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)

        # 第一次下载（无缓存）
        assert cache.is_downloaded("123456") is False
        assert cache.is_packed("123456", "zip") is None

        # 模拟：下载完成，保存元数据
        album_dir = tmp_path / "123456" / "1"
        album_dir.mkdir(parents=True)
        (album_dir / "00001.jpg").touch()
        cache.save_metadata("123456", {"title": "Test"})

        # 验证：缓存命中
        assert cache.is_downloaded("123456") is True

        # 模拟：打包完成
        pack_file = tmp_path / "123456" / "123456.zip"
        pack_file.touch()

        # 验证：打包文件已缓存
        result = cache.is_packed("123456", "zip")
        assert result is not None

    def test_package_cache_per_format(self, mock_plugin, tmp_path):
        """测试按格式缓存（zip/pdf/long_img）"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()

        # 创建不同格式的缓存文件
        (album_dir / "123456.zip").touch()
        (album_dir / "123456.pdf").touch()
        (album_dir / "123456_long.png").touch()

        # 所有格式都应该被检测到
        assert cache.is_packed("123456", "zip") is not None
        assert cache.is_packed("123456", "pdf") is not None
        assert cache.is_packed("123456", "long_img") is not None

    def test_redownload_flag_bypasses_cache(self, mock_plugin, tmp_path):
        """测试 --redownload 标志绕过缓存"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()
        (album_dir / "123456.zip").touch()

        # 缓存存在
        assert cache.is_packed("123456", "zip") is not None

        # --redownload 使缓存失效
        cache.invalidate("123456", scope="all")

        # 现在缓存为空
        assert cache.is_packed("123456", "zip") is None
        assert cache.is_downloaded("123456") is False

    def test_encrypted_package_password_persistence(self, mock_plugin, tmp_path):
        """测试加密包密码持久化"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()

        # 保存密码
        cache.save_password("123456", "abcd")

        # 加载密码
        assert cache.get_password("123456") == "abcd"

        # 密码在元数据中持久化
        meta = cache.get_metadata("123456")
        assert meta["password"] == "abcd"

    def test_auto_delete_false_keeps_files(self, mock_plugin, tmp_path):
        """测试 auto_delete_after_send=false 保留文件"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()
        (album_dir / "123456.zip").touch()

        # 文件存在
        assert cache.is_packed("123456", "zip") is not None

        # auto_delete=false 时，文件保留
        # （cache 模块不删除文件 —— main.py 控制此行为）
        assert (album_dir / "123456.zip").exists()

    def test_auto_delete_true_cleans_up(self, mock_plugin, tmp_path):
        """测试 auto_delete_after_send=true 清理文件"""
        from core.cache import JMCache  # Will FAIL - RED phase (core/cache.py doesn't exist)

        cache = JMCache(tmp_path)
        album_dir = tmp_path / "123456"
        album_dir.mkdir()
        (album_dir / "123456.zip").touch()

        # scope=pack 使缓存失效并删除打包文件
        cache.invalidate("123456", scope="pack")
        assert not (album_dir / "123456.zip").exists()
