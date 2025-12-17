import os
import pickle

#from pprint import pprint
from skopt.space import Space, Integer, Real, Categorical
#import numbers
import numpy as np

from logging_utils import init_logger
from x0_builder import X0Builder

# handling retrieved history
def process_retrieved_history(x0_orig, materials_list, searchSpBuilder, prev_attempts, paramsHolder, optimizerConf):
    logger = init_logger()
    hist_file = paramsHolder.get("history_file")
    x0_file = paramsHolder.get("init_x0")
    max_layers = paramsHolder.get("max_layers")
    min_layer_thickn = paramsHolder.get("min_layer_thickness")
    init_points = optimizerConf.getParam("n_initial_points")
    rnd_x0_if_needed = (paramsHolder.get("rnd_x0_fallback", "true") == "true")
    search_space = searchSpBuilder.getSearchSpace()
    if (prev_attempts > 0):
        logger.info("[driver] Restarting from pre-loaded history (" + hist_file + ", history points: " + str(prev_attempts) + ")")
        return x0_orig
    else:
        x0builder = X0Builder()
        x0 = x0builder.getX0FromFile(x0_file, max_layers, materials_list, searchSpBuilder, min_layer_thickn)
        if (x0 is None):
            if (rnd_x0_if_needed):
                x0 = x0builder.createRandomX0(search_space, init_points)
                logger.info("[driver] X0 (shield initial configuration) was built randomly with custom code")
            else:
                logger.info("[driver] X0 (shield initial configuration) will be built randomly by the optimization library")
        else:
            logger.info("[driver] X0 (shield initial configuration) loaded from: " + x0_file)
        return x0

def log_best_sol(res, searchSpBuilder):
    logger = init_logger()
    best_res_x = res.x
    if ((searchSpBuilder is not None) and searchSpBuilder.materialsByIndex()):
        logger.info(f"[opttrace][history] Best solution (x): {searchSpBuilder.decode_x_point(best_res_x)}")
        logger.info(f"[opttrace][history]   Raw: {best_res_x}")
    else:
        logger.info(f"[opttrace][history] Best raw solution (x): {res.x}")
    logger.info(f"[opttrace][history] Best objective function value (y/fun): {res.fun}")

def introspect_gpm_result(res, searchSpBuilder, title):
    """
    Print a summary of a skopt.gp_minimize result, including search space info.
    """
    logger = init_logger()
    try:
        n_points = len(res.x_iters)
        dim = len(res.x) if res.x is not None else None

        print("=== " + title + " ===")
        print(f"Total evaluations: {n_points}")
        #best_res_x = res.x
        #if ((searchSpBuilder is not None) and searchSpBuilder.materialsByIndex()):
        #    print(f"Best solution (x): {searchSpBuilder.decode_x_point(best_res_x)}")
        #    print(f"  Raw: {best_res_x}")
        #else:
        #    print(f"Best raw solution (x): {res.x}")
        #print(f"Best objective value (y/fun): {res.fun}")
        best_val = np.min(res.func_vals)
        best_iters0 = np.where(res.func_vals == best_val)[0]      # all zero-based indices
        best_iters1 = [i + 1 for i in best_iters0]                  # convert to 1-based
        best_points = [res.x_iters[i] for i in best_iters0]
        num_best_pts = len(best_iters1)
        print(f" Best objective function value (y): {best_val}, found at the following points (#: {num_best_pts}):")
        for it, pt in zip(best_iters1, best_points):
            if ((searchSpBuilder is not None) and searchSpBuilder.materialsByIndex()):
                print(f"    x({it}) -> {searchSpBuilder.decode_x_point(pt)}")
            print(f"    x_raw({it}) -> {pt}")

        if dim is not None:
            print(f"Dimension of search space: {dim}")

            # distribution of points along dimensions
            X = np.array(res.x_iters)
            for d in range(dim):
                col = X[:, d]
                print(f"  - Dimension {d}: {len(np.unique(col))} unique values "
                      f"(min={col.min()}, max={col.max()})")

        # stats on function values
        vals = np.array(res.func_vals)
        print("Objective value statistics:")
        print(f"  Min (best):   {vals.min()}")
        print(f"  Max (worst):  {vals.max()}")
        print(f"  Mean:         {vals.mean()}")
        print(f"  Median:       {np.median(vals)}")
        print(f"  Std dev:      {vals.std()}")

        # search space specifics
        print("Search space definition:")
        for i, dim in enumerate(res.space.dimensions):
            if hasattr(dim, "bounds"):
                bounds = dim.bounds
            else:
                bounds = None
            prior = getattr(dim, "prior", None)
            print(f"  - {i}: name={dim.name}, type={dim.__class__.__name__}, "
                  f"bounds={bounds}, prior={prior}")

        # optimizer configuration details
        #print("Optimizer configuration:")
        #for key in [
        #    "base_estimator", "n_calls", "n_random_starts", "n_initial_points",
        #    "initial_point_generator", "acq_func", "acq_optimizer",
        #    "random_state", "verbose", "n_points", "n_restarts_optimizer",
        #    "xi", "kappa", "n_jobs", "model_queue_size", "space_constraint",
        #    "function"
        #]:
        #    if hasattr(res, key):
        #        print(f"  {key}: {getattr(res, key)}")
        #
        # X0
        #if hasattr(res, "x0") and res.x0 is not None:
        #    try:
        #        depth = len(res.x0)
        #        print(f"Initial X0 depth: {depth}")
        #    except Exception:
        #        print("Initial X0 present but could not determine depth")

        print("============================")

    except Exception as e:
        logger.error(f"[history] Error while summarizing gp_minimize result: {e}")

def introspect_X0(x0, search_sp_raw):
    """
    Validate that x0 is consistent with search_space.
    - x0 must be a list of lists
    - each point must have same dimension as search_space
    - values must lie within bounds for Real/Integer
    - values must be in categories for Categorical
    Collect all violations, raise ValueError at the end if any.
    """
    logger = init_logger()
    search_space = Space(search_sp_raw)
    errors = []
    invalid_indices = set()
    all_valid = False
    reduced_x0 = []

    # check structure
    if not isinstance(x0, (list, tuple)) or not all(isinstance(xx, (list, tuple)) for xx in x0):
        raise ValueError("x0 must be a list of lists")

    dim = len(search_space.dimensions)

    itot = len(x0)
    #i_good = 0
    for i, point in enumerate(x0):
        # dimension check
        if len(point) != dim:
            invalid_indices.add(i)
            errors.append(f"Point {i} has dimension {len(point)} but expected {dim}")
            continue

        # per-dimension checks
        for j, (val, dim_def) in enumerate(zip(point, search_space.dimensions)):
            if isinstance(dim_def, Real):
                lo, hi = dim_def.bounds
                if not (lo <= val <= hi):
                    invalid_indices.add(i)
                    errors.append(f"Point {i}, dim {j}: value {val} outside bounds {lo}..{hi}")

            #elif isinstance(dim_def, Integer):
            #    lo, hi = dim_def.bounds
            #    if not (isinstance(val, int) or (isinstance(val, float) and val.is_integer())) or not (lo <= val <= hi):
            #        invalid_indices.add(i)
            #        errors.append(f"Point {i}, dim {j}: value {val} not integer in {lo}..{hi}")

            elif isinstance(dim_def, Integer):
                lo, hi = dim_def.bounds
                if isinstance(dim, Integer):
                    if not float(val).is_integer() or val < dim.low or val > dim.high:
                        errors.append(f"Point {i}, dim {j}: value {val} not integer in {lo}..{hi}")
                        invalid_indices.add(i)

            elif isinstance(dim_def, Categorical):
                if val not in dim_def.categories:
                    invalid_indices.add(i)
                    errors.append(f"Point {i}, dim {j}: value {val} not in categories {dim_def.categories}")

            else:
                invalid_indices.add(i)
                errors.append(f"Point {i}, dim {j}: unsupported dimension type {type(dim_def)}")
        #good = i_good + 1

    if errors:
        if (itot - len(invalid_indices) > 0):
            logger.error("[history] X0 validation PARTIALLY failed, as some data points were valid: " + str(i_good))
        for errormsg in errors:
            logger.error("[history] X0 validation error: " + errormsg) 
        #raise ValueError("[history] X0 validation failed")
    else:
        logger.info("[history] X0 was successfully validated (data points: " + str(itot) + ").")

    reduced_x0 = [pt for idx, pt in enumerate(x0) if idx not in invalid_indices]
    all_valid = (len(errors) == 0)
    return all_valid, reduced_x0
        

def get_list_fragment(lst, selection):
    logger = init_logger()
    """
    Returns a sublist from lst according to selection string:
      - 'a:b'  -> from a-th element, length b
      - 'a:'   -> from a-th element to end
      - ':b'   -> first b elements
      - '_:b'  -> last b elements
    Overshoots handled gracefully like Python slicing.
    If selection is None or malformed, returns the full list with a warning.
    If lst is None, returns [] with a warning.
    If lst is empty, returns [] with a warning.
    """
    if lst is None:
        logger.warning("[history] Slicing process: the specified history list is None. Returning [].")
        return []
    if len(lst) == 0:
        logger.warning("[history] Slicing process: the specified history list is empty. Returning [].")
        return []

    if selection is None:
        logger.warning("[history] Slicing process: the specified history  is None. Returning full list.")
        return lst

    try:
        if ":" not in selection:
            raise ValueError("Missing ':' separator.")

        a_str, b_str = selection.split(":", 1)

        if a_str == "_" and b_str:  # format "_:b" (last b elements)
            b = int(b_str)
            if b <= 0:
                raise ValueError("Invalid length.")
            return lst[-b:]

        elif a_str and b_str:  # format "a:b"
            a, b = int(a_str), int(b_str)
            if a < 0 or b <= 0:
                raise ValueError("Invalid indices.")
            return lst[a:a+b]

        elif a_str and not b_str:  # format "a:"
            a = int(a_str)
            if a < 0:
                raise ValueError("Invalid index.")
            return lst[a:]

        elif not a_str and b_str:  # format ":b"
            b = int(b_str)
            if b <= 0:
                raise ValueError("Invalid length.")
            return lst[:b]

        else:
            raise ValueError("Empty selection string.")

    except Exception as e:
        logger.warning(f"[history] Slicing process error: invalid slicing directive '{selection}' ({e}). Returning full list.")
        return lst

class HistoryManager:
    def __init__(self):
        self._hist_file = None
        self._is_initialized = False
        #self._num_items = 0
        #self._desc = "n.a."

    #def check(self, search_sp, x0):
    #    validate_x0(search_sp, x0)
    #def sanitize(self, search_sp, x0):
    #    return sanitize_x0(search_sp, x0)
    def introspectResult(self, res, search_sp_bldr, title):
        introspect_gpm_result(res, search_sp_bldr, title)

    def logBestSolution(self, res, searchSpBuilder):
        log_best_sol(res, searchSpBuilder)

    def checkX0(self, x0, search_sp):
        return introspect_X0(x0, search_sp)

    #def getHistory(self, hist_file: str, last_slice_sz: int):
    def getHistory(self, hist_file: str, slicing_directive: str):
        num_items = 0
        x0 = None
        y0 = None
        if (hist_file is None):
            #raise ValueError("[history] A not-null file path for the history management has to be specified!")
            return x0, y0, num_items
            logger.info("[history] Starting optimization loop from scratch (history file was not specified)")
            return x0, y0, num_items

        self._hist_file = hist_file
        logger = init_logger()
        if os.path.exists(hist_file):
            logger.debug("[history] Resuming optimization loop (loading history from: " + hist_file + ")...")
            with open(hist_file, 'rb') as f:
                res = pickle.load(f)
            x0 = res.x_iters
            #if x0 is not None:
            #    #debug_history(x0)
            #    #validate_x0(sspace, x0)
            num_items = len(x0 or [])
            logger.info("[history] History retrieved (" + hist_file + "). History points: " + str(num_items))
            y0 = res.func_vals.tolist()

            x0, y0 = get_list_fragment(x0, slicing_directive), get_list_fragment(y0, slicing_directive)
            slice_sz = len(x0 or [])
            if (num_items > 0) and (num_items > slice_sz):
                old_hist_sz = num_items
                num_items = slice_sz
                logger.info("[history] History has been sliced [orig sz: " + str(old_hist_sz) + ", optimizer will consider only the selected slice (slicing directive: " + slicing_directive + " , sz: " + str(num_items) + ")]")
            #if ((last_slice_sz > 0) and (num_items > last_slice_sz)):
            #    old_hist_sz = num_items
            #    x0, y0 = x0[-last_slice_sz:], y0[-last_slice_sz:]
            #    num_items = last_slice_sz
            #    logger.info("[history] History has been sliced (orig sz: " + str(old_hist_sz) + ", optimizer will consider only last " + str(num_items) + ")")
        else:
            logger.info("[history] Starting optimization loop from scratch (history file " + hist_file + " not found, and it will be created at the end of the loop)")
            num_items = 0
            x0 = None
            y0 = None

        self._is_initialized = True
        return x0, y0, num_items

    def updateHistory(self, oResult):
        if (not self._is_initialized):
            raise RuntimeError("[history] Error. Bad Sequence. 'updateHistory' cannot be called here, as the history manager has not been initialized")
        logger = init_logger()
        if (self._hist_file is None):
            logger.info("[history] History is not being saved or updated, as no history file was specified.")
        else:
            logger.info("[history] Updating history (" + self._hist_file + ")")
            with open(self._hist_file, 'wb') as f:
                pickle.dump(oResult, f)
            logger.info("[history] History updated")


