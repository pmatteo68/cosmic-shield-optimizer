#!/bin/bash

PYTHON_HOME=/usr/bin
PATH=${PYTHON_HOME}:${PATH}
PATH=${PYTHON_HOME}/Scripts:${PATH}

VENV_NAME=css-opt-venv
# Set to false if you want that the venv is centralized (ie used by many versions) or true (if you want that the venv is dedicated to this version)
VENV_IS_DEDICATED=false

OPT_CONFIG_DIR=./config
OPT_LOGS_DIR=./logs
OPT_OUT_DIR=./out
OPT_STATE_DIR=./state

# DEBUG, INFO, WARNING, ERROR, CRITICAL
CSS_OPT_LOG_LEVEL=INFO

CSS_ROOT_DIR=../../cosmic-shield-sim/v5.1.5-wk
CSS_PRJ_DIR=${CSS_ROOT_DIR}/proj
CSS_OUT_DIR=${CSS_PRJ_DIR}/out
CSS_CFG_OPTIM=${CSS_PRJ_DIR}/config/optim
CSS_LAUNCH_SCRIPT=run-cssim.sh

CSS_MODE=batch

if [ "x${VENV_IS_DEDICATED}" = "xtrue" ]; then
  # Best setting if you want to have a venv for each individual version
  VENV_BASE=.
else
  # If you want a centralized venv to be referenced by other (or all) versions, set this directory to any path which is external to any specific version's directory. Eg the following is fine:
  VENV_BASE=~/.py_venvs
fi
VENV_HOME=${VENV_BASE}/${VENV_NAME}

export PATH
export VENV_BASE
export VENV_NAME
export VENV_HOME
export OPT_CONFIG_DIR
export OPT_LOGS_DIR
export OPT_OUT_DIR
export OPT_STATE_DIR
export VENV_IS_DEDICATED
export CSS_OPT_LOG_LEVEL

export CSS_PRJ_DIR
export CSS_OUT_DIR
export CSS_CFG_OPTIM
export CSS_LAUNCH_SCRIPT
export CSS_MODE
