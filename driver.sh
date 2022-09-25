#!/bin/bash -eu

set -o pipefail

git ls-files -z |\
    grep --null-data '.*\.xml\|.*\.kt\|.*\.swift\|.*\.json\|.*\.css\|.*\.html' |\
    xargs --null \
          ~/code/color-grep/color-grep --distance 5 --exclude-identical --html "color-grep.html" \
          --color "#E1F5FE" \
          --color "#C3ECFF" \
          --color "#89E2FF" \
          --color "#5CD8FF" \
          --color "#1DC8FF" \
          --color "#00C1FF" \
          --color "#1FABE8" \
          --color "#1194CC" \
          --color "#0E5C9A" \
          --color "#004476" \
          --color "#F1F1F1" \
          --color "#E5E5E5" \
          --color "#D2D2D2" \
          --color "#B6B6B6" \
          --color "#9A9A9A" \
          --color "#7A7A7A" \
          --color "#555555" \
          --color "#353535" \
          --color "#1C1C1C" \
          --color "#D9D9FF" \
          --color "#C6C6FF" \
          --color "#C6C6FF" \
          --color "#8C8EFF" \
          --color "#6C6EF2" \
          --color "#5B5CD9" \
          --color "#4345CD" \
          --color "#24259B" \
          --color "#00016B" \
          --color "#C1CEFD" \
          --color "#829EFF" \
          --color "#5A75FF" \
          --color "#555965" \
          --color "#4144FF" \
          --color "#4B41DD" \
          --color "#2207C7" \
          --color "#180399" \
          --color "#FDE4E2" \
          --color "#FDCDCB" \
          --color "#FBA29D" \
          --color "#ED463F" \
          --color "#DF0000" \
          --color "#B22520" \
          --color "#960A05" \
          --color "#730400" \
          --color "#540000" \
          --color "#C7FABF" \
          --color "#C8EAC3" \
          --color "#9DDD93" \
          --color "#49B937" \
          --color "#249C71" \
          --color "#128C61" \
          --color "#00784E" \
          --color "#005B3B" \
          --color "#003D27" \
          --color "#FFF8E1" \
          --color "#FFEAAD" \
          --color "#FFD863" \
          --color "#50B08D" \
          --color "#F9A31A" \
          --color "#128C61" \
          --color "#FF6F00" \
          --color "#F16A21" \
          --color "#F16A21" \
          --color "#FAFAFA" \
          --color "#F3F4F6" \

          # --color "#90071" \
