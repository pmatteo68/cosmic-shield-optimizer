# common functions that can be leveraged by all the search space related functionalities and/or by the search space builders

#from searchsp_util import shield_has_consec_same_materials, get_trimmed_layers, decode_raw_params, encodeMaterialsToRaw
from misc_util import is_enabled
from logging_utils import init_logger

def is_shield_trimming_on():
    return is_enabled("CSS_OPT_SHIELD_TRIMMING")

def is_shield_wgt_trimming_on():
    return is_enabled("CSS_OPT_SHIELD_WGT_TRIMMING")

def adjacent_same_materials_allowed():
    return is_enabled("CSS_OPT_ADJL_SAME_MAT")

# trims the shield if exceeds the max shield thickness/weight. 'params' is the set of parameters passed by the gp_minimize to the obj function upon the generic iteration
def get_trimmed_layers(params, num_of_layers, max_shield_thickness, layers_offset, num_fields_per_layer, is_th_trimming_enab, materials_set, max_shield_weight, is_wgt_trimming_enab):
    logger = init_logger()
    result_o = []
    if (not (is_th_trimming_enab or is_wgt_trimming_enab)):
        logger.debug("Shield trimming is DISABLED - returning original layers structure AS IS")
        for i in range(num_of_layers):
            material = params[layers_offset + num_fields_per_layer*i]
            thickness = float(params[layers_offset + 1 + num_fields_per_layer*i])
            result_o.append({"material": material, "thickness": thickness})
        return result_o

    result = []
    logger.debug("Shield trimmed is ENABLED (thick: " + str(is_th_trimming_enab) + ", weight: " + str(is_wgt_trimming_enab) + "), moving on with trimming")
    accum_th = 0.0
    accum_wgt = 0.0
    #0, 1, .... num_layers-1
    for i in range(num_of_layers):
        allowed_th = max_shield_thickness - accum_th
        allowed_wgt = max_shield_weight - accum_wgt
        if ((allowed_th <= 0) or (allowed_wgt <= 0)):
            break

        #layers offset counts for the fact that layers come after something else
        material = params[layers_offset + num_fields_per_layer*i]
        thickness = float(params[layers_offset + 1 + num_fields_per_layer*i])
        cl_density = materials_set.getDensity(material)
        cl_weight = thickness * cl_density
        trimmed = min(min(thickness, allowed_th), (min(cl_weight, allowed_wgt) / cl_density))

        if trimmed > 0.0:
            result.append({"material": material, "thickness": trimmed})
            accum_th += trimmed
            accum_wgt += trimmed * cl_density

        if ((accum_th >= max_shield_thickness) or (accum_wgt >= max_shield_weight)):
            break

    #if sum(float(params[2 + 2*i]) for i in range(num_of_layers)) != sum(layer["thickness"] for layer in result):
    #    print("[TRIMDEBUG] Original layers from params:", [{"material": params[1 + 2*i], "thickness": float(params[2 + 2*i])} for i in range(num_of_layers)])
    #    print("[TRIMDEBUG] Trimmed result:", result)

    return result


#layers = [
#    {"material": "wood", "thickness": 1.0},
#    {"material": "wood", "thickness": 2.0},
#    {"material": "iron", "thickness": 3.0},
#]
def shield_has_consec_same_materials(layers):
    hasAny = any(
        layers[i]["material"] == layers[i+1]["material"]
        for i in range(len(layers) - 1)
    )
    return hasAny

#rotated indexes, simple indexes or materials
def encodeMaterialsToRaw(materials, names, materials_by_index, allow_adjacent_same_materials):
    """
    materials : full list of material names
    names     : sequence of material names (subset, i.e. a given shield) for layers
    returns   : materials, simple indexes or encoded indices (first ∈ [0..num-1], rest ∈ [0..num-2]), depending on the request
    """
    for mat_name in names:
        if mat_name not in materials:
            raise ValueError(f"[data_domain] DATA ERROR. Material '{mat_name}' not found in materials list")

    if (not materials_by_index):
        return names

    if (materials_by_index and allow_adjacent_same_materials):
        plain_indexes = [materials.index(mat_name) for mat_name in names]
        return plain_indexes
    

    encoded = []
    num = len(materials)

    #print("\n\nmaterials: " + str(materials))
    #print("x0shield: " + str(names))
    # first layer: direct index
    prev_idx = materials.index(names[0])
    encoded.append(prev_idx)

    # next layers: rotated index
    for mat_name in names[1:]:
        next_idx = materials.index(mat_name)
        rotated = list(range(prev_idx + 1, num)) + list(range(0, prev_idx + 1))
        v = rotated.index(next_idx)
        encoded.append(v)
        prev_idx = next_idx

    #print("\n\nx0shield rotated indexes: " + str(encoded) + "\n")
    return encoded

def decode_raw_material_indexes(materials, params, index_offset, num_layers, fields_per_layer, matching_adj_mat_not_allowed):

    #print(str(params))
    prev_idx = None

    #init variable to be returned
    decoded = [num_layers]

    # num materials
    num_materials = len(materials)

    # layer 1 (index in [0..num_materials-1])
    if (matching_adj_mat_not_allowed):
        prev_idx = int(params[index_offset])
    decoded.append(materials[int(params[index_offset])])
    # from 1 to. ...other fields (in layer 1)
    for j1 in range(1, fields_per_layer):
        # for j1==1 it's thickness, but this code is more general as we may introduce in future something else on top of the thickness
        otherParam1 = params[index_offset + j1]
        decoded.append(otherParam1)

    # layers 2..num_layers (index in [0..num_materials-2], decoded via rotation)
    for layer in range(2, num_layers + 1):
        # position of this layer's encoded index
        i = index_offset + fields_per_layer * (layer - 1)

        if (matching_adj_mat_not_allowed):
            # 0..num_materials-2
            v = int(params[i])
            rotated = list(range(prev_idx + 1, num_materials)) + list(range(0, prev_idx + 1))
            #print("\n[" + str(layer) + "] v: "+ str(v) + ", rotated: " + str(rotated))
            next_idx = rotated[v]
            decoded.append(materials[next_idx])
        else:
            # 0..num_materials-1 -> direct index
            mat_idx = int(params[fields_per_layer * layer - 1])
            decoded.append(materials[mat_idx])

        # from 1 to. ...other fields (in layers 2, ...num_layers)
        for j in range(1, fields_per_layer):
           # for j==1 it's thickness, but this code is more general as we may introduce in future something else on top of the thickness
           otherParam = params[i + j]
           decoded.append(otherParam)

        if (matching_adj_mat_not_allowed):
           prev_idx = next_idx

    return decoded

