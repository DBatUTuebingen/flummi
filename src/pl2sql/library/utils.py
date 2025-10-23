from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

from collections.abc import Iterator, Iterable
from functools import reduce
from itertools import groupby as _groupby
from typing import Callable


__all__ = ("union", "indent1", "groupby", "unzip", "partition", "zipwith")


def union[T](sets: Iterator[Iterable[T]]) -> set[T]:
    return reduce(lambda a, b: a | b, map(set, sets), set[T]())


def indent1(lines: str, prefix: str):
    out = ""
    for i, line in enumerate(lines.splitlines(keepends=True)):
        if i > 0:
            out += prefix + line
        else:
            out += line
    return out


def groupby[T, K: SupportsRichComparison](
    things: Iterator[T], key: Callable[[T], K]
) -> Iterable[tuple[K, Iterable[T]]]:
    return _groupby(
        sorted(
            things,
            key=key,
        ),
        key=key,
    )


def unzip[L, R](
    zipped: Iterable[tuple[L, R]],
) -> tuple[Iterable[L], Iterable[R]]:
    lefts, rights = list[L](), list[R]()

    for left, right in zipped:
        lefts.append(left)
        rights.append(right)

    return lefts, rights


def partition[T](
    things: Iterable[T], choice: Callable[[T], bool]
) -> tuple[Iterable[T], Iterable[T]]:
    truthy, falsey = list[T](), list[T]()

    for thing in things:
        if choice(thing):
            truthy.append(thing)
        else:
            falsey.append(thing)

    return truthy, falsey


def zipwith[L, R, T](
    func: Callable[[L, R], T], lefts: Iterable[L], rights: Iterable[R]
) -> Iterable[T]:
    for left, right in zip(lefts, rights):
        yield func(left, right)
