from logging_utils import init_logger

class TargetEval_Base250801:
    def __init__(self):
        logger = init_logger()
        self._targets_dict = {}
        logger.debug("[target-base250801] Target evaluator instantiated")

    def setTargets(self, kpiTargets):
        self._targets_dict = kpiTargets.getTargetsAsDict()

    def isTargetMet(self, kpis_dict):
        #logger = init_logger()
        trg_dict = self._targets_dict
        is_trg_met = kpis_dict["energy_efficiency"] >= trg_dict["target_eeff"] and kpis_dict["protection_efficiency"] >= trg_dict["target_peff"]
        return is_trg_met

