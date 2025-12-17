import subprocess
from logging_utils import init_logger, format_iter_log

from css_shield import CssShield
from kpis_utils import KPIHolder
from geom_utils import create_geometry_conf, get_geom_config
from simulator_wrap import run_simulation
from constraint_utils import check_constraints_pre, check_constraints_post

# -------------------------------------
# Objective
# -------------------------------------

def objective(params, inParamsHolder, search_sp_bldr, materials_set, constr_par, objf_evaluator, trg_evaluator):
    pn_value = inParamsHolder.get("penalization_value")
    sim_script = inParamsHolder.get("simulation_script")
    geom_trg_dir = inParamsHolder.get("geom_config_files_dir")
    config_templ_data, common_layer_data = get_geom_config(inParamsHolder.get("geom_config_template"), inParamsHolder.get("layer_conf"))
    outdata_dir = inParamsHolder.get("optimizer_out_dir")
    cf_factor = inParamsHolder.get("stiffness_cf_factor")
    logger = init_logger()
    logger.info("[driver] Iteration (objective function evaluation) BEGIN")
    #print("\n\nin objective: " + str(params) + "\n\n")

    checkConstrPre = None
    sim_id, kpis = None, None
    checkConstrPost = None
    obj_fun = None
    targetMet = None

    cShield = CssShield()
    layers_data, repair_fun_warnings = search_sp_bldr.getLayersData(params)
    num_repair_fun_warn = len(repair_fun_warnings or [])

    #Warnings about violations occurred due to repair functions actions (eg trimming, etc.)
    for w in repair_fun_warnings:
        logger.warning(f"[driver] Repair function warning: {w}")
    cShield.init(layers_data, materials_set, cf_factor)
    #layers_desc = cShield.getLayersDesc()

    checkConstrPre = check_constraints_pre(cShield, constr_par.getPRE())
    if not checkConstrPre:
        logger.info(format_iter_log(sim_id, cShield, num_repair_fun_warn, checkConstrPre, None, None, None, None, None))
        return pn_value

    try:
        sim_id, kpis = run_simulation(cShield, geom_trg_dir, config_templ_data, common_layer_data, sim_script, outdata_dir, objf_evaluator, trg_evaluator)
        logger.info(f"[driver][" + sim_id + "] KPIs retrieved after simulation: " + kpis.toString())
    except subprocess.CalledProcessError as e:
        logger.error(f"[driver] Simulation failed. CalledProcessError: {e}")
        logger.info(format_iter_log(sim_id, cShield, num_repair_fun_warn,  checkConstrPre, checkConstrPost, None, None, None, f"{e}"))
        return pn_value
    except Exception as ge:
        logger.error(f"[driver] Simulation failed. Generic error: {ge}")
        logger.info(format_iter_log(sim_id, cShield, num_repair_fun_warn, checkConstrPre, checkConstrPost, None, None, None, f"{ge}"))
        return pn_value

    checkConstrPost = check_constraints_post(cShield, kpis, constr_par.getPOST())
    if not checkConstrPost:
        logger.info(format_iter_log(sim_id, cShield, num_repair_fun_warn, checkConstrPre, checkConstrPost, None, None, kpis.toString(), None))
        return pn_value

    #Eval objective function
    obj_fun = kpis.evalObjFunction(cShield)

    # Eval if target is met
    targetMet = kpis.targetIsMet()
    logger.info(format_iter_log(sim_id, cShield, num_repair_fun_warn, checkConstrPre, checkConstrPost, targetMet, obj_fun, kpis.toString(), None))
    if (targetMet):
        # Stop condition: target is met
        logger.info("[driver][" + sim_id + "] Target met! Exit.")
        exit(0)

    return (obj_fun)

