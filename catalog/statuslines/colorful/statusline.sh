#!/usr/bin/env bash
# Claude Code status line: model · cwd · 5h% (Xh Ym) · 7d% (Xd Yh)
#
# Reads the JSON stdin envelope documented at
# https://code.claude.com/docs/en/statusline and emits a single coloured line.
# rate_limits.{five_hour,seven_day}.{used_percentage,resets_at} are only
# populated for Claude.ai Pro/Max subscribers after the first API response of
# a session — both percentage and reset time render as "—" until they appear.

set -u
input=$(cat)

# Muted greys + accent for usage; keep it readable on both light and dark.
GREY="\033[38;5;245m"
DIM="\033[38;5;240m"
ACCENT="\033[38;5;39m"
RESET="\033[0m"

now=$(date +%s)

model=$(printf '%s' "$input" | jq -r '.model.display_name // "Claude"')

# CWD → ~/... when under $HOME.
cwd=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
if [ -n "$cwd" ]; then
  case "$cwd" in
    "$HOME") cwd="~" ;;
    "$HOME"/*) cwd="~${cwd#$HOME}" ;;
  esac
else
  cwd=""
fi

# rate_limits.{five_hour,seven_day}.used_percentage → integer% or em-dash.
fmt_pct() {
  v=$1
  if [ -z "$v" ] || [ "$v" = "null" ]; then
    printf '—'
  else
    printf '%.0f%%' "$v"
  fi
}

# Format seconds-until as the largest two units (e.g. 2d 3h, 4h 12m, 8m).
# Returns empty string if the reset is missing, in the past, or unparseable.
fmt_reset() {
  ts=$1
  [ -z "$ts" ] || [ "$ts" = "null" ] && return
  case "$ts" in
    ''|*[!0-9]*) return ;;        # non-numeric → give up
  esac
  delta=$(( ts - now ))
  [ "$delta" -le 0 ] && return     # window already rolled — wait for next event
  d=$(( delta / 86400 ))
  h=$(( (delta % 86400) / 3600 ))
  m=$(( (delta % 3600)  / 60   ))
  if [ "$d" -gt 0 ]; then
    printf '%dd %dh' "$d" "$h"
  elif [ "$h" -gt 0 ]; then
    printf '%dh %dm' "$h" "$m"
  elif [ "$m" -gt 0 ]; then
    printf '%dm' "$m"
  else
    printf '<1m'
  fi
}

fivem=$(printf '%s' "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven=$(printf '%s' "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
fivem_at=$(printf '%s' "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
seven_at=$(printf '%s' "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

fivem_left=$(fmt_reset "$fivem_at")
seven_left=$(fmt_reset "$seven_at")

# Compose "5h:" and "7d:" segments: percentage, then a dim "·Xh Ym" suffix
# if a reset time is available. Reset suffix uses DIM so the eye lands on
# the percentage first.
fivem_seg="${GREY}5h:${RESET} $(fmt_pct "$fivem")"
[ -n "$fivem_left" ] && fivem_seg="${fivem_seg} ${DIM}·${fivem_left}${RESET}"
seven_seg="${GREY}7d:${RESET} $(fmt_pct "$seven")"
[ -n "$seven_left" ] && seven_seg="${seven_seg} ${DIM}·${seven_left}${RESET}"

# Assemble.
left="${ACCENT}${model}${RESET}"
[ -n "$cwd" ] && left="${left} ${DIM}${cwd}${RESET}"
right="${fivem_seg}  ${seven_seg}"

printf '%b  %b\n' "$left" "$right"
