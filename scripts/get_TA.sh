#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./loop.sh START_YEAR END_YEAR [START_MONTH] [END_MONTH]
#
# Notes:
#   TA_202305/TA33/ORTA_2202220_20230510.xml requires fixing
#   TA_202310/TA14/ORTA_2200305_20231004.xml requires fixing
#   TA_202310/TA14/ORTA_2300643_20231019.xml requires fixing
#   TA_202402/TA14/ORTA_2400400_20240215.xml requires fixing
#   TA_202402/TA35/ORTA_2306757_20240219.xml requires fixing
#   TA_202402/TA35/ORTA_2306757_20240219.xml requires fixing
#   TA_202406/TA35/ORTA_2402939_20240607.xml requires fixing
#   TA_202407/TA14/ORTA_2401085_20240702.xml requires fixing
#   TA_202407/TA14/ORTA_2301509_20240716.xml requires fixing
#   TA_202407/TA14/ORTA_2302431_20240704.xml requires fixing
#   TA_202501/TA14/ORTA_2301045_20250115.xml requires fixing
#   TA_202503/TA14/ORTA_2500686_20250319.xml requires fixing
#   TA_202504/TA14/ORTA_2501096_20250414.xml requires fixing
#   TA_202504/TA14/ORTA_2501167_20250429.xml requires fixing
#   
#   fix:
#      find data/raw/TA_* -type f -name '*.xml' -exec sed -i '' 's|<Texte_Integral></p>|<Texte_Integral>|g' {} +
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
    wget -nc "https://opendata.justice-administrative.fr/DTA/$year/$month_padded/TA_$year$month_padded.zip" -O "data/raw/TA_$year$month_padded.zip"
    unzip -o "data/raw/TA_$year$month_padded.zip" -d "data/raw/TA_$year$month_padded"
    rm "data/raw/TA_$year$month_padded.zip"
    # Your logic here
  done

done