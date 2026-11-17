import contextlib
import io
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "script" / "common"))
import PathCompat
import Utils


class PathCompatTest(unittest.TestCase):
    def test_non_path_arguments(self):
        stream = io.BytesIO()
        self.assertIs(PathCompat.fsPath(stream), stream)
        self.assertIsNone(PathCompat.fsPath(None))
        self.assertEqual(PathCompat.fsPath(1), 1)
        self.assertEqual(PathCompat.fsPath(""), "")

    def test_posix_path_unchanged(self):
        path = Path("relative")
        with patch.object(PathCompat.os, "name", "posix"):
            self.assertEqual(PathCompat.fsPath(path), "relative")

    @unittest.skipUnless(os.name == "nt", "Windows 路径语义")
    def test_windows_path_forms(self):
        absolute = os.path.abspath("relative/../file")
        self.assertEqual(PathCompat.fsPath("relative/../file"), "\\\\?\\" + absolute)
        self.assertEqual(PathCompat.fsPath(b"file"), b"\\\\?\\" + os.path.abspath(b"file"))
        self.assertEqual(PathCompat.fsPath(r"\\server\share\file"), r"\\?\UNC\server\share\file")
        for name in (r"\\?\C:\file", r"\\?\UNC\server\share\file", r"\\.\NUL"):
            self.assertEqual(PathCompat.fsPath(name), name)


class LongPathIoTest(unittest.TestCase):
    def setUp(self):
        # 所有创建和删除均限定在测试临时目录内。
        self.root = tempfile.mkdtemp(prefix="path-compat-", dir=Path(__file__).resolve().parents[1])
        self.addCleanup(shutil.rmtree, PathCompat.fsPath(self.root))
        self.source = os.path.join(self.root, "源文件 空格", "nested_" * 20, "smali_" * 20)
        os.makedirs(PathCompat.fsPath(self.source))
        self.file = os.path.join(self.source, "示例.smali")
        self.assertGreater(len(self.file), 260)
        with open(PathCompat.fsPath(self.file), "w", encoding="utf-8") as stream:
            stream.write("中文内容")

    def test_read_stat_list_and_delete(self):
        self.assertTrue(os.path.isfile(PathCompat.fsPath(self.file)))
        self.assertIn("示例.smali", os.listdir(PathCompat.fsPath(self.source)))
        self.assertGreater(os.path.getsize(PathCompat.fsPath(self.file)), 0)
        with open(PathCompat.fsPath(self.file), encoding="utf-8") as stream:
            self.assertEqual(stream.read(), "中文内容")
        Utils.deleteFile(self.file)
        self.assertFalse(os.path.exists(PathCompat.fsPath(self.file)))

    def test_copy_move_and_cleanup(self):
        target = os.path.join(self.root, "副本")
        Utils.copydir(os.path.join(self.root, "源文件 空格"), target)
        copied = os.path.join(target, os.path.relpath(self.file, os.path.join(self.root, "源文件 空格")))
        self.assertTrue(os.path.isfile(PathCompat.fsPath(copied)))
        with open(PathCompat.fsPath(copied), "w", encoding="utf-8") as stream:
            stream.write("保留目标")
        Utils.copyfile(self.file, copied, override=False)
        with open(PathCompat.fsPath(copied), encoding="utf-8") as stream:
            self.assertEqual(stream.read(), "保留目标")
        moved = os.path.join(self.source, "moved.smali")
        Utils.movefile(copied, moved)
        self.assertFalse(os.path.exists(PathCompat.fsPath(copied)))
        self.assertTrue(os.path.isfile(PathCompat.fsPath(moved)))
        Utils.deletedir(target)
        Utils.deletedir(target)
        self.assertFalse(os.path.exists(PathCompat.fsPath(target)))

    def test_relative_walk_and_pruning(self):
        relative = os.path.relpath(self.root)
        entries = list(PathCompat.walk(relative))
        self.assertEqual(entries[0][0], relative)
        self.assertTrue(all(not root.startswith("\\\\?\\") for root, _, _ in entries))
        self.assertIn(self.file, [os.path.abspath(path) for path in Utils.list_files(relative)])
        walker = PathCompat.walk(relative)
        _, dirs, _ = next(walker)
        dirs.clear()
        self.assertEqual(list(walker), [])

    def test_xml_and_zip_entries(self):
        xml = os.path.join(self.source, "资源.xml")
        ET.ElementTree(ET.Element("resources")).write(PathCompat.fsPath(xml), encoding="utf-8")
        self.assertEqual(ET.parse(PathCompat.fsPath(xml)).getroot().tag, "resources")
        archive = os.path.join(self.source, "archive.zip")
        with zipfile.ZipFile(PathCompat.fsPath(archive), "w") as output:
            output.write(PathCompat.fsPath(xml), "res/values/资源.xml")
        destination = os.path.join(self.source, "解压")
        with zipfile.ZipFile(PathCompat.fsPath(archive)) as source:
            self.assertEqual(source.namelist(), ["res/values/资源.xml"])
            source.extractall(PathCompat.fsPath(destination))
        self.assertTrue(os.path.isfile(PathCompat.fsPath(os.path.join(destination, "res", "values", "资源.xml"))))

    def test_copy_failure_is_visible(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            Utils.copyfile(os.path.join(self.root, "missing"), self.file)
        self.assertIn("Exception : copyfile", output.getvalue())

    def test_project_zip_function(self):
        script = Path(__file__).resolve().parents[1] / "script" / "android" / "apk2aab.py"
        # 此用例仅验证 Python 打包，不调用 Java 和 Android 工具。
        with contextlib.redirect_stdout(io.StringIO()), patch.dict(sys.modules, {"Common": types.ModuleType("Common")}):
            functions = runpy.run_path(str(script))
            archive = os.path.join(self.root, "output.zip")
            self.assertTrue(functions["zip_base_dir"](self.source, archive))
        with zipfile.ZipFile(archive) as result:
            self.assertEqual(result.namelist(), ["示例.smali"])
            self.assertEqual(result.read("示例.smali").decode("utf-8"), "中文内容")

    def test_project_resource_merge(self):
        script = Path(__file__).resolve().parents[1] / "script" / "merger" / "merge_res.py"
        functions = runpy.run_path(str(script))
        master = os.path.join(self.source, "master")
        slave = os.path.join(self.source, "slave")
        for folder, name in ((master, "first"), (slave, "second")):
            values = os.path.join(folder, "res", "values")
            os.makedirs(PathCompat.fsPath(values))
            with open(PathCompat.fsPath(os.path.join(values, "strings.xml")), "w", encoding="utf-8") as stream:
                stream.write('<resources><string name="%s">中文</string></resources>' % name)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(functions["merge_res"](master, slave))
        merged = ET.parse(PathCompat.fsPath(os.path.join(master, "res", "values", "strings.xml")))
        self.assertEqual({item.attrib["name"] for item in merged.getroot()}, {"first", "second"})

    def test_smali_scan_progress_and_repeat(self):
        script = Path(__file__).resolve().parents[1] / "script" / "android" / "apks2apk.py"
        with patch.dict(sys.modules, {"Common": types.ModuleType("Common")}):
            functions = runpy.run_path(str(script))
        smali_dir = os.path.join(self.source, "smali_classes2")
        os.makedirs(PathCompat.fsPath(smali_dir))
        target = "Lcom/pairip/licensecheck/LicenseClient;->checkLicense(Landroid/content/Context;)V"
        content = "    invoke-static {v0}, " + target + "\r\n"
        matching = os.path.join(smali_dir, "Matching.smali")
        other = os.path.join(smali_dir, "Other.smali")
        with open(PathCompat.fsPath(matching), "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        with open(PathCompat.fsPath(other), "w", encoding="utf-8", newline="") as stream:
            stream.write("    return-void\r\n" * 1000)
        # 使用可控时钟验证长时间扫描也会报告进度。
        namespace = functions["remove_check_licence"].__globals__
        ticks = iter(range(0, 100, 3))
        output = io.StringIO()
        with patch.dict(namespace, {"monotonic": lambda: next(ticks)}), contextlib.redirect_stdout(output):
            functions["remove_check_licence"](self.source)
        self.assertIn("\r[Logging...] 正在扫描文件", output.getvalue())
        self.assertIn("已扫描 2 个 Smali", output.getvalue())
        with open(PathCompat.fsPath(matching), "r", encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "    # " + content[4:])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            functions["remove_check_licence"](self.source)
        self.assertIn("注释调用次数 : 0", output.getvalue())
        with open(PathCompat.fsPath(other), "r", encoding="utf-8", newline="") as stream:
            self.assertEqual(stream.read(), "    return-void\r\n" * 1000)


if __name__ == "__main__":
    unittest.main()
