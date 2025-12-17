#!/bin/bash

. ./bin/env.sh

echo
echo "[$(date)] Optimizer temporary files cleanup shell"
echo "[$(date)] Deleting outputs .."
rm -rf ${OPT_OUT_DIR}/r*
echo "[$(date)] Deleting logs .."
rm ${OPT_LOGS_DIR}/*
echo "[$(date)] Deleting history files .."
rm ${OPT_STATE_DIR}/*

if [ "x${VENV_IS_DEDICATED}" == "xtrue" ]; then
  echo "[$(date)] VENV (${VENV_HOME}) is dedicated and is being removed"
  rm -rf ${VENV_HOME}
else
  echo "[$(date)] VENV (${VENV_HOME}) is not dedicated and is not being removed"
fi

echo "[$(date)] Deleting pycache files .."
rm -rf src/__pycache__
rm -rf src/util/__pycache__
rm -rf src/searchsp_impl/__pycache__
rm -rf src/objfun_impl/__pycache__
rm -rf src/target_impl/__pycache__

echo "[$(date)] Deleting temporary geometry configuration files .."
rm ./config/optim/geometry_*.json

echo "[$(date)] Cleanup completed"
