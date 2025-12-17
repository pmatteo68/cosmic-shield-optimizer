import math

from logging_utils import init_logger

class ObjFEval_AdvFMS250817:
    def __init__(self):
        logger = init_logger()
        self._constraints_dict = {}
        self._targets_dict = {}
        self._params_dict = {}

        logger.debug("[objfun] Object function evaluator instantiated")

    def setParams(self, prDict):
        logger = init_logger()
        if (not (prDict is None)):
            self._params_dict = prDict
            logger.info("[objfun] Parameters set: " + ", ".join(f"{k}={v}" for k, v in prDict.items()))

    def setProblemRef(self, constrPar, objTargets):
        self._constraints_dict = constrPar.getParamsAsDict()
        self._targets_dict = objTargets.getTargetsAsDict()

    def evalObjFun(self, kpis_dict, input_data_dict):
        logger = init_logger()

        # New logarithmic formula, weights + penalties

        # Weights and parameters of the new formula
        ofe_params = self._params_dict
        w_EE = ofe_params["w_EE"]
        w_PE = ofe_params["w_PE"]
        lambda_T = ofe_params["lambda_T"]
        lambda_W = ofe_params["lambda_W"]
        alpha_T = ofe_params["alpha_T"]
        alpha_W = ofe_params["alpha_W"]
        epsilon = ofe_params["epsilon"]
        hp_exponent = ofe_params["hp_exponent"]

        # Needed from input data:
        T = input_data_dict["shield_tot_thickness"]
        W = input_data_dict["shield_tot_weight"]

        # Needed from targets parameters
        target_params = self._targets_dict
        EE_target = target_params["target_eeff"]
        PE_target = target_params["target_peff"]

        # Needed from constraints
        constr_params = self._constraints_dict
        #T_max = constr_params["max_layer_thickness"], bug, fixed on 250909, 1.1.0, F. M. Soccorsi, max_tot_thickness max_shield_thickness
        T_max = constr_params["max_tot_thickness"]
        W_max = constr_params["max_weight"]

        # Needed from KPIs
        EE = kpis_dict["energy_efficiency"]
        PE = kpis_dict["protection_efficiency"]

        # Normalization in regards to targets
        EE_tilde = min(EE / EE_target, 1.0)
        PE_tilde = min(PE / PE_target, 1.0)
        T_tilde = T / T_max
        W_tilde = W / W_max

        # SCORE - Rewarding logarithmic component
        score = -math.log(epsilon + (w_EE * EE_tilde + w_PE * PE_tilde))

        # Mild linear penalties
        mild_penalty = lambda_T * T_tilde + lambda_W * W_tilde

        # Hard penalties (quadratic or more; if above configured thresholds
        #hp_exponent = 2
        hard_penalty = alpha_T * abs(max(0.0, T - T_max)) ** hp_exponent
        hard_penalty += alpha_W * abs(max(0.0, W - W_max)) ** hp_exponent

        penalty = mild_penalty + hard_penalty
        logger.debug("[objfun] Obj. function breakdown -  score: " + str(score) + ", mild_penalty: " + str(mild_penalty) + ", hard_penalty: " + str(hard_penalty))

        obj_fun_val = score + penalty

        return obj_fun_val

