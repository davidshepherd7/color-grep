import argparse
import sys
import re
from typing import List, Optional, Any, Tuple, cast
from dataclasses import dataclass
import itertools as it

from .color import sRGBColor, visual_diff

# TODO: print the colors

# TODO: validate color matching

# TODO support alpha similarity as well?

__version__ = "0.1.0"


class Args:
    base_color: sRGBColor
    files: List[str]
    distance: float
    html: Optional[str]


def parse_arguments(argv: List[str]) -> Args:
    parser = argparse.ArgumentParser()

    parser.add_argument("base_color", default=None, help="", type=sRGBColor.from_string)
    parser.add_argument("files", default=None, help="", nargs="+")
    parser.add_argument("--distance", default=0.9, type=float)
    parser.add_argument("--html", default=None)

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
    color: sRGBColor
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
                    out.append(Result(filename, i, match, color, distance))

    return out


def html_formatter(results: List[Result], base_color: sRGBColor) -> str:
    def html_color_block(color: sRGBColor) -> str:
        return f"""<span style="color: {color.to_string()}; font-size: 5em">&#9632;</span>"""

    def as_html(result: Result) -> str:
        return f"""
        <li>
            Found similar color to input: {base_color.to_string()} ->
            {html_color_block(base_color)}{html_color_block(result.color)} <- {result.color.to_string()}
             on line {result.line_number} of {result.filename}
        </li>
        """

    list_elements = "\n".join(as_html(r) for r in results)

    return f"""<!doctype html>
<html>
  <head>
    <title>Color grep output</title>
  </head>
  <body>
    <ul>
      {list_elements}
    </ul>
  </body>
</html>
"""


def main(argv: List[str]) -> int:
    args = parse_arguments(argv)

    results = list(
        it.chain(*[process_file(f, args.base_color, args.distance) for f in args.files])
    )

    for r in results:
        print(f"{r.filename}:{r.line_number} Match {r.matched_text}")

    if args.html is not None:
        if len(results) > 0:
            with open(args.html, "w") as f:
                f.write(html_formatter(results, args.base_color))
            print(f"Wrote output to file {args.html}", file=sys.stderr)
        else:
            # TODO: maybe write just a placeholder instead?
            print("No results, not writing html file", file=sys.stderr)

    return 0
