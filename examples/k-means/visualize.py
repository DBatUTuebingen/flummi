#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pandas",
#     "matplotlib",
# ]
# ///

import ast
import sys

import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    file = sys.argv[1]
    df = pd.read_csv(file, header=None)

    plt.figure(figsize=(10, 8))

    for idx, row in df.iterrows():
        points = ast.literal_eval(row[0])

        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]

        plt.scatter(
            xs,
            ys,
            marker=".",
            alpha=0.7,
            edgecolors="none",
            s=5,
        )

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(file + ".png", dpi=150)
