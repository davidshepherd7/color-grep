import argparse
import sys
import re
from typing import List, Optional, Any, Tuple, cast
from dataclasses import dataclass
import itertools as it

from .color import sRGBColor, visual_diff

# TODO: Multiple base colors

# TODO: validate color matching

# TODO: column numbers?

# TODO support alpha similarity as well?

# TODO: match all colors in project against all?

# TODO: non-rgb color schemes?

# TODO: include named colors? html? android?


__version__ = "0.1.0"


class Args:
    files: List[str]
    color: List[sRGBColor]
    distance: float
    html: Optional[str]
    exclude_identical: bool


def parse_arguments(argv: List[str]) -> Args:
    parser = argparse.ArgumentParser()

    parser.add_argument("files", default=None, help="", nargs="+")
    parser.add_argument("--color", help="", type=sRGBColor.from_string, action="append")
    parser.add_argument("--distance", default=0.9, type=float)
    parser.add_argument("--html", default=None)
    parser.add_argument("--exclude-identical", default=False, action="store_true")

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
    base_color: sRGBColor
    distance: float


def process_file(
    filename: str,
    base_colors: List[sRGBColor],
    max_distance: float,
    exclude_identical: bool,
) -> List[Result]:
    out: List[Result] = []
    with open(filename) as f:
        for i, line in enumerate(f.readlines(), start=1):
            for match in re.findall(rgb_regex, line):
                match_color = sRGBColor.from_string(match)
                for base_color in base_colors:
                    distance = visual_diff(
                        match_color.to_cielab(), base_color.to_cielab()
                    )
                    excluded_because_identical = (
                        exclude_identical and match_color == base_color
                    )
                    if distance < max_distance and not excluded_because_identical:
                        out.append(
                            Result(
                                filename=filename,
                                line_number=i,
                                matched_text=match,
                                color=match_color,
                                base_color=base_color,
                                distance=distance,
                            )
                        )

    return out


def html_formatter(results: List[Result]) -> str:
    def html_color_block(color: sRGBColor) -> str:
        return f"""<span style="color: {color.to_string()}; font-size: 5em">&#9632;</span>"""

    def as_html(result: Result) -> str:
        return f"""
        <li>
            Found color {result.distance} from input: {result.base_color.to_string()} ->
            {html_color_block(result.base_color)}{html_color_block(result.color)} <- {result.color.to_string()}
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
        it.chain(
            *[
                process_file(f, args.color, args.distance, args.exclude_identical)
                for f in args.files
            ]
        )
    )

    for r in results:
        print(
            f"{r.filename}:{r.line_number} Match {r.matched_text} against {r.base_color.to_string()}, distance {r.distance}"
        )

    if args.html is not None:
        if len(results) > 0:
            with open(args.html, "w") as f:
                f.write(html_formatter(results))
            print(f"Wrote output to file {args.html}", file=sys.stderr)
        else:
            # TODO: maybe write just a placeholder instead?
            print("No results, not writing html file", file=sys.stderr)

    return 0
