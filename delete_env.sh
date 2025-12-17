#!/bin/bash

. ./bin/env.sh

activateVEnv() {
  source ${VENV_HOME}/bin/activate
}

is_env_present=$(./bin/check_env.sh)
echo
echo "Virtual environment deletion shell"
if [ "x${is_env_present}" == "xtrue" ]; then
  echo "Virtual environment found (base: ${VENV_BASE}, name: ${VENV_NAME})."
  echo
  read -p "Confirm deletion? (y/n) " ans
  if [ $ans != "y" ]; then
    exit 0
  fi
  activateVEnv
  echo "[$(date)] Calling the virtual environment deactivation command ..."
  deactivate
  echo "[$(date)] Deleting the virtual environment directory ..."
  rm -rf "${VENV_HOME}"
  echo "[$(date)] Done"
  echo "[$(date)] The virtual environment has been deleted."
else
  echo "[$(date)] Virtual environment not found (base: ${VENV_BASE}, name: ${VENV_NAME})."
  if [ -d "${VENV_HOME}" ]; then
    echo "[$(date)] Deleting the virtual environment directory (found, and considered as leftover) ..."
    rm -rf "${VENV_HOME}"
    echo "[$(date)] Done. The virtual environment has been fully deleted."
    exit 0
  else
    echo "[$(date)] Exit"
  fi
fi


