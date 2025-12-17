import copy
import json

from logging_utils import init_logger
from css_metadata import build_geomconf_path

def create_geometry_conf(run_id, conf_dir, conf_templ_data, common_layer_data, shield):
    logger = init_logger()
    logger.info("[geom][" + run_id + "] Geometry configuration creation: begin")
    additional_layers = shield.getLayersGeomInfo()
    geom_data = copy.deepcopy(conf_templ_data)
    layers = geom_data.get("layers", [])
    if not layers:
        raise ValueError("No 'layers' key found in template, or it's empty.")

    # Insert new layers BEFORE any present layer (typically the template contains the detector)
    insert_index = 0
    #insert_index = len(layers) - 1

    new_layers = []
    for idx, (material, thickness) in enumerate(additional_layers, start=1):
        formatted_idx = f"L{idx:03d}"
        layer_name = f"{formatted_idx}-{material}"
        new_layer = {
            "name": layer_name,
            "material": material,
            "thickness": thickness
        }
        new_layer.update(common_layer_data)
        new_layers.append(new_layer)
        logger.debug("[geom][" + run_id + "] Added new layer: " + layer_name + " (" + material + ", " + str(thickness) + ")")

    layers[insert_index:insert_index] = new_layers
    logger.debug("[geom][" + run_id + "] New layers ADDED")

    # Save back
    geom_conf_path = build_geomconf_path(conf_dir, run_id)
    logger.info("[geom][" + run_id + "] Saving geometry configuration (" + geom_conf_path + ")")
    with open(geom_conf_path, 'w') as f:
        json.dump(geom_data, f, indent=2)
    logger.info("[geom][" + run_id + "] Geometry configuration saved.")
    return geom_conf_path

def get_geom_config(geomTemplPath, layerCfgPath):
    logger = init_logger()
    logger.info("[geom] Retrieving geometry template (" + geomTemplPath + ")")
    with open(geomTemplPath, 'r') as gt:
        geom_config_templ_info = json.load(gt)
    logger.info("[geom] Retrieving layer common configuration (" + layerCfgPath + ")")
    with open(layerCfgPath, 'r') as lc:
        layer_cfg_data = json.load(lc)
        comm_layer_info = layer_cfg_data["layerCommonProps"]
    return geom_config_templ_info, comm_layer_info

