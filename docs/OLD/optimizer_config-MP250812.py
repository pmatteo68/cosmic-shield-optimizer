import json
import os

from logging_utils import init_logger

class OptimizerConfig:
    def __init__(self):
        self._is_initialized = False
        self._params = []
        # Embedded defaults in case of failure in loading file, or in case of parameter not specified
        # "n_calls": 1000 and "verbose": False are better off in the command line
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

        logger.info("Loading optimizator configuration from: {confFilePath}")
        defaults = self._defaults.copy()
        optimCfgEntry = "optimizerParams"
        try:
            if not os.path.isfile(confFilePath):
                raise FileNotFoundError(f"Optimizator configuration file not found: {confFilePath}")
            #with open(confFilePath, "r", encoding="utf-8") as f:
            with open(confFilePath, "r") as f:
                ocdata = json.load(f)
                fileParamsRoot = ocdata[optimCfgEntry]
            if optimCfgEntry not in ocdata or not isinstance(ocdata[optimCfgEntry], dict):
                raise ValueError("Missing or invalid '" + optimCfgEntry + "' section in configuration file.")
        except Exception as e:
            fileParamsRoot = None
            # Log the error and fallback to defaults
            logger.warning("Could not load optimizer parameters from file: {e}, falling back to defaults")

        #populate params list
        paramsList = []
        for pName, pDefVal in self._defaults.items():
            pValue, pSourceDesc = fileParamsRoot[pName], "conf. file" if (fileParamsRoot and (pName in fileParamsRoot)) else pDefVal, "default"
            #paramInConfFile = (fileParamsRoot and (pName in fileParamsRoot))
            #sourceDesc = "conf. file" if paramInConfFile else "default"
            #pValue = fileParamsRoot[pName] if paramInConfFile else pDefVal
            paramsList.append((pName, pValue, pSourceDesc))
        self._params = paramsList

        #inform about unrecognized parameters with a warning
        if (fileParamsRoot):
            for fpName, _ in fileParamsRoot:
                if (not (fpName in defaults)):
                    logger.warning("[OPTIMIZER_CONFIG] Unrecognized parameter: " + fpName)

        self._is_initialized = True


    def toString(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[OPTIMIZER_CONFIG] ERROR. Bad Sequence. 'toString' cannot be called here, as the optimizer config object is not initialized")
        return (json.dumps({n: f"{v} ({d})" for n, v, d in self._params}, indent=3))

    #Retrieve a parameter by name. Raises error if not found
    def getOptimizerParam(self, paramName: str):
        if (not (self._is_initialized)):
            raise RuntimeError("[OPTIMIZER_CONFIG] ERROR. Bad Sequence. 'getOptimizerParam' cannot be called here, as the optimizer config object is not initialized")
        for n, v, _ in self._params:
            if n == name:
                return v
        raise KeyError(f"[OPTIMIZER_CONFIG] ERROR. Parameter '{paramName}' not found")

