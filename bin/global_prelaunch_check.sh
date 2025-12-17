#!/bin/bash

. ./bin/env.sh

if [ "x$(./bin/check_env.sh)" != "xtrue" ]; then
  echo "[$(date)] ERROR. Missing environment. The optimizer cannot be launched."
  exit 1
fi
. ${VENV_HOME}/bin/activate
echo
echo "[$(date)] Python requirements:"
cat requirements.txt
echo
echo "[$(date)] Python dependencies actually found in the environment:"
./bin/print_pyt_env_info.sh
if [ "x$(./bin/check_reqs.sh)" != "xtrue" ]; then
  echo
  echo "[$(date)] ERROR. Python requirements seem not entirely met. Check your environment (command: ${VENV_HOME}/bin/python -m pip install --dry-run -r requirements.txt), make the needed amendments (by uninstalling/installing/upgrading dependencies, or by re-creating the venv from scratch)."
  exit 1
fi
if [ ! -d "${CSS_PRJ_DIR}" ]; then
  echo
  echo "[$(date)] ERROR. Cosmic Shield Simulator NOT FOUND where expected (${CSS_PRJ_DIR})"
  exit 1
fi
echo

