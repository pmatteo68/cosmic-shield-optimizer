#!/bin/bash

. ./bin/env.sh

if [ "x${CSS_OPT_STOPFILE}" == "x" ] 2>/dev/null; then
  echo "[$(date)] ERROR. This script is not designed to be invoked directly."
  exit 1
fi

. ${VENV_HOME}/bin/activate

############## Editable section: BEGIN ############

#Log levels for the optimizer: DEBUG, INFO, WARNING, ERROR, CRITICAL
export CSS_OPT_LOG_LEVEL=INFO

#[requires CSS 5.1.2 or sup] If CSS_OPT_SAV_STEPDATA is set in this script, it will supersede the correspondent setting in the CSS launch script.
#It is best to set it to OFF, so to avoid huge disk size usage.
export CSS_OPT_SAV_STEPDATA=OFF

############## Editable section: END ##############

# Allows consecutive layers to have same material.
# Applies only from 1.0.6 onwards, and only with certain search space definition builders. Ref. README for details.
# Do NOT modify if not entirely sure of what you are doing.
export CSS_OPT_ADJL_SAME_MAT=OFF

# Enables shield trimming (by thickness).
# Applies only from 1.0.6 onwards, and only with certain search space definition builders. Ref. README for details.
# It is recommended to keep this enabled as it makes sure that no shield can be generated with total thickness exceeding max value.
export CSS_OPT_SHIELD_TRIMMING=ON

# Enables shield trimming (by weight).
# Applies only from 1.0.7 onwards, and only with certain search space definition builders. Ref. README for details.
# It is recommended to keep this enabled as it makes sure that no shield can be generated with total weight exceeding max value.
export CSS_OPT_SHIELD_WGT_TRIMMING=ON

# "-mr", "--max-runs", type=int, help="Max number of simulations", default=1000)
# "-sb", "--searchsp-builder", type=str, help="Search space builder class", default="searchsp_adv250814.SearchSpaceBuilderAdv250814"),
#         full list, from newest to oldest:
#             - searchsp_adv250814.SearchSpaceBuilderAdv250814 (same as base250801, plus shield trimming AND no matching material in two adjacent layers)
#             - searchsp_adv250813.SearchSpaceBuilderAdv250813 (same as base250801, plus shield trimming, it is a work-in-progress created during the works for v. 1.0.6)
#             - searchsp_base250801.SearchSpaceBuilderBase250801 (first ever built, same as per versions 1.0.0-1.0.5)
# "-of", "--objfun-evaluator", type=str, help="Object function evaluation class", default="objfun_base250801.ObjFEval_Base250801")
#          full list, from newest to oldest:
#             - objfun_adv250817fms.ObjFEval_AdvFMS250817 (F. M. Soccorsi, Aug. 17, 2025)
#             - objfun_base250801.ObjFEval_Base250801  (first ever built, same as per versions 1.0.0-1.0.7, simple sum)
# "-op", "--objfun-params", type=str, help="Object function evaluation parameters", default=None)
# "-ta", "--target-evaluator", type=str, help="Target evaluator class", default="trgeval_base250801.TargetEval_Base250801")
#          full list, from newest to oldest:
#             - trgeval_base250801.TargetEval_Base250801 (first ever built, same as per versions 1.0.0-1.0.8)
####### REMOVED IN 1.0.4, now it is in a json file. "-ip", "--initial-points", type=int, help="Number of random initial points", default=200) -   -ip 10 \
# "-hf", "--history-file", type=str, help="Attempts history file path", default="./state/css_optimizer_state.pkl")
# "-ee", "--energy-efficiency", type=float, help="Target energy efficiency", default=0.9)
# "-pe", "--protection-efficiency", type=float, help="Target protection efficiency", default=0.9)
# "-pv", "--penalize-value", type=float, help="Value for penalization", default=1e6)
# "-sc", "--sim-script", type=str, help="Simulator launch script path", default="./css_wrap.sh")
# -----------------"-kf", "--kpis-file", type=str, help="KPIs file path", default="./global_kpis.csv")
# "-or", "--outputdata-root", type=str, help="Output data root", default="./out")
# "-ml", "--materials-list", type=str, help="Materials list file", default="./config/materials.txt")
# "-md", "--materials-database", type=str, help="Materials database file", default=None)
# "-gd", "--geom-directory", type=str, help="Target directory for geometry configuration files", default="./config/optim")
#  -gd ./config/optim \
# "-gt", "--geom-template", type=str, help="Geometry configuration template path", default="./config/geometry_template.json")
# "-lc", "--layer-config", type=str, help="Layer common configurations path", default="./config/layer_config.json")
# "-lm", "--min-layers", type=int, help="Min number of layers", default=1)
# "-lx", "--max-layers", type=int, help="Max number of layers", default=10)
# "-tm", "--min-thickness", type=float, help="Min layer thickness (mm)", default=1.0)
# "-tx", "--max-thickness", type=float, help="Max layer thickness (mm)", default=10.0)
# "-nt", "--min-tot-thickness", type=float, help="Min total thickness (mm)", default=0.0) new in 1.0.5
# "-mt", "--max-tot-thickness", type=float, help="Max total thickness (mm)", default=30.0)
#    parser.add_argument("-sm", "--min-stiffness", type=float, help="Min total stiffness", default=0.0)
#    parser.add_argument("-sx", "--max-stiffness", type=float, help="Max total stiffness", default=100.0)
# "-mw", "--max-tot-weight", type=float, help="Max total weight (kg/m2)", default=20.0)
# "-mc", "--max-tco", type=int, help="Max TCO (Total Cost of Ownership)", default=10)
# "-hs", "--history-slice", type=str, help="History slicing directive ('a:b' -> from a-th element, length b, 'a:'  -> from a-th element to end, ':b'  -> first b elements, '_:b'  -> last b elements)", default=None)
# "-oc", "--optimizer-config", type=str, help="Core optimization engine configuration file", default="./config/optimizer_conf.json")
# "-x0", "--x0-file", type=str, help="Initial shield configuration", default=None)
#  -x0 ./config/init_shield_x0.json \
# ""-xr", "--rnd-x0-fallback", action="store_true", help="if X0 could not be loaded in any way and this flag is set, a custom random X0 will be generated (instead of letting the gp_minimized do this for you. Additional details about why this could be best can be found in the readme)")
# "-sf", "--stop-file", type=str, help="Stop file path", default=None)
# "-vo", "--verbose-optimization", action="store_true", help="Enable verbose optimization logging")
#   -kf ./global_kpis.csv \
# -sb searchsp_base250801.SearchSpaceBuilderBase250801 searchsp_adv250813.SearchSpaceBuilderAdv250813 searchsp_adv250814.SearchSpaceBuilderAdv250814

# objfun_base250801.ObjFEval_Base250801 objfun_adv250817fms.ObjFEval_AdvFMS250817
# trgeval_base250801.TargetEval_Base250801
#exec best so the process does not proliferate another pid
exec python src/shield_optimizer.py \
  --pr max_runs 1000 \
  --pr searchspace_builder searchsp_adv250814.SearchSpaceBuilderAdv250814 \
  --pr objfun_evaluator objfun_base250801.ObjFEval_Base250801 \
  --pr objfun_config ${OPT_CONFIG_DIR}/objfun_params.json \
  --pr target_evaluator trgeval_base250801.TargetEval_Base250801 \
  --pr history_file ${OPT_STATE_DIR}/dummy_optimizer_state.pkl \
  --pr history_slice _:5 \
  --pr target_energy_eff 0.9 \
  --pr target_protection_eff 0.9 \
  --pr penalization_value 1e6 \
  --pr simulation_script ./dummy_simulation.sh \
  --pr optimizer_out_dir ${OPT_OUT_DIR} \
  --pr materials_database ${OPT_CONFIG_DIR}/materials_db.json \
  --pr materials_list ${OPT_CONFIG_DIR}/materials.txt \
  --pr geom_config_files_dir ${OPT_CONFIG_DIR}/optim \
  --pr geom_config_template ${OPT_CONFIG_DIR}/geometry_template.json \
  --pr layer_conf ${OPT_CONFIG_DIR}/layer_config.json \
  --pr optimizer_conf  ${OPT_CONFIG_DIR}/optimizer_conf.json \
  --pr min_layers 1 \
  --pr max_layers 5 \
  --pr min_layer_thickness 1.0 \
  --pr max_layer_thickness 10.0 \
  --pr min_shield_stiffness 0.0 \
  --pr max_shield_stiffness 100.0 \
  --pr stiffness_cf_factor 0.9 \
  --pr min_shield_thickness 0.0 \
  --pr max_shield_thickness 30.0 \
  --pr max_shield_weight 20.0 \
  --pr max_tco 10.0 \
  --pr init_x0 ${OPT_CONFIG_DIR}/init_shield_x0.json \
  --pr rnd_x0_fallback true \
  --pr stop_file ${CSS_OPT_STOPFILE} \
  --pr verbose_optimization false

