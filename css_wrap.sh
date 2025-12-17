#!/bin/bash

. ./bin/env.sh
#. ${VENV_HOME}/bin/activate

############## Editable section: BEGIN ############

#[requires CSS 5.1.2 or sup] If CSS_OPT_SAV_STEPDATA is set in this script, it will supersede the correspondent setting in the CSS launch script.
#It is best to set it to OFF, so to avoid huge disk size usage.
#export CSS_OPT_SAV_STEPDATA=OFF

############## Editable section: END ##############

#curr_tstamp=$(date +"%y%m%d%H%M%S")
css_proj_dir=${CSS_PRJ_DIR}
optim_dir=$(pwd)

sims_log_dir=${OPT_LOGS_DIR}
#sims_log=${sims_log_dir}/sims-${curr_tstamp}.log
sims_log=${sims_log_dir}/sims.log

SIM_ID=$1

echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation wrapper command: $(basename "$0") $@"
echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation wrapper command: $(basename "$0") $@" >> ${sims_log}
echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation dir.: ${css_proj_dir}"
echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation dir.: ${css_proj_dir}" >> ${sims_log}

SIM_OUT_ROOT="${CSS_OUT_DIR}/r${SIM_ID}"
#mkdir -p "${SIM_OUT_ROOT}"

if [ -d "${css_proj_dir}" ]; then
  cd "${css_proj_dir}"
  #sim_command=./run-css.sh ${CSS_MODE} ${SIM_ID}
  echo "[$(date)][SIM WRAP][${SIM_ID}] Launching simulation: ${CSS_LAUNCH_SCRIPT} ${CSS_MODE} ${SIM_ID}"
  echo "[$(date)][SIM WRAP][${SIM_ID}] Launching simulation: ${CSS_LAUNCH_SCRIPT} ${CSS_MODE} ${SIM_ID}" >> ${sims_log}
  #"${sim_command}"
  ./${CSS_LAUNCH_SCRIPT} ${CSS_MODE} ${SIM_ID}
  cd "${optim_dir}"

  target_kpis_file="${SIM_OUT_ROOT}/glob_kpis_${SIM_ID}.csv"
  if [ -f "${target_kpis_file}" ]; then
    echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation results created in: ${target_kpis_file}"
    echo "[$(date)][SIM WRAP][${SIM_ID}] Simulation results created in: ${target_kpis_file}" >> ${sims_log}
  else
    echo "[$(date)][SIM WRAP][${SIM_ID}] ERROR - RESULTS NOT FOUND (missing: ${target_kpis_file})"
    echo "[$(date)][SIM WRAP][${SIM_ID}] ERROR - RESULTS NOT FOUND (missing: ${target_kpis_file})" >> ${sims_log}
    exit 1
  fi
else
  echo "[$(date)][SIM WRAP][${SIM_ID}] ERROR - Simulator NOT FOUND (missing: ${css_proj_dir})"
  echo "[$(date)][SIM WRAP][${SIM_ID}] ERROR - Simulator NOT FOUND (missing: ${css_proj_dir})" >> ${sims_log}
  exit 1
fi
cd "${optim_dir}"

echo "[$(date)][SIM WRAP][${SIM_ID}] Processing complete."

