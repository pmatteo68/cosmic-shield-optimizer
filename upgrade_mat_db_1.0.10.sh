#!/bin/bash

in_file=$1

if [ "x${in_file}" == "x" ]; then
  echo
  echo "Usage:"
  echo
  echo "$0 <json filename>"
  echo
  echo "Example:"
  echo
  echo "$0 config/fileabc.json"
  echo
  exit 1
fi

file_name=$in_file
if [ -f $file_name ]; then
  ts=$(date +"%y%m%d%H%M%S")
  bkp_file_name=${file_name%.json}_OLD$ts.json
  num_to_amend=$(cat "$file_name" | jq '[.materials[] | select(has("mat_E") | not)]| length')
  echo "[$(date)] Entries to be transformed: $num_to_amend"
  if [ $num_to_amend -gt 0 ]; then
    mv "$file_name" "$bkp_file_name"
    echo "[$(date)] Transforming ..."
    cat "$bkp_file_name" | jq '.materials |= map(if has("mat_E") then . else . + {mat_E: 50.0} end)' > "$file_name"
    echo "[$(date)] Done. $file_name is now upgraded. Old file has been saved to: $bkp_file_name"
  else
    echo "[$(date)] Nothing to do. Exit"
  fi
else
  echo "[$(date)] The specified file was not found"
fi

