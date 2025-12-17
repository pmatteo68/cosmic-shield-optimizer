#!/bin/bash

#. ./bin/env-cssim.sh

target_dir=~
echo "Packing project ..."
cur_proj_dir=$(basename "$(pwd | sed 's/\/proj//g')")
echo "Project dir is: ${cur_proj_dir}"
cd ../../../
arc_filename=css-opt-${cur_proj_dir}.tar.gz
arc_fullpath=${target_dir}/${arc_filename}
if [ -f "${arc_fullpath}" ]; then
  echo "ERROR: file ${arc_fullpath} exists already: cannot overwrite"
  exit 1
else
  tar czf ${arc_fullpath} projects/css-optimizer/${cur_proj_dir}
  if [ -f "${arc_fullpath}" ]; then
    echo "The ${arc_fullpath} file has been created successfully"
    ls -lart ${arc_fullpath}
  else
    echo "ERROR: ${arc_fullpath} creation command succeeded, but the file seems not being there"
    exit 1
  fi
fi

cd - >/dev/null 2>&1

