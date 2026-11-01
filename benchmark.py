# benchmark.py
import csv
import os
import sys
from typing import Any, Callable, Dict, List, Tuple

# Tự động nhận diện đường dẫn từ thư mục gốc và package game/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.join(BASE_DIR, "game")
CORE_DIR = os.path.join(GAME_DIR, "core")

for p in (BASE_DIR, GAME_DIR, CORE_DIR):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from board import Board, discover_levels
import solver
from state import GameState

try:
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

SolverFunc = Callable[[Board, GameState], Dict[str, Any]]

ALGORITHMS: List[Tuple[str, SolverFunc]] = [
    ("BFS", solver.solve_bfs),
    ("DFS", solver.solve_dfs),
    ("UCS", solver.solve_ucs),
    ("A*", solver.solve_astar),
]

OUTPUT_DIR = os.path.join(BASE_DIR, "results")


def _resolve_levels_dir() -> str:
    game_levels = os.path.join(GAME_DIR, "levels")
    if os.path.isdir(game_levels):
        return game_levels
    return os.path.join(BASE_DIR, "levels")


def _export_pivot_csv(
    results: List[Dict[str, Any]],
    metric_key: str,
    filename: str,
) -> None:
    """Xuất bảng so sánh từng tiêu chí (Hàng: Level, Cột: BFS, DFS, UCS, A*)."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    alg_names = [alg for alg, _ in ALGORITHMS]
    fieldnames = ["level_id", "level_tag", "level_name", "group", *alg_names]

    levels_seen: List[Tuple[int, str, str, str]] = []
    for r in results:
        lvl_info = (r["level_id"], r["level_tag"], r["level_name"], r["group"])
        if lvl_info not in levels_seen:
            levels_seen.append(lvl_info)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lvl_id, lvl_tag, lvl_name, grp in levels_seen:
            row: Dict[str, Any] = {
                "level_id": lvl_id,
                "level_tag": lvl_tag,
                "level_name": lvl_name,
                "group": grp,
            }
            for alg in alg_names:
                val = next(
                    (
                        r[metric_key]
                        for r in results
                        if r["level_id"] == lvl_id and r["algorithm"] == alg
                    ),
                    "-",
                )
                row[alg] = val
            writer.writerow(row)

    print(f"[CSV] Đã lưu: {filepath}")


def plot_charts(results: List[Dict[str, Any]]) -> None:
    """Vẽ 4 biểu đồ so sánh hiệu năng và lưu trực tiếp vào thư mục results/."""
    if not results:
        return
    if not HAS_MATPLOTLIB:
        print(
            "\n[!] Chưa cài đặt matplotlib. Chạy lệnh `pip install matplotlib` "
            "để tự động xuất 4 biểu đồ PNG vào thư mục results/."
        )
        return

    level_ids = sorted({int(r["level_id"]) for r in results})
    level_labels = [f"L{idx}" for idx in level_ids]
    alg_names = [alg for alg, _ in ALGORITHMS]
    colors = {
        "BFS": "#2563EB",
        "DFS": "#DC2626",
        "UCS": "#7C3AED",
        "A*": "#059669",
    }

    metrics_cfg = [
        (
            "time_ms",
            "Search Time Comparison Across Levels (ms - Log Scale)",
            "Search Time (ms)",
            "chart_time.png",
            True,
        ),
        (
            "memory_kb",
            "Peak Memory Usage Comparison Across Levels (KB - Log Scale)",
            "Peak Memory (KB)",
            "chart_memory.png",
            True,
        ),
        (
            "expanded_nodes",
            "Expanded Nodes Comparison Across Levels (Log Scale)",
            "Expanded Nodes",
            "chart_nodes.png",
            True,
        ),
        (
            "solution_length",
            "Solution Length Comparison Across Levels (Moves)",
            "Solution Length (Moves)",
            "chart_length.png",
            False,
        ),
    ]

    x_positions = list(range(len(level_ids)))
    bar_width = 0.2

    for metric_key, title, ylabel, filename, use_log in metrics_cfg:
        plt.figure(figsize=(13.5, 5.5))
        for i, alg in enumerate(alg_names):
            vals = [
                float(
                    next(
                        (
                            r[metric_key]
                            for r in results
                            if r["level_id"] == lvl_id and r["algorithm"] == alg
                        ),
                        0.0,
                    )
                )
                for lvl_id in level_ids
            ]
            # Tránh giá trị <= 0 khi vẽ trục Logarit
            if use_log:
                vals = [max(v, 1e-3) for v in vals]

            offsets = [x + (i - 1.5) * bar_width for x in x_positions]
            plt.bar(offsets, vals, width=bar_width, label=alg, color=colors[alg])

        plt.title(title, fontsize=13, fontweight="bold")
        plt.xlabel(
            "Test Levels (G1: L1-L3 | G2: L4-L6 | G3: L7-L9 | G4: L10-L12 | G5: L13-L15)",
            fontsize=10,
        )
        plt.ylabel(ylabel, fontsize=10)
        plt.xticks(x_positions, level_labels)
        if use_log:
            plt.yscale("log")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, filename)
        plt.savefig(out_path, dpi=200)
        plt.close()
        print(f"[PNG] Đã lưu biểu đồ: {out_path}")


def run_all_benchmarks() -> None:
    levels_dir = _resolve_levels_dir()
    level_paths = discover_levels(levels_dir)
    if not level_paths:
        print(f"Không tìm thấy file level (.json) nào trong: {levels_dir}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results: List[Dict[str, Any]] = []

    header = (
        f"{'Level':<8} | {'Alg':<5} | {'Time (ms)':>10} | "
        f"{'Mem (KB)':>10} | {'Nodes':>8} | {'Len':>5}"
    )
    print(header)
    print("-" * len(header))

    for idx, path in enumerate(level_paths, start=1):
        board = Board.from_json(path)
        init_state = board.get_initial_state()
        level_tag = f"Level {idx}"
        group_idx = (idx - 1) // 3 + 1

        for alg_name, solve_fn in ALGORITHMS:
            res = solve_fn(board, init_state)
            actions = res.get("actions", [])
            time_ms = round(res.get("time_sec", 0.0) * 1000.0, 3)
            mem_kb = round(res.get("memory_kb", 0.0), 3)
            nodes = int(res.get("expanded_nodes", 0))
            length = int(res.get("solution_length", len(actions)))

            print(
                f"{level_tag:<8} | {alg_name:<5} | {time_ms:>10.3f} | "
                f"{mem_kb:>10.3f} | {nodes:>8} | {length:>5}"
            )

            results.append(
                {
                    "level_id": idx,
                    "level_tag": level_tag,
                    "level_name": board.name,
                    "group": f"Group {group_idx}",
                    "algorithm": alg_name,
                    "time_ms": time_ms,
                    "memory_kb": mem_kb,
                    "expanded_nodes": nodes,
                    "solution_length": length,
                }
            )

    print()
    # 1. Xuất file CSV tổng hợp toàn bộ kết quả
    master_csv = os.path.join(OUTPUT_DIR, "all_experiments.csv")
    with open(master_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "level_id",
                "level_tag",
                "level_name",
                "group",
                "algorithm",
                "time_ms",
                "memory_kb",
                "expanded_nodes",
                "solution_length",
            ],
        )
        writer.writeheader()
        writer.writerows(results)
    print(f"[CSV] Đã lưu bảng tổng hợp: {master_csv}")

    # 2. Xuất 4 bảng CSV đối chiếu theo từng tiêu chí
    _export_pivot_csv(results, "time_ms", "table_time_ms.csv")
    _export_pivot_csv(results, "memory_kb", "table_memory_kb.csv")
    _export_pivot_csv(results, "expanded_nodes", "table_expanded_nodes.csv")
    _export_pivot_csv(results, "solution_length", "table_solution_length.csv")

    # 3. Vẽ và lưu 4 biểu đồ PNG vào cùng thư mục results/
    plot_charts(results)


if __name__ == "__main__":
    run_all_benchmarks()