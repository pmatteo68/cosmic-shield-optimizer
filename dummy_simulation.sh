#!/bin/bash

. ./bin/env.sh
#. /${VENV_HOME}/bin/activate

echo "(INSIDE DUMMY SIM) Simulation command: $(basename "$0") $@"
echo "(INSIDE DUMMY SIM) Simulation command: $(basename "$0") $@" >> ${OPT_LOGS_DIR}/sims-dummy.log
echo "(INSIDE DUMMY SIM) Processing ..."

SIM_ID=$1

SIM_OUT_ROOT="${OPT_OUT_DIR}/r${SIM_ID}"
mkdir -p "${SIM_OUT_ROOT}"
TARGET_KPIS_FILE="${SIM_OUT_ROOT}/glob_kpis_${SIM_ID}.csv"

echo "[opttrace][dummy] GlobThickness;GlobNormWeight;EnergyEfficiency;ProtectionEfficiency: 270.000000;1870.400000;0.505040;0.665954"
echo "GlobThickness;GlobNormWeight;EnergyEfficiency;ProtectionEfficiency" > "${TARGET_KPIS_FILE}"
echo "270.000000;1870.400000;0.505040;0.665954" >> "${TARGET_KPIS_FILE}"

sleep 2

echo "(INSIDE DUMMY SIM) Results created: ${TARGET_KPIS_FILE}"
echo "(INSIDE DUMMY SIM) Processing complete."

