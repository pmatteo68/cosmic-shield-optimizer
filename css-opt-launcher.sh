#!/bin/bash

. ./bin/env.sh

./bin/global_prelaunch_check.sh
if [ $? -eq 1 ]; then
  exit 1
fi

curr_tstamp=$(date +"%y%m%d%H%M%S")

opt_log=${OPT_LOGS_DIR}/css-opt-${curr_tstamp}.log

export CSS_OPT_STOPFILE=./css-opt-stop-${curr_tstamp}.txt

#nohup ./css-optimizer-dummy.sh > ${opt_log} 2>&1 &
nohup ./css-optimizer.sh > ${opt_log} 2>&1 &

ppid=$!
echo "[$(date)] CSS Optimizer process launched in background (pid: ${ppid})"
echo
echo "Check progress with:"
echo "tail -f ${opt_log} | grep opttrace"
echo
echo "Or also, if you want full detail:"
echo "tail -f ${opt_log}"
echo
echo "Commands available for early termination:"
echo "./kill_optimizer.sh ${ppid} (note: this is neverending, and it can be safely interrupted with CTRL+C)"
echo "kill ${ppid} (NOT 'kill -9 ..', just 'kill')"
echo "touch ${CSS_OPT_STOPFILE}"
echo

