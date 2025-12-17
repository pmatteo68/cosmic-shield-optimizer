import json
import os

from logging_utils import init_logger

class OptimizerConfig:
    def __init__(self):
        self._is_initialized = False
        self._params = []
        self._defaults = {
            "n_initial_points": 200,
            "initial_point_generator": "random",
            "acq_func": "gp_hedge",
            "acq_optimizer": "lbfgs",
            "random_state": None,
            "n_points": 10000,
            "n_restarts_optimizer": 5,
            "kappa": 1.96,
            "xi": 0.01,
            "noise": "gaussian",
            "n_jobs": 1,
            "model_queue_size": None
        }

    def init(self, confFilePath: str):
        logger = init_logger()

        logger.info(f"[optconf] Loading optimizer configuration from: {confFilePath}")  # use f-string
        defaults = self._defaults.copy()
        optimCfgEntry = "optimizerParams"
        fileParamsRoot = None

        try:
            if not os.path.isfile(confFilePath):
                raise FileNotFoundError(f"Optimizer configuration file not found: {confFilePath}")
            with open(confFilePath, "r") as f:
                ocdata = json.load(f)
            if optimCfgEntry not in ocdata or not isinstance(ocdata[optimCfgEntry], dict):
                raise ValueError(f"Missing or invalid '{optimCfgEntry}' section in configuration file.")
            fileParamsRoot = ocdata[optimCfgEntry]
        except Exception as e:
            # Log the error and fallback to defaults
            logger.warning(f"[optconf] Could not load optimizer parameters from file: {e}, falling back to defaults")

        # populate params list correctly
        paramsList = []
        for pName, pDefVal in defaults.items():
            if fileParamsRoot and pName in fileParamsRoot:
                pValue, pSourceDesc = fileParamsRoot[pName], "conf. file"
            else:
                pValue, pSourceDesc = pDefVal, "default"
            paramsList.append((pName, pValue, pSourceDesc))
        self._params = paramsList

        # inform about unrecognized parameters with a warning
        if fileParamsRoot:
            for fpName in fileParamsRoot:
                if fpName not in defaults:
                    logger.warning(f"[optconf] Unrecognized parameter: {fpName}")

        self._is_initialized = True

    def toString(self):
        if not self._is_initialized:
            raise RuntimeError("[optconf] ERROR. Bad Sequence. 'toString' cannot be called before initialization")
        return json.dumps({n: f"{v} ({d})" for n, v, d in self._params}, indent=3)

    # Retrieve a parameter by name. Raises error if not found
    def getParam(self, paramName: str):
        if not self._is_initialized:
            raise RuntimeError("[optconf] ERROR. Bad Sequence. 'getOptimizerParam' cannot be called before initialization")
        for n, v, _ in self._params:
            if n == paramName:   # fix: use paramName instead of undefined name
                return v
        raise KeyError(f"[optconf] ERROR. Parameter '{paramName}' not found")

