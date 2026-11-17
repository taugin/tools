"""Python 文件系统边界的 Windows 长路径兼容处理。"""

import os


def fsPath(path):
    # 保留文件对象、文件描述符和 None，兼容 open、XML 和 ZIP 的参数类型。
    if not isinstance(path, (str, bytes, os.PathLike)):
        return path
    path = os.fspath(path)
    if os.name != "nt":
        return path
    prefix = b"\\\\?\\" if isinstance(path, bytes) else "\\\\?\\"
    device = b"\\\\.\\" if isinstance(path, bytes) else "\\\\.\\"
    unc = b"\\\\" if isinstance(path, bytes) else "\\\\"
    uncPrefix = b"UNC\\" if isinstance(path, bytes) else "UNC\\"
    if path.startswith((prefix, device)) or not path:
        return path
    path = os.path.abspath(path)
    if path.startswith(unc):
        return prefix + uncPrefix + path[2:]
    return prefix + path


def walk(top, topdown=True, onerror=None, followlinks=False):
    # 对外保留相对/普通路径，避免破坏调用方的 replace、ZIP 条目及命令参数。
    originalTop = os.fspath(top)
    nativeTop = fsPath(originalTop)
    for root, dirs, files in os.walk(nativeTop, topdown, onerror, followlinks):
        relative = os.path.relpath(root, nativeTop)
        current = originalTop if relative == os.curdir or relative == b"." else os.path.join(originalTop, relative)
        yield current, dirs, files
