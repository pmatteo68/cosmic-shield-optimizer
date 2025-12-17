
#from logging_utils import init_logger

#def is_problem_well_posed(maxRuns, initPoints, Lmin, Lmax, LTmin, LTmax, STmin, STmax, Wmax, materialSet):
def is_problem_well_posed(paramsHolder, optimizerConf, materialSet):
    """
    Check if shield optimization problem constraints are consistent.

    Args:
        maxRuns, initPoints: max runs and init points of the optimization
        Lmin, Lmax (int): Min/max number of layers.
        LTmin, LTmax (float): Min/max thickness of each layer.
        STmin, STmax (float): Min/max total shield thickness.
        Wmax (float): Max normalized weight of shield.
        materials (list of str)

    Returns:
        bool: True if constraints are consistent, False otherwise.
        [str]: list of violation messages if any
    """
    initPoints = optimizerConf.getParam("n_initial_points")
    maxRuns = paramsHolder.get("max_runs")
    Lmin = paramsHolder.get("min_layers")
    Lmax = paramsHolder.get("max_layers")
    LTmin = paramsHolder.get("min_layer_thickness")
    LTmax = paramsHolder.get("max_layer_thickness")
    STmin = paramsHolder.get("min_shield_thickness")
    STmax = paramsHolder.get("max_shield_thickness")
    Wmax = paramsHolder.get("max_shield_weight")
    violations = []
    #return False, ["dummy violation"]

    _, _, materials = materialSet.getMaterialsList()

    # these have to be >= 0
    numeric_paramsnn = [STmin]
    namesnn = ["STmin"]
    iNegVals = 0
    for name, val in zip(namesnn, numeric_paramsnn):
        if val < 0:
            iNegVals = iNegVals + 1
            violations.append(f"{name} must be non negative, got {val}.")
    if (iNegVals > 0):
        return (len(violations) == 0), violations

    # these have to be > 0
    numeric_params = [maxRuns, initPoints, Lmin, Lmax, LTmin, LTmax, STmax, Wmax]
    names = ["MaxRuns", "InitialPoints", "Lmin", "Lmax", "LTmin", "LTmax", "STmax", "Wmax"]
    iNonPosVals = 0
    for name, val in zip(names, numeric_params):
        if val <= 0:
            iNonPosVals = iNonPosVals + 1
            violations.append(f"{name} must be positive, got {val}.")
    if (iNonPosVals > 0):
        return (len(violations) == 0), violations

    if not materials:
        violations.append("No materials were specified.")
        return (len(violations) == 0), violations

    #print(materialSet)
    dens_min = min(materialSet.getDensity(m) for m in materials) if materials else 0
    dens_max = max(materialSet.getDensity(m) for m in materials) if materials else 0


    if ((dens_max <= 0) or (dens_min <= 0)):
        violations.append("Non positive densities are not allowed")
        return (len(violations) == 0), violations

    min_max_runs = initPoints + 1
    if (maxRuns < min_max_runs):
        violations.append("Too low MAX RUNS ! It should be incremented to " + str(min_max_runs)  + " at least.")

    # Feasible thickness range
    feasible_ST_min = Lmin * LTmin
    feasible_ST_max = Lmax * LTmax

    if feasible_ST_min > STmax:
        violations.append(f"Minimum total thickness {feasible_ST_min} exceeds STmax {STmax}.")
    if feasible_ST_max < STmin:
        violations.append(f"Maximum total thickness {feasible_ST_max} is below STmin {STmin}.")

    # Feasible weight range
    feasible_W_min = feasible_ST_min * dens_min
    feasible_W_max = feasible_ST_max * dens_max

    if feasible_W_min > Wmax:
        violations.append(f"Minimum weight {feasible_W_min:.2f} exceeds Wmax {Wmax}.")
    #if feasible_W_max < Wmin:
    #    violations.append(f"Maximum weight {feasible_W_max:.2f} below Wmin {Wmin}.")

    return (len(violations) == 0), violations

