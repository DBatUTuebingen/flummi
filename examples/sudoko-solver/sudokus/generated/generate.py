#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "requests",
#   "urllib3",
#   "typer",
#   "python-dotenv",
#   "rich",
# ]
# ///

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import StrEnum
from multiprocessing import cpu_count
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from requests import Session
from requests.adapters import HTTPAdapter
from rich.progress import (
    Progress,
    TextColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    SpinnerColumn,
)


load_dotenv(override=True)
# just create a .env file with variable YOUDOSUDOKU_API_KEY containing your api key!

s = Session()
s.headers = {
    "Content-Type": "application/json",
    "x-api-key": os.getenv("YOUDOSUDOKU_API_KEY"),
}
s.mount("https://", HTTPAdapter(max_retries=10))


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


def download_sudoku(difficulty: Difficulty) -> tuple[str, int]:
    response = s.get(
        "https://youdosudoku.com/api/",
        json={"difficulty": difficulty, "solution": False, "array": False},
    )
    response.raise_for_status()

    puzzle: str = response.json()["puzzle"]
    number_of_clues: int = 81 - puzzle.count("0")

    return puzzle, number_of_clues


app = typer.Typer()


@app.command(
    name="generate",
    no_args_is_help=True,
    help="Generate/download sudokus via [u]https://youdosudoku.com[/u].",
)
def generate(
    count: Annotated[
        int, typer.Argument(help="The number of sudokus to generate.")
    ],
    output: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            help="The file to write the generate sudokus to.",
            file_okay=True,
            dir_okay=False,
            writable=True,
        ),
    ] = Path("sudokus.csv"),
    difficulty: Annotated[
        Difficulty,
        typer.Option(
            "-d",
            "--difficulty",
            help="The difficulty to generate the sudokus with.",
        ),
    ] = Difficulty.MEDIUM,
    workers: Annotated[
        int,
        typer.Option(
            "-w",
            "--workers",
            help="Number of concurrent download workers",
        ),
    ] = cpu_count() // 2,
):
    output.touch()

    with (
        ThreadPoolExecutor(max_workers=workers) as pool,
        Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        ) as progress,
    ):
        task = progress.add_task("Downloading sudokus...", total=count)

        futures = [
            pool.submit(
                download_sudoku,
                difficulty=difficulty,
            )
            for _ in range(count)
        ]
        with output.open("a") as f:
            for future in as_completed(futures):
                try:
                    puzzle, number_of_clues = future.result()
                    progress.console.print(
                        f"[green]:heavy_check_mark: Downloaded {difficulty} sudoku with {number_of_clues} clues[/green]"
                    )
                    f.write(puzzle + "\n")
                except Exception as e:
                    progress.console.print(
                        f"[red]:warning: Download failed with {e}[/red]"
                    )
                progress.advance(task, advance=1)
            progress.update(task, visible=False)


if __name__ == "__main__":
    app()
