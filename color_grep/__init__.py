import argparse
import re
from typing import List, Optional, Any, Tuple, cast
from dataclasses import dataclass
import itertools as it

from .color import sRGBColor, visual_diff

# TODO support alpha similarity as well?

__version__ = "0.1.0"


class Args(argparse.Namespace):
    base_color: sRGBColor
    files: List[str]
    distance: float


def parse_arguments(argv: List[str]) -> Args:
    parser = argparse.ArgumentParser()

    parser.add_argument("base_color", default=None, help="", type=sRGBColor.from_string)
    parser.add_argument("files", default=None, help="", nargs="*")
    parser.add_argument("--distance", default=0.9, type=float)

    args = parser.parse_args(argv)
    return cast(Args, args)


# Ascii only probably gets us some perf, TODO check this
rgb_regex = re.compile("#[0-9abcdef]{6}", re.IGNORECASE | re.ASCII)


@dataclass(frozen=True)
class Result:
    filename: str
    line_number: int
    # column_number: int
    matched_text: str
    distance: float


def process_file(
    filename: str, base_color: sRGBColor, max_distance: float
) -> List[Result]:
    out: List[Result] = []
    with open(filename) as f:
        for i, line in enumerate(f.readlines(), start=1):
            for match in re.findall(rgb_regex, line):
                color = sRGBColor.from_string(match)
                distance = visual_diff(color.to_cielab(), base_color.to_cielab())
                if distance < max_distance:
                    out.append(Result(filename, i, match, distance))

    return out


def main(argv: List[str]) -> int:
    args = parse_arguments(argv)

    results = it.chain(
        *[process_file(f, args.base_color, args.distance) for f in args.files]
    )

    for r in results:
        print(f"{r.filename}:{r.line_number} Match {r.matched_text}")

    return 0
