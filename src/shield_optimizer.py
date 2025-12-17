import sys
import signal

from datetime import datetime
from skopt import gp_minimize
#fxrom skopt.space import Space
from functools import partial

py_root='./src'
py_util=py_root + '/util'
py_ssp_impl=py_root + '/searchsp_impl'
py_ofe_impl=py_root + '/objfun_impl'
py_trg_impl=py_root + '/target_impl'
sys.path.append(py_root)
sys.path.append(py_util)
sys.path.append(py_ssp_impl)
sys.path.append(py_ofe_impl)
sys.path.append(py_trg_impl)

from cmdline_parsing import ParametersHolder
from misc_util import get_elapsed_time, load_params_generic
from logging_utils import init_logger
from interrupt_mgr import IRQManager
from kpis_utils import KPITargets
from constraint_utils import ConstraintParams
from history_mgr import HistoryManager, process_retrieved_history
from materials_set import MaterialsSet
from materials_db import MaterialsDatabase
from optimizer_config import OptimizerConfig
from obj_factory import CO_ObjectFactory
from feasibility import is_problem_well_posed
from sw_metadata import SoftwareMetadata
from objfunction_wrap import objective
from post_simulation import post_sim_logic

from searchsp_adv250814 import SearchSpaceBuilderAdv250814
from objfun_base250801 import ObjFEval_Base250801
from trgeval_base250801 import TargetEval_Base250801

# --------------------------------------------------
# Harnessing for graceful exit upon SIGTERM/SIGINT
# --------------------------------------------------
def graceful_exit(signum, frame):
    IRQManager.setKillSignalDetected()

signal.signal(signal.SIGTERM, graceful_exit)
signal.signal(signal.SIGINT, graceful_exit)

# -------------------------------------
# Program entry point: main
# -------------------------------------
def main(args=None):
    logger = init_logger()
    swMetaData = SoftwareMetadata()
    sw_name = swMetaData.getSWName()
    paramsHolder = ParametersHolder(sw_name, args, "--pr")

    HISTORY_FILE = paramsHolder.get("history_file")
    HISTORY_SLICING_DIR = paramsHolder.get("history_slice")
    MATERIALS_FILE = paramsHolder.get("materials_list")
    MATERIALS_DB_FILE = paramsHolder.get("materials_database")

    # -------------------------------------
    # CONFIG
    # -------------------------------------

    MAX_RUNS = paramsHolder.get("max_runs")
    OPTIM_VERBOSE = (paramsHolder.get("verbose_optimization", "false") == "true")

    OPTIM_CFG_FILE = paramsHolder.get("optimizer_conf")
    STOP_FILE = paramsHolder.get("stop_file")
    SSB_MODULE, SSB_CLASSNAME = paramsHolder.get("searchspace_builder").split(".", 1)
    OFE_MODULE, OFE_CLASSNAME = paramsHolder.get("objfun_evaluator").split(".", 1)
    TRG_MODULE, TRG_CLASSNAME = paramsHolder.get("target_evaluator").split(".", 1)
    OBJFUN_PARAMS_FILE = paramsHolder.get("objfun_config")

    logger.info("[driver] " + sw_name + ", v. " + swMetaData.getSWVersion())
    paramsHolder.dump(logger)

    optimizerConf = OptimizerConfig()
    optimizerConf.init(OPTIM_CFG_FILE)
    INITIAL_POINTS = optimizerConf.getParam("n_initial_points")

    irqMgr = IRQManager()
    irqMgr.init(STOP_FILE)

    materialsDb = MaterialsDatabase()
    dbLoaded = materialsDb.init(MATERIALS_DB_FILE)

    matSet = MaterialsSet()
    matSet.initByFile(MATERIALS_FILE, materialsDb)
    materials_desc, num_mats, MATERIALS = matSet.getMaterialsList()

    if (dbLoaded):
        materialsDb.assertContains(matSet)
    is_prob_ok, inconsistencies = is_problem_well_posed(paramsHolder, optimizerConf, matSet)
    if (not is_prob_ok):
        logger.error("[feasibility] The problem has inconsistencies:")
        for incs in inconsistencies:
            logger.error("[feasibility]     - " + incs)
        logger.error("[feasibility] The optimizer cannot process an inconsistent problem.")
        sys.exit(1)

    materialsDb.reduceTo([MATERIALS])

    # -------------------------------------
    # Optimize loop
    # -------------------------------------
    logger.info("[driver] Optimization core engine parameters (verbose="+ str(OPTIM_VERBOSE) + "):\n" + optimizerConf.toString())

    objFactory = CO_ObjectFactory()
    searchSpBuilder = objFactory.createObject("search space builder", SSB_MODULE, SSB_CLASSNAME, SearchSpaceBuilderAdv250814())

    searchSpBuilder.init(paramsHolder, matSet)
    search_space = searchSpBuilder.getSearchSpace()

    constrPar = ConstraintParams()
    constrPar.init(paramsHolder)

    logger.info("[driver] Defining objective function")
    objTargets = KPITargets()
    objTargets.init(paramsHolder)
    objFunEvaluator = objFactory.createObject("object function evaluator", OFE_MODULE, OFE_CLASSNAME, ObjFEval_Base250801())
    oFunParamsDict = load_params_generic(OBJFUN_PARAMS_FILE, "objFunParams")
    objFunEvaluator.setParams(oFunParamsDict)
    objFunEvaluator.setProblemRef(constrPar, objTargets)
    targetEvaluator = objFactory.createObject("target evaluator", TRG_MODULE, TRG_CLASSNAME, TargetEval_Base250801())
    targetEvaluator.setTargets(objTargets)

    objective_fn = partial(objective, inParamsHolder=paramsHolder, search_sp_bldr=searchSpBuilder, materials_set=matSet, constr_par=constrPar, objf_evaluator=objFunEvaluator, trg_evaluator=targetEvaluator)
    histManager = HistoryManager()
    x0, y0, prev_attempts = histManager.getHistory(HISTORY_FILE, HISTORY_SLICING_DIR)
    x0 = process_retrieved_history(x0, MATERIALS, searchSpBuilder, prev_attempts, paramsHolder, optimizerConf)

    wrapped_post_callback = partial(post_sim_logic, prv_attempts=prev_attempts, irq_Manager=irqMgr, hist_Manager=histManager)

    x0isValid, reduced_x0 = histManager.checkX0(x0, search_space)
    logger.info("[driver] Optimization loop BEGIN")
    t_begin = datetime.now()
    result = gp_minimize(
        objective_fn,
        search_space,
        n_calls=MAX_RUNS,
        n_initial_points=INITIAL_POINTS,
        x0=x0,
        y0=y0,
        callback=[wrapped_post_callback],
        initial_point_generator=optimizerConf.getParam("initial_point_generator"),
        acq_func=optimizerConf.getParam("acq_func"),
        acq_optimizer=optimizerConf.getParam("acq_optimizer"),
        random_state=optimizerConf.getParam("random_state"),
        n_points=optimizerConf.getParam("n_points"),
        n_restarts_optimizer=optimizerConf.getParam("n_restarts_optimizer"),
        kappa=optimizerConf.getParam("kappa"),
        xi=optimizerConf.getParam("xi"),
        noise=optimizerConf.getParam("noise"),
        n_jobs=optimizerConf.getParam("n_jobs"),
        model_queue_size=optimizerConf.getParam("model_queue_size"),
        verbose=OPTIM_VERBOSE
    )
    mins, time_formatted = get_elapsed_time(t_begin, datetime.now())
    logger.info("[opttrace][driver] Optimization loop completed. Elapsed: " + time_formatted + " (mins: " + str(mins) + ")")
    histManager.logBestSolution(result, searchSpBuilder)
    histManager.introspectResult(result, searchSpBuilder, "Optimization Summary")
    # Save state at the end
    histManager.updateHistory(result)

    logger.debug("[driver] gp_minimize result full dump:")
    logger.debug("[driver] " + str(result))

if __name__ == '__main__':
    main()

