# main.py
import os
import sys
import tkinter as tk

# Định vị thư mục game/ và game/core/ để các module tự nhận diện nhau
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(BASE_DIR, "game")
CORE_DIR = os.path.join(GAME_DIR, "core")

for path in (GAME_DIR, CORE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from board import discover_levels
from ui.gui import BloxorzGUI


def main() -> None:
    levels_dir = os.path.join(GAME_DIR, "levels")
    os.makedirs(levels_dir, exist_ok=True)

    # 1. Tự động quét tất cả các file .json trong game/levels/
    level_paths = discover_levels(levels_dir)

    # 2. Hỗ trợ truyền đường dẫn file JSON từ tham số dòng lệnh (nếu có)
    if len(sys.argv) > 1:
        custom_path = os.path.abspath(sys.argv[1])
        if os.path.isfile(custom_path) and custom_path not in level_paths:
            level_paths.insert(0, custom_path)

    # 3. Khởi chạy giao diện Bloxorz 2.5D
    root = tk.Tk()
    BloxorzGUI(root, level_paths, levels_dir=levels_dir)
    root.mainloop()


if __name__ == "__main__":
    main()