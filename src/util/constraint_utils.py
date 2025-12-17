from logging_utils import init_logger

# -------------------------------------
# Constraints
# -------------------------------------

#Constraint params useful for pre-simulation checks
class ConstraintParamsPRE:
    def __init__(self):
        self._constr_par = None
        self._is_initialized = False

    def init(self, constraintPar):
        self._constr_par = constraintPar
        self._is_initialized = True

    def getParams(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr][pre] ERROR. Bad Sequence. 'getParams' cannot be called here, as the ConstraintParamsPRE object is not initialized")
        return self._constr_par.getParams()

#Constraint params useful for post-simulation checks
class ConstraintParamsPOST:
    def __init__(self):
        self._constr_par = None
        self._is_initialized = False

    def init(self, constraintPar):
        self._constr_par = constraintPar
        self._is_initialized = True

    def getParams(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr][post] ERROR. Bad Sequence. 'getParams' cannot be called here, as the ConstraintParamsPOST object is not initialized")
        _, _, _, max_weight, _, _, _ = self._constr_par.getParams()
        return max_weight

class ConstraintParams:
    def __init__(self):
        self._max_weight = None
        self._max_layer_thickn = None
        self._min_tot_thick = None
        self._max_tot_thick = None
        self._min_stiff = None
        self._max_stiff = None
        self._max_cost = None
        self._constr_par_pre = None
        self._constr_par_post = None
        self._is_initialized = False

    #def init(self, max_weight, max_layer_thickn, min_tot_thick, max_tot_thick, min_stiff, max_stiff, max_cost):
    def init(self, paramsHolder):
        max_weight = paramsHolder.get("max_shield_weight")
        max_layer_thickn = paramsHolder.get("max_layer_thickness")
        min_tot_thick = paramsHolder.get("min_shield_thickness")
        max_tot_thick = paramsHolder.get("max_shield_thickness")
        min_stiff = paramsHolder.get("min_shield_stiffness")
        max_stiff = paramsHolder.get("max_shield_stiffness")
        max_cost = paramsHolder.get("max_tco")
        self._max_weight = max_weight
        self._max_layer_thickn = max_layer_thickn
        self._min_tot_thick = min_tot_thick
        self._max_tot_thick = max_tot_thick
        self._min_stiff = min_stiff
        self._max_stiff = max_stiff
        self._max_cost = max_cost
        self._constr_par_pre = ConstraintParamsPRE()
        self._constr_par_pre.init(self)
        self._constr_par_post = ConstraintParamsPOST()
        self._constr_par_post.init(self)
        self._is_initialized = True

    def getPRE(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr] ERROR. Bad Sequence. 'getPRE' cannot be called here, as the ConstraintParams object is not initialized")
        return self._constr_par_pre

    def getPOST(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr] ERROR. Bad Sequence. 'getPOST' cannot be called here, as the ConstraintParams object is not initialized")
        return self._constr_par_post

    def getParams(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr] ERROR. Bad Sequence. 'getParams' cannot be called here, as the ConstraintParams object is not initialized")
        return self._max_layer_thickn, self._min_tot_thick, self._max_tot_thick, self._max_weight, self._min_stiff, self._max_stiff, self._max_cost

    #used by obj function evaluators
    def getParamsAsDict(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[constr] ERROR. Bad Sequence. 'getParamsAsDict' cannot be called here, as the ConstraintParams object is not initialized")
        max_layer_thickn, min_tot_thick, max_tot_thick, max_weight, min_stiff, max_stiff, max_cost = self.getParams()
        constr_dict = {}
        constr_dict["max_layer_thickness"] = max_layer_thickn
        constr_dict["min_tot_thickness"] = min_tot_thick
        constr_dict["max_tot_thickness"] = max_tot_thick
        constr_dict["max_weight"] = max_weight
        constr_dict["min_stiffness"] = min_stiff
        constr_dict["max_stiffness"] = max_stiff
        constr_dict["max_cost"] = max_cost
        return constr_dict

def check_constraints_pre(shield, constrParPRE):
    logger = init_logger()
    logger.info("[constr][pre] Pre-test constraints check - begin")

    max_layer_thick, min_tot_thick, max_tot_thick, max_wgt, min_stiff, max_stiff, max_econ_cost = constrParPRE.getParams()
    logger.debug(f"[constr][pre] max_layer_thick={max_layer_thick}, min_tot_thick={min_tot_thick}, max_tot_thick={max_tot_thick}, max_wgt={max_wgt}, max_econ_cost={max_econ_cost}")

    s_stiffness = shield.getStiffness()
    if ((s_stiffness > max_stiff) or (s_stiffness < min_stiff)):
        logger.warning(f"[constr][pre] Shield stiffness out of range: {s_stiffness:.5f} (range: {min_stiff:.5f}-{max_stiff:.5f})")

    total_thickness = shield.getTotThickness()
    if ((total_thickness > max_tot_thick) or (total_thickness < min_tot_thick)):
        # we calculate also on min_tot_thick but if the problem is well posed, this should be just impossible
        logger.info(f"[constr][pre] Shield thickness out of range: {total_thickness:.5f} (range: {max_tot_thick:.5f}-{max_tot_thick:.5f})")
        return False

    #if shield.hasConsecutiveDupMaterials():
    #    logger.info("[constr][pre] Consecutive layers material match, skipping.")
    #    return False

    tot_wgt_pre = shield.getTotWeight()    
    if (tot_wgt_pre):
        logger.info("[constr][pre] Pre-calculated shield norm. weight: " + str(tot_wgt_pre))
        if (tot_wgt_pre > max_wgt):
            logger.info(f"[constr][pre] Excessive weight (pre): {tot_wgt_pre:.2f} (max allowed: {max_wgt:.2f})")
            return False

    largestEffLayerSz = shield.getLargestEffLayerSz()
    if (largestEffLayerSz > max_layer_thick):
        logger.info(f"[constr][pre] Excessive effective layer size caused by CONSECUTIVE LAYERS MADE OF SAME MATERIAL (pre): {largestEffLayerSz:.2f} (max allowed: {max_layer_thick:.2f})")
        return False

    shieldCost = shield.getTCO()
    if (shieldCost > max_econ_cost):
        logger.info(f"[constr][pre] Excessive cost (pre): {shieldCost:.2f} (max allowed: {max_econ_cost:.2f})")
        return False

    logger.info(f"[constr][pre] Pre-test constraints check PASSED")
    return True

def check_constraints_post(shield, kpis, constrParPOST):
    logger = init_logger()
    logger.info(f"[constr][post] Post-test constraints check - begin")

    max_wgt = constrParPOST.getParams()
    logger.debug(f"[constr][post] max_wgt={max_wgt}")

    total_weight_post = kpis.getShieldWeight()
    tot_wgt_pre = shield.getTotWeight()
    if (tot_wgt_pre):
        #tot_wgt_pre = tot_wgt_pre + 0.001
        #tot_wgt_pre is specified only if the materials db was initialized correctly.
        #In such case, the threshold is checked already in the check_constraints_pre function, no need to do it again, we only write a warning if pre and post weights differ.
        if (tot_wgt_pre == total_weight_post):
            logger.debug("[constr][post] Weight_pre and weight_post MATCH! THIS IS OK!")
        else:
            logger.warning(f"[constr][post] Weight calculation pre/post simulation discrepancy found: {tot_wgt_pre:.5f}/{total_weight_post:.5f}, further analysis is recommended.")
    else:
        #in this case, the materials db was not initialized at all, or its initialization failed. Then we check the weight threshold in the post phase, i.e. here
        if total_weight_post > max_wgt:
            logger.info(f"[constr][post] Excessive weight (post): {total_weight_post:.2f} (max allowed: {max_wgt:.2f})")
            return False

    logger.info(f"[constr][post] Post-test constraints check PASSED")
    return True

