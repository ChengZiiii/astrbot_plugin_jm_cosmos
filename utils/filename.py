"""
文件名生成器模块（兼容性占位）

原 `generate_album_filename` / `generate_cached_filename` 已统一收敛到
`core.cache.generate_cached_filename`，命名规则只保留一处真相。

本模块保留为空，避免历史导入路径报错；新代码请直接：

    from core.cache import generate_cached_filename
"""
