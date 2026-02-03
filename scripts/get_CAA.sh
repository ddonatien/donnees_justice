#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./loop.sh START_YEAR END_YEAR [START_MONTH] [END_MONTH]
#
# Defaults:
#   START_MONTH = 1
#   END_MONTH   = 12

START_YEAR="${1:?Start year required (YYYY)}"
END_YEAR="${2:?End year required (YYYY)}"
START_MONTH="${3:-1}"
END_MONTH="${4:-12}"

# ---- Validation ----

# Year format
[[ "$START_YEAR" =~ ^[0-9]{4}$ ]] || { echo "Invalid START_YEAR"; exit 1; }
[[ "$END_YEAR"   =~ ^[0-9]{4}$ ]] || { echo "Invalid END_YEAR"; exit 1; }

# Month format
(( START_MONTH >= 1 && START_MONTH <= 12 )) || { echo "Invalid START_MONTH"; exit 1; }
(( END_MONTH   >= 1 && END_MONTH   <= 12 )) || { echo "Invalid END_MONTH"; exit 1; }

(( START_YEAR <= END_YEAR )) || { echo "START_YEAR must be <= END_YEAR"; exit 1; }

# ---- Loops ----

for (( year=START_YEAR; year<=END_YEAR; year++ )); do

  # Determine month range for this year
  if (( year == START_YEAR )); then
    month_start=$START_MONTH
  else
    month_start=1
  fi

  if (( year == END_YEAR )); then
    month_end=$END_MONTH
  else
    month_end=12
  fi

  for (( month=month_start; month<=month_end; month++ )); do
    printf "Downloading...: " "%04d-%02d\n" "$year" "$month"
    month_padded=$(printf "%02d" "$month")
    wget -nc "https://opendata.justice-administrative.fr/DCA/$year/$month_padded/CAA_$year$month_padded.zip" -O "data/raw/CAA_$year$month_padded.zip"
    unzip -o "data/raw/CAA_$year$month_padded.zip" -d "data/raw/CAA_$year$month_padded"
    rm "data/raw/CAA_$year$month_padded.zip"
    # Your logic here
  done

done