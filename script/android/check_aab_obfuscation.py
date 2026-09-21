#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 Android App Bundle 中 DEX 标识符的混淆占比。

该脚本不依赖 androguard、Android SDK 或 Java，直接读取 AAB 中的 DEX 表。
结果是基于标识符名称的静态估算值，不等同于 Google Play 内部指标。
"""

import argparse
import hashlib
import html
import json
import re
import struct
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


OBFUSCATED_NAME = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
JAVA_KEYWORDS = {
    "a", "i", "j", "k", "v", "x", "y", "z", "id", "in", "is", "to",
    "get", "set", "run", "main", "ok", "on", "of", "do", "io",
}
R8_JSON_PATH = "BUNDLE-METADATA/com.android.tools/r8.json"
MAPPING_PATH = "BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map"
CHINA_TIMEZONE = timezone(timedelta(hours=8))


def read_u8(data, offset):
    return data[offset], offset + 1


def read_uleb128(data, offset):
    value = 0
    shift = 0
    while True:
        byte, offset = read_u8(data, offset)
        value |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            return value, offset
        shift += 7
        if shift > 35:
            raise ValueError("DEX 中发现无效的 ULEB128")


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def is_obfuscated_name(name):
    """识别典型 R8/ProGuard 名称，降低常见短业务名的误报。"""
    if not name or not OBFUSCATED_NAME.match(name):
        return False
    if len(name) <= 2:
        return name not in JAVA_KEYWORDS
    if len(name) <= 4 and name.islower() and not any(c in name for c in "aeiou"):
        return True
    # a、b、aa、ab 这类名称是 R8/ProGuard 最常见的输出。
    return len(name) <= 3 and name.islower() and name.isalpha()


def descriptor_to_class_name(descriptor):
    if descriptor.startswith("L") and descriptor.endswith(";"):
        return descriptor[1:-1].replace("/", ".")
    return descriptor


def parse_dex(data, dex_name):
    if len(data) < 0x70 or data[:4] != b"dex\n":
        raise ValueError("不是有效的 DEX 文件")

    string_count, string_offset = u32(data, 0x38), u32(data, 0x3C)
    type_count, type_offset = u32(data, 0x40), u32(data, 0x44)
    field_count, field_offset = u32(data, 0x50), u32(data, 0x54)
    method_count, method_offset = u32(data, 0x58), u32(data, 0x5C)
    class_count, class_offset = u32(data, 0x60), u32(data, 0x64)

    strings = []
    for index in range(string_count):
        offset = u32(data, string_offset + index * 4)
        _, offset = read_uleb128(data, offset)
        end = data.find(b"\0", offset)
        if end < 0:
            raise ValueError("DEX 字符串表损坏")
        strings.append(data[offset:end].decode("utf-8", errors="replace"))

    type_strings = [strings[u32(data, type_offset + i * 4)] for i in range(type_count)]
    fields = []
    for i in range(field_count):
        offset = field_offset + i * 8
        fields.append((u16(data, offset), u32(data, offset + 4)))
    methods = []
    for i in range(method_count):
        offset = method_offset + i * 8
        methods.append((u16(data, offset), u16(data, offset + 2), u32(data, offset + 4)))

    classes = []
    class_indexes = set()
    for i in range(class_count):
        offset = class_offset + i * 32
        class_idx, class_data_offset = u32(data, offset), u32(data, offset + 24)
        class_indexes.add(class_idx)
        classes.append(type_strings[class_idx])

    symbols = {"class": [], "method": [], "field": []}
    for class_descriptor in classes:
        class_name = descriptor_to_class_name(class_descriptor).split(".")[-1]
        symbols["class"].append({"name": class_name, "descriptor": class_descriptor})

    # method_ids/field_ids 中的名称比 class_data 更完整，包含没有 code 的引用。
    for class_idx, _, name_idx in methods:
        symbols["method"].append({
            "name": strings[name_idx],
            "owner": descriptor_to_class_name(type_strings[class_idx]),
        })
    for class_idx, name_idx in fields:
        symbols["field"].append({
            "name": strings[name_idx],
            "owner": descriptor_to_class_name(type_strings[class_idx]),
        })

    return {
        "name": dex_name,
        "classes": len(symbols["class"]),
        "methods": len(symbols["method"]),
        "fields": len(symbols["field"]),
        "symbols": symbols,
    }


def calculate_stats(dex_reports, excluded_prefixes):
    totals = Counter()
    obfuscated = Counter()
    examples = {"class": [], "method": [], "field": []}
    for dex in dex_reports:
        for category, items in dex["symbols"].items():
            for item in items:
                owner = item.get("owner", item.get("descriptor", ""))
                if any(owner.startswith(prefix) for prefix in excluded_prefixes):
                    continue
                totals[category] += 1
                if is_obfuscated_name(item["name"]):
                    obfuscated[category] += 1
                    if len(examples[category]) < 20:
                        examples[category].append(item["name"])

    total = sum(totals.values())
    obfuscated_total = sum(obfuscated.values())
    categories = {}
    for category in ("class", "method", "field"):
        count = totals[category]
        hit = obfuscated[category]
        categories[category] = {
            "total": count,
            "obfuscated": hit,
            "percentage": round(hit * 100.0 / count, 2) if count else 0.0,
        }
    return {
        "total_symbols": total,
        "obfuscated_symbols": obfuscated_total,
        "obfuscation_percentage": round(obfuscated_total * 100.0 / total, 2) if total else 0.0,
        "categories": categories,
        "examples": examples,
    }


def find_nested_value(value, key):
    """从 R8 元数据中读取字段，兼容不同 R8 版本的 JSON 结构。"""
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            result = find_nested_value(child, key)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = find_nested_value(child, key)
            if result is not None:
                return result
    return None


def read_r8_metadata(bundle):
    """读取 Google Play 使用的 R8 构建元数据。"""
    try:
        raw = bundle.read(R8_JSON_PATH)
    except KeyError:
        return None
    metadata = json.loads(raw.decode("utf-8-sig"))
    no_obfuscation = find_nested_value(metadata, "noObfuscationPercentage")
    if no_obfuscation is None:
        return None
    raw_no_obfuscation = no_obfuscation
    if isinstance(no_obfuscation, str):
        no_obfuscation = no_obfuscation.strip().rstrip("%")
    try:
        no_obfuscation = float(no_obfuscation)
    except (TypeError, ValueError):
        return {
            "source": R8_JSON_PATH,
            "source_type": "google_play_r8_metadata_invalid",
            "valid": False,
            "error": "noObfuscationPercentage 不是数字：{}".format(raw_no_obfuscation),
            "raw_no_obfuscation_percentage": raw_no_obfuscation,
        }
    if no_obfuscation < 0:
        return {
            "source": R8_JSON_PATH,
            "source_type": "google_play_r8_metadata_invalid",
            "valid": False,
            "error": "noObfuscationPercentage 不能为负数：{}".format(raw_no_obfuscation),
            "raw_no_obfuscation_percentage": raw_no_obfuscation,
        }
    # 不同 R8 版本可能输出比例、百分数或百分数的整数放大值。
    if 0 <= no_obfuscation <= 1:
        no_obfuscation *= 100
    elif 100 < no_obfuscation <= 10000:
        no_obfuscation /= 100
    if not 0 <= no_obfuscation <= 100:
        return {
            "source": R8_JSON_PATH,
            "source_type": "google_play_r8_metadata_invalid",
            "valid": False,
            "error": "noObfuscationPercentage 超出范围：{}".format(raw_no_obfuscation),
            "raw_no_obfuscation_percentage": raw_no_obfuscation,
        }
    metadata_dex_checksums = {
        item.get("checksum")
        for item in metadata.get("dexFiles", [])
        if isinstance(item, dict) and item.get("checksum")
    }
    bundle_dex_checksums = {
        hashlib.sha256(bundle.read(name)).hexdigest()
        for name in bundle.namelist()
        if re.match(r"(?:[^/]+/)*classes(?:\d+)?\.dex$", name)
    }
    checksum_match = (
        bool(metadata_dex_checksums)
        and metadata_dex_checksums == bundle_dex_checksums
    )
    return {
        "source": R8_JSON_PATH,
        "source_type": "google_play_r8_metadata",
        "valid": checksum_match,
        "error": None if checksum_match else (
            "r8.json 中的 DEX SHA-256 与 AAB 实际 DEX 不匹配，"
            "Google Play 可能会忽略该元数据并使用回退检测"
        ),
        "obfuscation_percentage": round(100.0 - no_obfuscation, 2),
        "no_obfuscation_percentage": round(no_obfuscation, 2),
        "raw_no_obfuscation_percentage": raw_no_obfuscation,
        "normalization": "negative value converted to absolute value"
        if isinstance(raw_no_obfuscation, (int, float)) and raw_no_obfuscation < 0
        else None,
        "r8_dex_checksum_match": checksum_match,
        "r8_dex_count": len(metadata_dex_checksums),
        "bundle_dex_count": len(bundle_dex_checksums),
        "metadata": metadata,
    }


def read_mapping_stats(bundle, dex_reports):
    """按 Google/Android AAB 分析器的类级口径统计 mapping。"""
    try:
        text = bundle.read(MAPPING_PATH).decode("utf-8", errors="replace")
    except KeyError:
        return None
    class_mapping = {}
    member_total = member_obfuscated = 0
    class_line = re.compile(r"^([^\s].*?)\s+->\s+([^:]+):$")
    member_line = re.compile(r"^\s+(.+?)\s+->\s+([^\s]+)$")
    for line in text.splitlines():
        match = class_line.match(line)
        if match:
            original_name, obfuscated_name = match.groups()
            class_mapping[obfuscated_name] = {
                "original": original_name,
                "obfuscated": original_name != obfuscated_name,
            }
            continue
        match = member_line.match(line)
        if match:
            member_total += 1
            original = match.group(1).rsplit(" ", 1)[-1]
            member_obfuscated += int(original != match.group(2).split("(", 1)[0])
    dex_classes = []
    for dex in dex_reports:
        for item in dex["symbols"]["class"]:
            class_name = descriptor_to_class_name(item["descriptor"])
            # 官方 AAB 分析器只统计 DEX 顶层类，不重复统计内部类。
            if "$" not in class_name.rsplit(".", 1)[-1]:
                dex_classes.append(class_name)
    dex_classes = sorted(set(dex_classes))
    class_total = len(dex_classes)
    class_obfuscated = sum(
        1 for class_name in dex_classes
        if class_name in class_mapping and class_mapping[class_name]["obfuscated"]
    )
    return {
        "source": MAPPING_PATH,
        "source_type": "proguard_mapping_estimate",
        "obfuscation_percentage": round(class_obfuscated * 100.0 / class_total, 2) if class_total else 0.0,
        "categories": {
            "class": {"total": class_total, "obfuscated": class_obfuscated,
                       "percentage": round(class_obfuscated * 100.0 / class_total, 2) if class_total else 0.0},
        },
        "mapping_classes": len(class_mapping),
        "mapping_classes_found_in_dex": class_obfuscated,
        "member_diagnostic": {
            "total": member_total,
            "obfuscated": member_obfuscated,
            "percentage": round(member_obfuscated * 100.0 / member_total, 2) if member_total else 0.0,
        },
    }


def display_width(value):
    """计算文本在等宽终端中的显示宽度，中文通常占两列。"""
    return sum(
        2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        for char in str(value)
    )


def table_cell(value, width, align="left"):
    text = str(value)
    padding = max(0, width - display_width(text))
    if align == "right":
        return " " * padding + text
    return text + " " * padding


def table_row(values, widths, aligns=None):
    aligns = aligns or ["left"] * len(values)
    return " ".join(
        table_cell(value, width, align)
        for value, width, align in zip(values, widths, aligns)
    )


def print_table(headers, rows, aligns=None):
    """在控制台绘制带完整边框的等宽表格。"""
    aligns = aligns or ["left"] * len(headers)
    widths = [
        max(
            display_width(header),
            *(display_width(row[index]) for row in rows),
        ) + 2
        for index, header in enumerate(headers)
    ]
    border = "+" + "+".join("-" * width for width in widths) + "+"
    print(border)
    print("|" + "|".join(
        table_cell(" " + str(header), width, "left")
        for header, width in zip(headers, widths)
    ) + "|")
    print(border)
    for row in rows:
        cells = []
        for value, width, align in zip(row, widths, aligns):
            text = str(value)
            if align == "right":
                cells.append(" " + table_cell(text, width - 1, "right"))
            else:
                cells.append(table_cell(" " + text, width, "left"))
        print("|" + "|".join(cells) + "|")
    print(border)


def render_html(report, output_path):
    stats = report["statistics"]
    rows = []
    for category, value in stats["categories"].items():
        percentage = value.get("percentage")
        status = "通过" if percentage is None or percentage >= report["threshold_percentage"] else "低于阈值"
        rows.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(category), value.get("total", "-"), value.get("obfuscated", "-"),
            "-" if percentage is None else "{:.2f}%".format(percentage), status))
    comparison_rows = []
    for result in report.get("detection_results", []):
        comparison_rows.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(result["name"]),
            "{:.2f}%".format(result["obfuscation_percentage"]),
            "采用" if result["selected"] else "对比"))
    html_text = """<!doctype html><meta charset="utf-8"><title>AAB 混淆检测报告</title>
<style>body{{font:14px sans-serif;max-width:900px;margin:32px auto;color:#222}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#f5f5f5}}.warn{{color:#b42318}}code{{background:#f5f5f5;padding:2px 4px}}</style>
<h1>AAB DEX 混淆检测报告</h1><p>文件：<code>{file}</code>　生成时间：{time}</p>
<p>总体混淆占比：<strong>{overall:.2f}%</strong>，阈值：{threshold:.2f}%</p>
<table><tr><th>类别</th><th>总数</th><th>疑似混淆</th><th>占比</th><th>结果</th></tr>{rows}</table>
<h2>多方式检测结果</h2>
<table><tr><th>检测方式</th><th>混淆占比</th><th>状态</th></tr>{comparison_rows}</table>
<h2>说明</h2><p>数据来源：{source}。使用 r8.json 时，该值采用 Google Play 官方构建元数据；只有缺少官方元数据时才回退到 mapping 文件或 DEX 名称启发式。</p>
""".format(file=html.escape(report["input"]), time=html.escape(report["generated_at"]),
           overall=stats["obfuscation_percentage"], threshold=report["threshold_percentage"],
           source=html.escape(report["source"]), rows="".join(rows),
           comparison_rows="".join(comparison_rows))
    output_path.write_text(html_text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="检测 AAB 中 DEX 标识符的混淆占比并生成报告")
    parser.add_argument("aab", type=Path, help="待检测的 .aab 文件")
    parser.add_argument("--threshold", type=float, default=25.0, help="阈值百分比，默认 25")
    parser.add_argument("--exclude-prefix", action="append", default=[],
                        help="排除指定类名前缀，可重复传入，例如 --exclude-prefix com.google.")
    args = parser.parse_args()
    if not args.aab.is_file():
        parser.error("AAB 文件不存在：{}".format(args.aab))
    try:
        with zipfile.ZipFile(args.aab) as bundle:
            dex_names = sorted(name for name in bundle.namelist()
                               if re.match(r"(?:[^/]+/)*classes(?:\d+)?\.dex$", name))
            if not dex_names:
                raise ValueError("AAB 中未找到 classes*.dex")
            dex_reports = [parse_dex(bundle.read(name), name) for name in dex_names]
            metadata_stats = read_r8_metadata(bundle)
            mapping_stats = read_mapping_stats(bundle, dex_reports)
    except (OSError, zipfile.BadZipFile, KeyError, ValueError, struct.error) as exc:
        print("检测失败：{}".format(exc), file=sys.stderr)
        return 2

    heuristic_stats = calculate_stats(dex_reports, args.exclude_prefix)
    valid_r8_stats = metadata_stats and metadata_stats.get("valid", True)
    if valid_r8_stats:
        statistics = {
            "total_symbols": None,
            "obfuscated_symbols": None,
            "obfuscation_percentage": metadata_stats["obfuscation_percentage"],
            "categories": {
                "class": {"total": None, "obfuscated": None, "percentage": None},
                "method": {"total": None, "obfuscated": None, "percentage": None},
                "field": {"total": None, "obfuscated": None, "percentage": None},
            },
            "no_obfuscation_percentage": metadata_stats["no_obfuscation_percentage"],
        }
        source = "AAB 内 r8.json（Google Play 指标来源）"
    elif mapping_stats:
        statistics = mapping_stats
        source = "AAB 内 proguard.map（本地映射估算，非 Google Play 精确值）"
    else:
        statistics = heuristic_stats
        source = "DEX 名称启发式（无法获得 Google Play 元数据）"

    detection_results = []
    if valid_r8_stats:
        detection_results.append({
            "name": "Google Play r8.json",
            "source_type": metadata_stats["source_type"],
            "obfuscation_percentage": metadata_stats["obfuscation_percentage"],
            "selected": True,
        })
    if mapping_stats:
        detection_results.append({
            "name": "proguard.map（本地估算）",
            "source_type": "proguard_mapping_estimate",
            "obfuscation_percentage": mapping_stats["obfuscation_percentage"],
            "selected": not valid_r8_stats,
        })
    detection_results.append({
        "name": "DEX 名称启发式",
        "source_type": "dex_heuristic",
        "obfuscation_percentage": heuristic_stats["obfuscation_percentage"],
        "selected": not valid_r8_stats and not mapping_stats,
    })

    report = {
        "input": str(args.aab.resolve()),
        "generated_at": datetime.now(CHINA_TIMEZONE).isoformat(),
        "threshold_percentage": args.threshold,
        "source": source,
        "r8_metadata_error": None if valid_r8_stats or not metadata_stats else metadata_stats.get("error"),
        "source_type": metadata_stats["source_type"] if valid_r8_stats else (
            mapping_stats["source_type"] if mapping_stats else "dex_heuristic"),
        "detection_results": detection_results,
        "dex_files": [{key: value for key, value in dex.items() if key != "symbols"} for dex in dex_reports],
        "statistics": statistics,
    }
    print("AAB：{}".format(args.aab))
    print("总体混淆占比：{:.2f}%（阈值 {:.2f}%）".format(
        report["statistics"]["obfuscation_percentage"], args.threshold))
    print("")
    print("报告信息")
    print("文件：{}".format(report["input"]))
    print("生成时间：{}".format(report["generated_at"]))
    print("数据来源：{}".format(report["source"]))
    print("说明：使用有效 r8.json 时，混淆率来自 Google Play 官方构建元数据；"
          "缺少或无法验证官方元数据时，回退到 proguard.map 或 DEX 名称启发式，"
          "回退结果仅作为本地估算，不能保证与 Google Play 完全一致。")
    print("")
    print("各方式检测结果：")
    if report["r8_metadata_error"]:
        print("  警告：r8.json 无效，未按 Google Play 官方元数据采用：{}".format(
            report["r8_metadata_error"]))
    if valid_r8_stats:
        print("  r8.json DEX 校验：{}（元数据 {} 个，AAB {} 个）".format(
            "匹配" if metadata_stats["r8_dex_checksum_match"] else "不匹配",
            metadata_stats["r8_dex_count"], metadata_stats["bundle_dex_count"]))
    print("")
    print("多方式检测结果")
    detection_rows = []
    for result in report["detection_results"]:
        detection_rows.append([
            result["name"],
            "{:.2f}%".format(result["obfuscation_percentage"]),
            "采用" if result["selected"] else "对比",
        ])
    print_table(["检测方式", "混淆占比", "状态"], detection_rows,
                ["left", "right", "left"])
    print("")
    print("分类统计")
    category_rows = []
    for category, value in report["statistics"]["categories"].items():
        if value.get("percentage") is None:
            category_rows.append([category, "-", "-", "-", "无明细"])
        else:
            status = "通过" if value["percentage"] >= args.threshold else "低于阈值"
            category_rows.append([
                category,
                value["total"],
                value["obfuscated"],
                "{:.2f}%".format(value["percentage"]),
                status,
            ])
    print_table(["类别", "总数", "疑似混淆", "占比", "结果"], category_rows,
                ["left", "right", "right", "right", "left"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
