#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从导出的 xlsx 聊天记录中提取可用于真心为你技能训练的结构化数据。
该脚本会输出三类文件：
1) chat_records.jsonl：所有消息
2) dialogue_pairs.jsonl：连续对话对（用于微调/示例）
3) skill_profile.json 与 skill_report.md：统计画像与学习摘要
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import openpyxl


TEXT_MSG_HINT = ("文本消息", "文本信息")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Message:
    source_file: str
    index: Optional[int]
    time: str
    sender: str
    msg_type: str
    content: str
    is_text: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 xlsx 聊天导出中生成真心为你训练素材")
    parser.add_argument(
        "--source-dir",
        default=str(PROJECT_ROOT / "data" / "input"),
        help="xlsx 文件目录（默认项目下的 data/input）",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "outputs"),
        help="输出目录（默认项目下的 outputs）",
    )
    parser.add_argument("--self-name", default="我", help="主动方默认名称（例如“我”）")
    parser.add_argument("--min-pair-gap-min", type=int, default=120, help="超过多少分钟不算连续回复对（默认120）")
    parser.add_argument(
        "--strict-text-only",
        action="store_true",
        help="只保留文本内容消息，过滤图片、语音、系统消息",
    )
    return parser.parse_args()


def load_workbook_text(path: Path) -> List[Tuple[Any, ...]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    return rows


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text


def parse_datetime(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if value is None:
        return ""
    text = clean_text(value)
    if not text:
        return ""
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"]:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return text


def detect_columns(header: Iterable[Any]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for i, col in enumerate(header):
        value = clean_text(col)
        if not value:
            continue
        if value in ("序号", "序号(或ID)", "序列"):
            mapping["index"] = i
        elif "时间" in value:
            mapping["time"] = i
        elif "发送者" in value:
            mapping["sender"] = i
        elif "消息类型" in value:
            mapping["type"] = i
        elif value == "内容" or value.startswith("内容"):
            mapping["content"] = i
    return mapping


def guess_header_row(rows: List[Tuple[Any, ...]]) -> Tuple[int, Dict[str, int]]:
    for idx, row in enumerate(rows[:20], start=1):
        mapping = detect_columns(row)
        if len(mapping) >= 3 and {"time", "sender", "type", "content"}.issubset(set(mapping.keys())):
            return idx, mapping
    # 兼容旧导出：默认前四列为序号/时间/发送者/类型/内容
    fallback = {"index": 0, "time": 1, "sender": 2, "type": 3, "content": 4}
    return 1, fallback


def is_text_message(msg_type: str) -> bool:
    return any(key in msg_type for key in TEXT_MSG_HINT)


def is_system_or_empty(sender: str, msg_type: str, content: str) -> bool:
    if not sender:
        return True
    if sender == "系统消息":
        return True
    if "系统" in msg_type and "消息" in msg_type and not content:
        return True
    if "系统消息" in msg_type:
        return True
    return False


def read_messages(path: Path) -> List[Message]:
    rows = load_workbook_text(path)
    header_row, cols = guess_header_row(rows)
    messages: List[Message] = []
    for row in rows[header_row:]:
        if not row:
            continue
        index = row[cols.get("index", 0)] if cols.get("index") is not None else None
        time_text = parse_datetime(row[cols.get("time", 1)] if cols.get("time") is not None else "")
        sender = clean_text(row[cols.get("sender", 2)] if cols.get("sender") is not None else "")
        msg_type = clean_text(row[cols.get("type", 3)] if cols.get("type") is not None else "")
        content = clean_text(row[cols.get("content", 4)] if cols.get("content") is not None else "")
        if not sender and not msg_type and not content:
            continue
        if not content and "消息" in msg_type:
            content = "[{}]".format(msg_type)
        if not index:
            continue
        messages.append(
            Message(
                source_file=path.name,
                index=int(index) if str(index).isdigit() else None,
                time=time_text,
                sender=sender,
                msg_type=msg_type,
                content=content,
                is_text=is_text_message(msg_type),
            )
        )
    return messages


def build_pairs(messages: List[Message], max_gap_min: int) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    for left, right in zip(messages, messages[1:]):
        if left.source_file != right.source_file:
            continue
        if left.sender == right.sender:
            continue
        if left.time and right.time:
            try:
                t1 = datetime.strptime(left.time, "%Y-%m-%d %H:%M:%S")
                t2 = datetime.strptime(right.time, "%Y-%m-%d %H:%M:%S")
                gap = (t2 - t1).total_seconds() / 60
                if gap < 0 or gap > max_gap_min:
                    continue
            except ValueError:
                pass
        if not left.content or not right.content:
            continue
        if is_system_or_empty(left.sender, left.msg_type, left.content):
            continue
        if is_system_or_empty(right.sender, right.msg_type, right.content):
            continue
        pairs.append(
            {
                "source_file": left.source_file,
                "speaker_a": left.sender,
                "speaker_b": right.sender,
                "input": left.content,
                "target": right.content,
                "time_a": left.time,
                "time_b": right.time,
                "is_text_a": left.is_text,
                "is_text_b": right.is_text,
            }
        )
    return pairs


def build_profile(messages: List[Message], pairs: List[Dict[str, Any]], self_name: str) -> Dict[str, Any]:
    sender_counter = Counter(m.sender for m in messages if m.sender)
    type_counter = Counter(m.msg_type for m in messages if m.msg_type)
    length_counter = Counter()
    emoji_counter = Counter()

    emoji_pattern = re.compile(r"[\U0001F300-\U0001FAFF]|[\u2600-\u26FF]")

    for msg in messages:
        if msg.content:
            length_counter[msg.sender] += len(msg.content)
            emoji_counter[msg.sender] += 1 if emoji_pattern.search(msg.content) else 0

    sender_text_count = defaultdict(int)
    sender_text_len = defaultdict(int)
    for msg in messages:
        if not msg.is_text:
            continue
        sender_text_count[msg.sender] += 1
        sender_text_len[msg.sender] += len(msg.content)

    senders = list(sender_counter.keys())
    if self_name not in senders and senders:
        self_name = sender_counter.most_common(1)[0][0]
    partner_names = [s for s in sender_counter if s not in {self_name, "", "系统消息", "系统"}]

    text_pairs = [p for p in pairs if p["is_text_a"] and p["is_text_b"]]

    return {
        "message_total": len(messages),
        "messages_by_sender": sender_counter,
        "messages_by_type": type_counter,
        "self_name": self_name,
        "partner_names": partner_names[:5],
        "avg_text_length_by_sender": {
            k: round(v / max(sender_text_count[k], 1), 2) for k, v in sender_text_len.items()
        },
        "emoji_usage_by_sender": {
            k: emoji_counter[k] for k in sender_text_count
        },
        "dialogue_pair_total": len(pairs),
        "text_pair_total": len(text_pairs),
        "top_pair_examples": text_pairs[:8],
        "sample_messages": messages[:10],
    }


def write_jsonl(records: Iterable[Dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe_int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def render_markdown_report(profile: Dict[str, Any], path: Path) -> None:
    lines: List[str] = []
    lines.append("# 真心为你 技能学习摘要")
    lines.append("")
    lines.append(f"- 总消息数：{profile['message_total']}")
    lines.append(f"- 对话对数：{profile['dialogue_pair_total']}（文本对：{profile['text_pair_total']}）")
    lines.append(f"- 识别主体：{profile['self_name']}，对象：{', '.join(profile['partner_names']) or '未识别'}")
    lines.append("")
    lines.append("## 按发送方统计")
    for name, count in sorted(profile['messages_by_sender'].items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {name or '系统/未识别'}: {count}")
    lines.append("")
    lines.append("## 按消息类型统计")
    for name, count in sorted(profile['messages_by_type'].items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- {name}: {count}")
    lines.append("")
    lines.append("## 平均文本长度")
    for name, avg in profile['avg_text_length_by_sender'].items():
        lines.append(f"- {name or '系统/未识别'}: {avg}")
    lines.append("")
    lines.append("## 可用于训练的高质量对话对（前 8 条）")
    for item in profile['top_pair_examples']:
        lines.append(f"- [{item['source_file']}] {item['speaker_a']} -> {item['speaker_b']}")
        lines.append(f"  - 问：{item['input']}")
        lines.append(f"  - 答：{item['target']}")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    xlsx_files = sorted(source_dir.glob("*.xlsx"))
    if not xlsx_files:
        raise RuntimeError(f"未在 {source_dir} 找到 xlsx 文件")

    all_messages: List[Message] = []
    per_file_counts: Dict[str, Dict[str, int]] = {}

    for file in xlsx_files:
        msgs = read_messages(file)
        if not msgs:
            continue
        all_messages.extend(msgs)
        per_file_counts[file.name] = {
            "total": len(msgs),
        }

    all_messages.sort(key=lambda msg: (msg.source_file, safe_int(msg.index), msg.time or ""))

    pairs = build_pairs(all_messages, args.min_pair_gap_min)
    if args.strict_text_only:
        pairs = [p for p in pairs if p["is_text_a"] and p["is_text_b"]]

    records = [
        {
            "source_file": m.source_file,
            "index": m.index,
            "time": m.time,
            "sender": m.sender,
            "msg_type": m.msg_type,
            "content": m.content,
            "is_text": m.is_text,
        }
        for m in all_messages
    ]

    records_path = output_dir / "chat_records.jsonl"
    pair_path = output_dir / "dialogue_pairs.jsonl"
    profile_path = output_dir / "skill_profile.json"
    report_path = output_dir / "skill_report.md"
    meta_path = output_dir / "project_meta.json"

    write_jsonl(records, records_path)
    write_jsonl(pairs, pair_path)

    profile = build_profile(all_messages, pairs, self_name=args.self_name)
    profile["sample_messages"] = [
        {
            "source_file": m.source_file,
            "index": m.index,
            "time": m.time,
            "sender": m.sender,
            "msg_type": m.msg_type,
            "content": m.content,
            "is_text": m.is_text,
        }
        for m in all_messages[:10]
    ]
    profile["source_dir"] = str(source_dir)
    profile["files"] = {
        "count": len(xlsx_files),
        "per_file_messages": per_file_counts,
        "names": [p.name for p in xlsx_files],
    }

    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    render_markdown_report(profile, report_path)

    meta_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_dir": str(source_dir),
                "output_dir": str(output_dir),
                "records": len(records),
                "pairs": len(pairs),
                "strict_text_only": args.strict_text_only,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"已输出：{records_path}")
    print(f"已输出：{pair_path}")
    print(f"已输出：{profile_path}")
    print(f"已输出：{report_path}")
    print(f"已输出：{meta_path}")


if __name__ == "__main__":
    main()
