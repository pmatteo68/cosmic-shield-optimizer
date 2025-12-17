import csv

from logging_utils import init_logger
from css_metadata import create_kpi_filepath

class KPITargets:
    def __init__(self):
        self._trg_eeff = None
        self._trg_peff = None
        self._is_initialized = False

    def init(self, params_holder):
        trg_eeff = params_holder.get("target_energy_eff")
        trg_peff = params_holder.get("target_protection_eff")
        self._trg_eeff = trg_eeff
        self._trg_peff = trg_peff
        self._is_initialized = True

    def getTargets(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpit] ERROR. Bad Sequence. 'getTargets' cannot be called here, as the KPI target object is not initialized")
        return self._trg_eeff, self._trg_peff

    # used by the object function evaluators
    def getTargetsAsDict(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpit] ERROR. Bad Sequence. 'getTargetsAsDict' cannot be called here, as the KPI target object is not initialized")
        trg_eeff, trg_peff = self.getTargets()
        trg_dict = {}
        trg_dict["target_eeff"] = trg_eeff
        trg_dict["target_peff"] = trg_peff
        return trg_dict

    #def getTargetEnergyEff(self):
    #    if (not (self._is_initialized)):
    #        raise RuntimeError("[kpit] ERROR. Bad Sequence. 'getTargetEnergyEff' cannot be called here, as the KPI target object is not initialized")
    #    return self._trg_eeff

    #def getTargetProtectionEff(self):
    #    if (not (self._is_initialized)):
    #        raise RuntimeError("[kpit] ERROR. Bad Sequence. 'getTargetProtectionEff' cannot be called here, as the KPI target object is not initialized")
    #    return self._trg_peff

class KPIHolder:
    def __init__(self):
        self._kpis_file = None
        self._kpis_dict = {}
        self._objf_evaluator = None
        self._target_met_assessor = None
        self._is_initialized = False

    def load(self, sim_id: str, out_root_dir: str, objfu_evaluator, targetMetAssessor):
        logger = init_logger()

        kpi_file_path, kpi_file_delim = create_kpi_filepath(out_root_dir, sim_id)
        self._kpis_file = kpi_file_path
        self._objf_evaluator = objfu_evaluator
        self._target_met_assessor = targetMetAssessor

        logger.info("[kpih] Initialization (retrieving KPIs from: " + self._kpis_file + ")")
        with open(self._kpis_file) as f:
            reader = csv.reader(f, delimiter=kpi_file_delim)
            header = next(reader)  # skip header
            row = next(reader)
            #total_thickness = float(row[0]) # I don't need it
            total_wgt = float(row[1])
            energ_eff = float(row[2])
            protect_eff = float(row[3])
            logger.info("[kpih] KPIs retrieved:")
            logger.info("[kpih]    Weight:          " + str(total_wgt))
            logger.info("[kpih]    Energy eff.:     " + str(energ_eff))
            logger.info("[kpih]    Protection eff.: " + str(protect_eff))

            self._kpis_dict["shield_weight"] = total_wgt
            self._kpis_dict["energy_efficiency"] = energ_eff
            self._kpis_dict["protection_efficiency"] = protect_eff

        self._is_initialized = True
        logger.info("[kpih] KPIs retrieved successfully")

    def getShieldWeight(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpih] ERROR. Bad Sequence. 'getShieldWeight' cannot be called here, as the KPI holder is not initialized")
        return self._kpis_dict["shield_weight"]

    def evalObjFunction(self, shield):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpih] ERROR. Bad Sequence. 'evalObjFunction' cannot be called here, as the KPI holder is not initialized")

        input_data_dict = {}
        input_data_dict["shield_tot_thickness"] = shield.getTotThickness()
        input_data_dict["shield_tot_weight"] = shield.getTotWeight()

        obj_fun_val = self._objf_evaluator.evalObjFun(self._kpis_dict, input_data_dict)
        return obj_fun_val

    def targetIsMet(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpih] ERROR. Bad Sequence. 'targetIsMet' cannot be called here, as the KPI holder is not initialized")
        return (self._target_met_assessor.isTargetMet(self._kpis_dict))

    def toString(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[kpih] ERROR. Bad Sequence. 'toString' cannot be called here, as the KPI holder is not initialized")
        return ", ".join(f"{k}={v}" for k, v in self._kpis_dict.items())


