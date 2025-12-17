#!/bin/bash

. ./bin/env.sh

logs_dir=${OPT_LOGS_DIR}
#ce_log=${logs_dir}/create_env_$(date +"%y%m%d%H%M%S").log
dep_list=${logs_dir}/pip_list_latest.txt

activateVEnv() {
  source ${VENV_HOME}/bin/activate
}

is_env_present=$(./bin/check_env.sh)
if [ "x${is_env_present}" == "xtrue" ]; then
  echo "[$(date)] Virtual environment already present (base: ${VENV_BASE}, name: ${VENV_NAME}), no need for creation."
  echo "[$(date)] Calling the virtual environment activation script ..."
  activateVEnv
  echo "[$(date)] Done"
else
  if [ -d "${VENV_BASE}" ]; then
    echo "[$(date)] Base directory (${VENV_BASE}): found"
  else
    echo "[$(date)] Base directory (${VENV_BASE}) not found, creating base directory ..."
    mkdir "${VENV_BASE}"
    if [ -d "${VENV_BASE}" ]; then
      echo "[$(date)] Done."
    else
      echo "[$(date)] Base directory (${VENV_BASE}) could not be created. Fix the problem and retry."
      exit 1
    fi
  fi
  echo "[$(date)] Virtual environment creation ongoing (base: ${VENV_BASE}, name: ${VENV_NAME}) ..."
  rm -rf ${VENV_HOME} 2>/dev/null
  #python -m venv ${VENV_HOME} >> ${ce_log}
  python -m venv ${VENV_HOME}
  echo "[$(date)] Done. Activating the virtual environment ..."
  #activateVEnv >> ${ce_log} 2>&1
  activateVEnv
  #echo "[$(date)] Done. Installing dependencies (it will take a while) ..."
  echo "[$(date)] Done. Installing dependencies ..."
  #python -m pip install -r requirements.txt >> ${ce_log} 2>&1
  python -m pip install -r requirements.txt
  echo "[$(date)] Done. Upgrading PIP ..."
  #python -m pip install --upgrade pip >> ${ce_log} 2>&1
  python -m pip install --upgrade pip
  echo "[$(date)] Done. Collecting full dependencies list -> ${dep_list} ..."
  python -m pip list > ${dep_list} 2>&1
  echo
  #echo >> ${ce_log}
  #cat ${dep_list} >> ${ce_log}
  cat ${dep_list}
  #echo >> ${ce_log}
  echo
  #echo "[$(date)] Done (details in: ${ce_log})"
  echo "[$(date)] Done."
fi
echo "[$(date)] The environment is set."

