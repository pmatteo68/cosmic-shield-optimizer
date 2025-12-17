from logging_utils import init_logger

# -------------------------------------
# Post-simulation logic
# -------------------------------------
def post_sim_logic(res, prv_attempts, irq_Manager, hist_Manager):
    logger = init_logger()
    x_iters_desc = str(len(res.x_iters)) if getattr(res, "x_iters", None) is not None else "n.a."
    logger.info("[opttrace] Iterations completed: " + x_iters_desc + " (started from: " + str(prv_attempts) + ") \n")

    if (irq_Manager.foundIRQ()):
        irq_Manager.processIRQ()
        hist_Manager.updateHistory(res)
        logger.warning("[opttrace][driver] INTERRUPT REQUEST INTERCEPTED. Optimization run is shutting down.")
        return True
    else:
        return False

