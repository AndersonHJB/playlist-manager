# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 10:56
# @Author  : AI悦创
# @FileName: playlist-manager.py
# @Software: PyCharm
# @Blog    ：https://bornforthis.cn/
# code is far away from bugs with the god animal protecting
#    I love animals. They taste delicious.
"""
本程序演示如何使用 Python 的高级编程技巧来实现一个
灵活、健壮且易扩展的控制台音乐播放列表管理工具。

主要特点 ⚙️
1. **面向对象设计** —— 使用 dataclass 封装歌曲信息。
2. **多维数据结构** —— 使用 `list[dict]` 持久化并动态修改数据。
3. **函数/方法 + 参数 & 返回值** —— 各功能模块化，便于单元测试。
4. **非基础字符串处理** —— 对用户输入做大小写忽略、正则校验。
5. **第三方库调用** —— 使用 *tabulate* 美化表格输出，若未安装自动降级。
6. **稳健的输入校验** —— 处理预期、边界与无效输入，防止程序崩溃。
7. **可持续扩展** —— 所有常量集中在 `config.py`，便于后期功能升级。

运行环境 🖥️
Python ≥ 3.9；可选依赖：`pip install tabulate`

文件结构 📁
├── playlist_manager.py  —— 主程序（即本文件）
└── README.md            —— 运行指南（留空由学生撰写）

版本控制 🕹
请将本文件提交到 **私有 GitHub 仓库** 并按功能迭代打 tag：
v0.1 初始化菜单 · v0.2 完成增删改查 · v1.0 正式发布等
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

# ====== 常量配置 ====== #
DATA_FILE: Path = Path("songs.json")      # 本地持久化文件
MIN_TITLE_LEN: int = 1                    # 标题/艺术家最小长度
MAX_TITLE_LEN: int = 90                   # 标题/艺术家最大长度
VALID_INT_PATTERN = re.compile(r"^\d+$")  # 正整数校验
SAMPLE_DATA = [
    ("Shape of You", "Ed Sheeran", 1560),
    ("Blinding Lights", "The Weeknd", 1780),
    ("Bad Guy", "Billie Eilish", 1340),
    ("Dance Monkey", "Tones and I", 1120),
    ("Levitating", "Dua Lipa", 980),
]

# tabulate 为第三方库，用户若未安装自动降级到纯文本表格
try:
    from tabulate import tabulate  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    def tabulate(rows, headers, tablefmt="github"):  # fallback
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*rows, headers)]  # type: ignore
        border = "| " + " | ".join("-" * w for w in col_widths) + " |"
        header_row = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " |"
        data_rows = ["| " + " | ".join(f"{c:<{w}}" for c, w in zip(row, col_widths)) + " |" for row in rows]
        return "\n".join([border, header_row, border, *data_rows, border])


# ====== 数据模型 ====== #
@dataclass
class Song:
    """歌曲数据结构"""
    title: str
    artist: str
    plays: int

    def to_row(self) -> List[str]:
        return [self.title, self.artist, str(self.plays)]

    @classmethod
    def from_dict(cls, data: dict) -> "Song":
        return cls(**data)


# ====== 工具函数 ====== #
def load_songs() -> List[Song]:
    """从本地 JSON 恢复歌曲列表；首次运行写入示例数据"""
    if DATA_FILE.exists():
        with DATA_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
        return [Song.from_dict(d) for d in data]
    # 首次运行：写入示例数据
    songs = [Song(*item) for item in SAMPLE_DATA]
    save_songs(songs)
    return songs


def save_songs(songs: List[Song]) -> None:
    """将当前歌曲列表保存到 JSON 文件"""
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in songs], f, ensure_ascii=False, indent=2)


def validate_text(prompt: str) -> str:
    """通用文本输入校验（长度 & 非空）"""
    while True:
        txt = input(prompt).strip()
        if MIN_TITLE_LEN <= len(txt) <= MAX_TITLE_LEN:
            return txt
        print(f"＞ 输入应为 {MIN_TITLE_LEN}-{MAX_TITLE_LEN} 个字符，请重试。")


def validate_int(prompt: str) -> int:
    """正整数输入校验"""
    while True:
        txt = input(prompt).strip()
        if VALID_INT_PATTERN.match(txt):
            return int(txt)
        print("＞ 请输入非负整数！")


def find_song(songs: List[Song], title: str, artist: str) -> Optional[Song]:
    """按标题 + 艺术家查找歌曲（忽略大小写）"""
    title, artist = title.lower(), artist.lower()
    for s in songs:
        if s.title.lower() == title and s.artist.lower() == artist:
            return s
    return None


def display_songs(songs: List[Song]) -> None:
    if not songs:
        print("♪ 歌曲列表为空。\n")
        return
    rows = [s.to_row() for s in songs]
    print(tabulate(rows, headers=["歌曲", "艺术家", "播放次数"], tablefmt="github"))
    print()  # 空行


# ====== 核心功能 ====== #
def add_song(songs: List[Song]) -> None:
    print("\n--- 添加歌曲 ---")
    title = validate_text("输入歌曲名称：")
    artist = validate_text("输入歌手名称：")
    if find_song(songs, title, artist):
        print("＞ 该歌曲已存在，若需修改播放量请使用选项 3。\n")
        return
    plays = validate_int("输入播放次数：")
    songs.append(Song(title, artist, plays))
    save_songs(songs)
    print("✓ 添加成功！\n")


def edit_song(songs: List[Song]) -> None:
    print("\n--- 修改播放次数 ---")
    title = validate_text("输入歌曲名称：")
    artist = validate_text("输入歌手名称：")
    song = find_song(songs, title, artist)
    if not song:
        print("＞ 未找到该歌曲。\n")
        return
    new_plays = validate_int(f"当前播放 {song.plays} 次，输入新的播放次数：")
    song.plays = new_plays
    save_songs(songs)
    print("✓ 修改成功！\n")


def delete_song(songs: List[Song]) -> None:
    print("\n--- 删除歌曲 ---")
    title = validate_text("输入歌曲名称：")
    artist = validate_text("输入歌手名称：")
    song = find_song(songs, title, artist)
    if not song:
        print("＞ 未找到该歌曲。\n")
        return
    songs.remove(song)
    save_songs(songs)
    print("✓ 删除成功！\n")


def generate_playlist(songs: List[Song]) -> None:
    print("\n--- 生成播放列表 ---")
    min_plays = validate_int("输入最小播放次数：")
    filtered = [s for s in songs if s.plays >= min_plays]
    if not filtered:
        print("＞ 没有歌曲符合条件。\n")
        return
    print(f"符合条件（≥{min_plays} 次）的歌曲：")
    display_songs(filtered)


def main() -> None:
    songs = load_songs()

    MENU = """
==================  菜  单  ==================
1. 打印所有歌曲
2. 添加歌曲
3. 修改歌曲的播放次数
4. 删除歌曲
5. 按最小播放次数生成播放列表
6. 退出
==============================================
"""
    actions = {
        "1": lambda: display_songs(songs),
        "2": lambda: add_song(songs),
        "3": lambda: edit_song(songs),
        "4": lambda: delete_song(songs),
        "5": lambda: generate_playlist(songs),
        "6": lambda: sys.exit("👋 感谢使用，再见！"),
    }

    while True:
        print(MENU)
        choice = input("请输入功能序号：").strip()
        action = actions.get(choice)
        if action:
            action()
        else:
            print("＞ 无效选择，请输入 1-6。\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户终止，程序退出。")
