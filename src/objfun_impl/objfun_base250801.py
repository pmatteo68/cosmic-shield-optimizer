from logging_utils import init_logger

class ObjFEval_Base250801:
    def __init__(self):
        self._params_dict = {}
        logger = init_logger()
        logger.debug("[objfun-base250801] Object function evaluator instantiated")

    def setParams(self, prDict):
        if (not (prDict is None)):
            self._params_dict = prDict

    def setProblemRef(self, constrPar, objTargets):
        logger = init_logger()
        logger.debug("[objfun-base250801] Problem ref. SET (dummy, nothing to do in this implementation)")

    #def evalObjFun(self, kpis_dict, input_data_dict, constraints_dict, targets_dict):
    def evalObjFun(self, kpis_dict, input_data_dict):
        #logger = init_logger()
        # We minimize, so return negative sum to push higher values
        obj_fun_val = - (kpis_dict["energy_efficiency"] + kpis_dict["protection_efficiency"])
        return obj_fun_val

