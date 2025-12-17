import subprocess
from logging_utils import init_logger

from kpis_utils import KPIHolder
from geom_utils import create_geometry_conf
from css_metadata import create_run_id

# -------------------------------------
# Run simulation
# -------------------------------------
def run_simulation(shield, gconf_trg_dir, conf_template_data, comm_layer_data, sim_script_path, out_data_dir, objFunEvaluator, trgReachedEvaluator):
    logger = init_logger()
    logger.debug("[driver] Run simulation: begin")

    simulation_id = create_run_id()
    logger.info("[driver][" + simulation_id + "] Simulation ID established")
    geom_path = create_geometry_conf(simulation_id, gconf_trg_dir, conf_template_data, comm_layer_data, shield)
    #for i, (material, thickness) in enumerate(layers):
    #    shield_materials += [f"--material{i+1}", material, f"--thickness{i+1}", str(thickness)]

    layers_desc = shield.getLayersDesc()
    logger.info("[driver][" + simulation_id + "] Calling simulation {script: " + sim_script_path + ", geometry: " + geom_path + ", layers: " + layers_desc + "} ..")
    #subprocess.run([sim_script_path] + shield_materials, check=True)
    #subprocess.run([sim_script_path] + ['batch'] + [simulation_id], check=True)
    subprocess.run([sim_script_path] + [simulation_id], check=True)

    logger.info("[driver][" + simulation_id + "] Simulation complete")

    #shield.getTotThickness()
    kpis = KPIHolder()
    kpis.load(simulation_id, out_data_dir, objFunEvaluator, trgReachedEvaluator)
    return simulation_id, kpis


