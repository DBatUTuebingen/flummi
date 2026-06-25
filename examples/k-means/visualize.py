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
    # Load the CSV file (no headers, each row represents an entire cluster list string)
    df = pd.read_csv(sys.argv[1], header=None)

    # Configure the plot area
    plt.figure(figsize=(10, 8))

    # Iterate through each row and plot the corresponding cluster
    for idx, row in df.iterrows():
        # Safely parse the Python literal array of dictionaries from the row string
        points = ast.literal_eval(row[0])

        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]

        # Render the points with a unique color per cluster
        plt.scatter(
            xs,
            ys,
            label=f"Cluster {idx + 1}",
            alpha=0.7,
            edgecolors="none",
            s=30,
        )

    # Add clear labeling and styling
    plt.title(
        "K-Means Point Clusters Visualization",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("X Coordinate", fontsize=11)
    plt.ylabel("Y Coordinate", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)

    # Place the legend neatly outside the plot area to avoid overlap
    plt.legend(title="Clusters", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Automatically adjust layout boundaries so text isn't cut off
    plt.tight_layout()

    # Save the output visualization
    output_filename = "clusters_plot.png"
    plt.savefig(output_filename, dpi=150)
