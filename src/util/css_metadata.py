
from datetime import datetime

#useful to build the ID of the optimization run
RUNTIMESTAMP_FMT = "%y%m%d%H%M%S"

#useful for geometry file creation
GEOM_FILENAME_PFIX = "geometry_"
GEOM_FILENAME_EXT = "json"

#useful for KPIs filename definition
KPI_FILE_DELIM = ";"
OUT_DIR_PFIX = "r"
KPI_FILE_PFIX = "glob_kpis_"
KPI_FILE_EXT = "csv"

def create_run_id():
    run_idf = datetime.now().strftime(RUNTIMESTAMP_FMT)
    return run_idf

def build_geomconf_path(conf_dir, run_id):
    gconf_path = conf_dir + "/" + GEOM_FILENAME_PFIX + run_id + '.' + GEOM_FILENAME_EXT
    return gconf_path

def create_kpi_filepath(out_root_dir, run_id):
    k_path = out_root_dir + "/" + OUT_DIR_PFIX + run_id + "/" + KPI_FILE_PFIX + run_id + "." + KPI_FILE_EXT
    return k_path, KPI_FILE_DELIM

