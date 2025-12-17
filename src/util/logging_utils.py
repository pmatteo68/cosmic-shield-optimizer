import os
import logging
#from rich.logging import RichHandler
#from rich.console import Console

#DEBUG, INFO, WARNING, ERROR, CRITICAL
DEFAULT_LOG_LEVEL = "INFO"

#class RichColorFormatter(logging.Formatter):
#    LEVEL_STYLES = {
#        "DEBUG": "[dim cyan]DEBUG[/dim cyan]",
#        "INFO": "[white]INFO[/white]",
#        "WARNING": "[bold yellow]WARNING[/bold yellow]",
#        "ERROR": "[bold red]ERROR[/bold red]",
#        "CRITICAL": "[reverse bold red]CRITICAL[/reverse bold red]",
#    }
#
#    def format(self, record):
#        levelname = record.levelname
#        if levelname in self.LEVEL_STYLES:
#            record.levelname = self.LEVEL_STYLES[levelname]
#        return super().format(record)

#logger_level: int = logging.INFO,
def init_logger(
    logger_level: int = None,
    logger_format: str = "%(levelname)s [%(asctime)s] [%(threadName)s] - %(message)s") -> logging.Logger:

    # Create a console with a very wide width to avoid wrapping
    #myConsole = Console(width=9999)

    level_name = os.getenv("CSS_OPT_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    logger_level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler()
    #handler = RichHandler(
    #    show_path=False,
    #    show_time=False,     # disable Rich's own timestamp
    #    show_level=False,    # disable Rich's own level formatting
    #    markup=True
    #    #console=myConsole
    #)

    #formatter = RichColorFormatter(logger_format, datefmt="%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(logger_format, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logger_level,
        handlers=[handler],
        force=True
    )
    return logging.getLogger(__name__)

def format_iter_log(simul_id, cshield, num_rep_fun_warnings, constr_pre_ok, constr_post_ok, target_met, obj_fun_val, kpis_str, err_info):
    sim_id_rep = simul_id or "na"
    log_line = "[opttrace][driver][" + sim_id_rep + "] GEOMETRY"

    geom_desc = ": na"
    if (cshield):
        geom_desc = " (layers: " + str(cshield.getNumOfLayers()) + "): [" + cshield.getLayersDesc() + "]"
    log_line = log_line + geom_desc

    rfw_part = "Rep. fun. warn.: " + str(num_rep_fun_warnings)
    log_line = log_line + ", " + rfw_part

    cpre_part = "Constr. PRE: na"
    if constr_pre_ok is not None:
        cpre_part = "Constr. PRE: " + str(constr_pre_ok)
    log_line = log_line + ", " + cpre_part

    cpost_part = "Constr. POST: na"
    if constr_post_ok is not None:
        cpost_part = "Constr. POST: " + str(constr_post_ok)
    log_line = log_line + ", " + cpost_part


    obj_part = "OBJ: na"
    if (obj_fun_val is not None):
        obj_part = "OBJ: " + str(obj_fun_val)
    log_line = log_line + ", " + obj_part

    kpi_part = "KPIs: na"
    if (kpis_str is not None):
        kpi_part = "KPIs: [" + kpis_str + "]"
    log_line = log_line + ", " + kpi_part

    tmet_part = "Target met: na"
    if (target_met is not None):
        tmet_part = "Target met: " + str(target_met)
    log_line = log_line + ", " + tmet_part

    if (err_info is not None):
        err_part = "Failure: " + err_info
        log_line = log_line + ", " + err_part

    return log_line

