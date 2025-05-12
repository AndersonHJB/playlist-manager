# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 10:56
# @Author  : AI悦创
# @FileName: playlist-manager.py|简易音乐播放列表管理程序
# @Software: PyCharm
# @Blog    ：https://bornforthis.cn/
# code is far away from bugs with the god animal protecting
#    I love animals. They taste delicious.
"""
本程序满足以下作业要求：
▪ 变量含数值、文本、布尔三种数据类型
▪ 采用顺序 / 选择 / 循环控制结构
▪ 从键盘输入并输出到终端
▪ 至少两项高级技巧：
   ① 动态修改列表 / 字典等集合数据
   ② 正则表达式进行非基础字符串校验
   ③ 第三方库 tabulate （若未安装自动降级）
▪ 充分的输入合法性检查，处理边界与异常
▪ 代码使用清晰的常量与注释；符合 PEP 8
"""

import json
import re
import sys
from pathlib import Path

# =========== 全局常量 =========== #
DATA_FILE = Path("songs.json")             # 持久化文件
TITLE_RANGE = (1, 90)                      # 标题/歌手字符长度限制
INT_RE = re.compile(r"^\d+$")              # 正整数校验
SAMPLE_DATA = [                            # 首次运行示例数据
    {"title": "Shape of You", "artist": "Ed Sheeran", "plays": 1560},
    {"title": "Blinding Lights", "artist": "The Weeknd", "plays": 1780},
    {"title": "Bad Guy", "artist": "Billie Eilish", "plays": 1340},
    {"title": "Dance Monkey", "artist": "Tones and I", "plays": 1120},
    {"title": "Levitating", "artist": "Dua Lipa", "plays": 980},
]

# -------- tabulate：若缺失自动降级 -------- #
try:
    from tabulate import tabulate  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    def tabulate(rows, headers, tablefmt="github"):  # 简陋备选实现
        widths = [max(len(str(c)) for c in col) for col in zip(*rows, headers)]
        line = "| " + " | ".join("-" * w for w in widths) + " |"
        head = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, widths)) + " |"
        body = ["| " + " | ".join(f"{c:<{w}}" for c, w in zip(r, widths)) + " |" for r in rows]
        return "\n".join([line, head, line, *body, line])


# =========== 数据存取 =========== #
def load_songs():
    """读取歌曲记录；若无文件则写入示例数据。"""
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    DATA_FILE.write_text(json.dumps(SAMPLE_DATA, ensure_ascii=False, indent=2), encoding="utf-8")
    return SAMPLE_DATA.copy()


def save_songs(songs):
    """保存歌曲记录到本地 JSON。"""
    DATA_FILE.write_text(json.dumps(songs, ensure_ascii=False, indent=2), encoding="utf-8")


# =========== 输入校验 =========== #
def ask_text(prompt):
    """文本输入校验：非空且长度在指定范围。"""
    lo, hi = TITLE_RANGE
    while True:
        txt = input(prompt).strip()
        if lo <= len(txt) <= hi:
            return txt
        print(f"＞ 输入需为 {lo}–{hi} 个字符，请重试。")


def ask_int(prompt):
    """正整数输入校验。"""
    while True:
        val = input(prompt).strip()
        if INT_RE.fullmatch(val):
            return int(val)
        print("＞ 请输入非负整数！")


# =========== 辅助逻辑 =========== #
def find_song(songs, title, artist):
    """按标题+歌手查找（忽略大小写），存在返回索引，否则 -1。"""
    title, artist = title.lower(), artist.lower()
    for i, s in enumerate(songs):
        if s["title"].lower() == title and s["artist"].lower() == artist:
            return i
    return -1


def show_table(rows, header):
    """打印表格；空列表时给出提示。"""
    if rows:
        print(tabulate(rows, header, tablefmt="github"), end="\n\n")
    else:
        print("♪ 歌曲列表为空。\n")


# =========== 核心功能 =========== #
def print_all(songs):
    show_table([[s["title"], s["artist"], s["plays"]] for s in songs],
               ["歌曲", "艺术家", "播放次数"])


def add_song(songs):
    print("\n--- 添加歌曲 ---")
    title = ask_text("输入歌曲名称：")
    artist = ask_text("输入歌手名称：")
    if find_song(songs, title, artist) != -1:
        print("＞ 该歌曲已存在，若需修改播放量请选 3。\n")
        return
    plays = ask_int("输入播放次数：")
    songs.append({"title": title, "artist": artist, "plays": plays})
    save_songs(songs)
    print("✓ 添加成功！\n")


def edit_song(songs):
    print("\n--- 修改播放次数 ---")
    title = ask_text("输入歌曲名称：")
    artist = ask_text("输入歌手名称：")
    idx = find_song(songs, title, artist)
    if idx == -1:
        print("＞ 未找到该歌曲。\n")
        return
    new_plays = ask_int(f"当前播放 {songs[idx]['plays']} 次，输入新的播放次数：")
    songs[idx]["plays"] = new_plays
    save_songs(songs)
    print("✓ 修改成功！\n")


def delete_song(songs):
    print("\n--- 删除歌曲 ---")
    title = ask_text("输入歌曲名称：")
    artist = ask_text("输入歌手名称：")
    idx = find_song(songs, title, artist)
    if idx == -1:
        print("＞ 未找到该歌曲。\n")
        return
    songs.pop(idx)
    save_songs(songs)
    print("✓ 删除成功！\n")


def generate_playlist(songs):
    print("\n--- 生成播放列表 ---")
    min_plays = ask_int("输入最小播放次数：")
    filtered = [s for s in songs if s["plays"] >= min_plays]
    if not filtered:
        print("＞ 没有歌曲符合条件。\n")
    else:
        print(f"符合 ≥{min_plays} 次的歌曲：")
        print_all(filtered)


# =========== 主循环 =========== #
def main():
    songs = load_songs()
    menu = """
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
        "1": lambda: print_all(songs),
        "2": lambda: add_song(songs),
        "3": lambda: edit_song(songs),
        "4": lambda: delete_song(songs),
        "5": lambda: generate_playlist(songs),
        "6": lambda: sys.exit("👋 感谢使用，再见！"),
    }

    while True:
        print(menu)
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
