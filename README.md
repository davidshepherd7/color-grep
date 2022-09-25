# Color-grep

Search your code for colors which are visually similar to an input.


Typical usage is something like:

```
git ls-files | xargs ~/bin/color-grep --distance 2 --html output.html --color "#0D6C3A"
```

## Installation

Clone the project, run the `color-grep` file in the root of the repo.


## Status

Just a toy project, but might do what you want!

Limitations:

* Doesn't support anything other than sRGB right now, e.g. doesn't know what
  `color: red;` in html means or how to understand ios's json format for colors.
* The color matching uses the CIE Delta-E 2000 algorithm, but the distance
  results for greys look a bit odd so there might be something wrong. I am not a
  color expert. In particular it's possible that I picked the wrong illuminants
  for computer screens.
* Alpha channel is ignored.
* No support for an equivalent of grep's `-r` flag, use `git ls-files | xargs
  color-grep` or similar instead.
* Very little automated testing.
* No pip package etc.
