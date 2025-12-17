#from skopt.space import Categorical
from skopt.space import Real, Integer

from logging_utils import init_logger

#self._materials_by_index, self._allow_adjacent_same_materials
from searchsp_util import get_trimmed_layers, shield_has_consec_same_materials, get_trimmed_layers, decode_raw_material_indexes, encodeMaterialsToRaw, is_shield_trimming_on, is_shield_wgt_trimming_on, adjacent_same_materials_allowed

#from misc_util import is_enabled, 

# -------------------------------------
# Same as Base250801 search space builder, PLUS:
# - [new in Adv250813] the shield is trimmed in its tail (i.e. last layers) if its total thickness exceeds maxShieldThick OR if total weight exceeds max shield weight
# - [new in Adv250814] no two consecutive layers can be made of the same material
# -------------------------------------

#repair_function_warnings = build_rep_fun_warnings(num_of_layers, self._min_layers, min_layer_thick, self._min_layer_thick, shield_thick_orig, shield_thick, self._min_shield_thick)
def build_rep_fun_warnings(num_layers, min_num_layers, min_layer_thick_actual, min_layer_thick, shield_thick_pretrim, shield_thick, min_shield_thick):
    rfw = []
    violations_info = []
    if (num_layers < min_num_layers):
        amt = min_num_layers - num_layers
        violations_info.append(("min_num_layers", amt))
    if (min_layer_thick_actual < min_layer_thick):
        amt = min_layer_thick - min_layer_thick_actual
        violations_info.append(("min_layer_thick", amt))
    if ((shield_thick_pretrim >= min_shield_thick) and (shield_thick < min_shield_thick)):
        amt = min_shield_thick - shield_thick
        violations_info.append(("min_shield_thick", amt))
    if (len(violations_info) > 0): 
        wMsg = ", ".join(f"{name} ({amt})" for name, amt in violations_info)
        rfw.append("Trimming-induced constraint violations occurred: " + wMsg)
    return rfw

class SearchSpaceBuilderAdv250814:
    def __init__(self):
        self._materials_by_index = True
        self._max_shield_thick = None
        self._search_space = []
        self._num_layers_idx = None
        self._num_layer_fields = None
        self._layers_params_offset = None
        self._materials_list = None
        self._materials_set = None
        self._max_shield_wgt = None

        self._min_layers = None
        self._min_layer_thick = None
        self._min_shield_thick = None

        #this class can work in both modes, False and True
        self._allow_adjacent_same_materials = adjacent_same_materials_allowed()
        self._sh_trimming_enabled = is_shield_trimming_on()
        self._sh_w_trimming_enabled = is_shield_wgt_trimming_on()

        self._is_initialized = False

    def hasShieldTrimming(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'hasShieldTrimming' cannot be called here, as the search space builder has not been initialized")
        return self._sh_trimming_enabled

    def hasShieldTrimming_Wgt(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'hasShieldTrimming_Wgt' cannot be called here, as the search space builder has not been initialized")
        return self._sh_w_trimming_enabled

    #def init(self, materialsList, minLayers, maxLayers, minLayerThick, maxLayerThick, minShieldThick, maxShieldThick, materialsSet, maxShieldWeight):
    def init(self, paramsHolder, materialsSet):
        _, _, materialsList = materialsSet.getMaterialsList()
        minLayers = paramsHolder.get("min_layers")
        maxLayers = paramsHolder.get("max_layers")
        minLayerThick = paramsHolder.get("min_layer_thickness")
        maxLayerThick = paramsHolder.get("max_layer_thickness")
        minShieldThick = paramsHolder.get("min_shield_thickness")
        maxShieldThick = paramsHolder.get("max_shield_thickness")
        maxShieldWeight = paramsHolder.get("max_shield_weight")

        allow_adj_same_mats = self._allow_adjacent_same_materials
        logger = init_logger()
        logger.info("[searchsp-adv250814] Search space definition - begin (materialsByIndex: " + str(self._materials_by_index) + ")")
        logger.info("[searchsp-adv250814] Has shield trimming (by thickness): " + str(self._sh_trimming_enabled))
        logger.info("[searchsp-adv250814] Has shield trimming (by weight): " + str(self._sh_w_trimming_enabled))

        logger.info("[searchsp-adv250814] Allow same material in adjacent layers: " + str(allow_adj_same_mats))

        self._materials_list = materialsList
        self._max_shield_thick = maxShieldThick
        self._materials_set = materialsSet
        self._max_shield_wgt = maxShieldWeight

        self._min_layers = minLayers
        self._min_layer_thick = minLayerThick
        self._min_shield_thick = minShieldThick

        #We slice params like this:
        # First: num layers (index: 0)
        currIdx = 0
        search_sp = [Integer(minLayers, maxLayers, transform="identity", name="num_layers")]
        self._num_layers_idx = currIdx
        logger.debug("[searchsp-adv250814]    Search space - added num. layers parameter [" + str(currIdx) + "], max: " + str(maxLayers))
        currIdx = currIdx + 1

        # then , offset (index after which layers params start)
        self._layers_params_offset = currIdx

        # then, the layers, one after another, first material index then thickness (from index 1 onwards)
        num_materials = len(materialsList)
        logger.debug("[searchsp-adv250814]  Num. of materials: " + str(num_materials) + ", layers range: [" + str(minLayers) + "-" + str(maxLayers) + "]")
        material_index_min = 0
        for i in range(maxLayers):
            fieldCount = 0

            #material index
            if (allow_adj_same_mats):
                material_index_max = num_materials - 1
            else:
               if (i > 0):
                   material_index_max = num_materials - 2
               else:
                   material_index_max = num_materials - 1

            #material_index_max = (num_materials if (alXlow_adj_same_mats or (i > 1)) else (num_materials - 1)) - 1
            search_sp.append(Integer(material_index_min, material_index_max, transform="identity", name=f"material_index_{i+1}"))
            currIdx = currIdx + 1
            fieldCount = fieldCount + 1
            logger.debug("[searchsp-adv250814]      added material index #" + str(i) + " parameter [" + str(currIdx) + "] (range: " + str(material_index_min) + "-" + str(material_index_max) + ")")

            #thickness
            search_sp.append(Real(minLayerThick, maxLayerThick, transform="normalize", name=f"thickness_{i+1}"))
            currIdx = currIdx + 1
            fieldCount = fieldCount + 1
            logger.debug("[searchsp-adv250814]      added thickness #" + str(i) + " parameter [" + str(currIdx) + "]")

            if (not self._num_layer_fields):
                self._num_layer_fields = fieldCount
                logger.debug("[searchsp-adv250814] Set _num_layer_fields: " + str(self._num_layer_fields))

        #print(str(search_sp))
        logger.debug("[searchsp-adv250814]    Search space - added materials and thickness parameters")
        self._search_space = search_sp
        logger.info("[searchsp-adv250814] Search space definition - complete")

        self._is_initialized = True

    def getValidRawMaterialPlaceholder(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getValidRawMaterialPlaceholder' cannot be called here, as the search space builder has not been initialized")
        defMat = self._materials_list[0]
        #defMat = materialsList[0]
        defRawMatToAppend = self._materials_list.index(defMat) if (self._materials_by_index) else defMat
        return defRawMatToAppend

    def materialsByIndex(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'materialsByIndex' cannot be called here, as the search space builder has not been initialized")
        return self._materials_by_index

    def adjacentSameMaterialAllowed(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'adjacentSameMaterialAllowed' cannot be called here, as the search space builder has not been initialized")
        return self._allow_adjacent_same_materials

    def getSearchSpace(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getSearchSpace' cannot be called here, as the search space builder has not been initialized")
        return self._search_space

    #def getNumLayers(self, params):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getNumLayers' cannot be called here, as the search space builder has not been initialized")
    #    return params[self._num_layers_idx]

    #def getLayerData(self, params, layerIndex):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getLayerData' cannot be called here, as the search space builder has not been initialized")
    #    layerStartIdx = self._layers_params_offset + self._num_layer_fields * layerIndex
    #    #material, thickness
    #    #return (params[layerStartIdx], params[layerStartIdx + 1])
    #    #
    #    # This will return a tuple with exactly num_layer_fields elements starting from layerStartIdx
    #    return tuple(params[layerStartIdx : layerStartIdx + self._num_layer_fields])

    def getMaterialsRawList(self, materials_in_x0):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getMaterialsRawList' cannot be called here, as the search space builder has not been initialized")
        materialsRawList = encodeMaterialsToRaw(self._materials_list, materials_in_x0, self._materials_by_index, self._allow_adjacent_same_materials)
        return materialsRawList

    def decode_x_point(self, params):
        num_of_layers_orig = params[self._num_layers_idx]
        return decode_raw_material_indexes(self._materials_list, params, self._layers_params_offset, num_of_layers_orig, self._num_layer_fields, (not self._allow_adjacent_same_materials))

    def getLayersData(self, params):
        repair_function_warnings = []
        #print("in getLayersData: " + str(params))
        #allow_adj_same_mats = self._allow_adjacent_same_materials
        logger = init_logger()
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250814] Error. Bad Sequence. 'getLayersData' cannot be called here, as the search space builder has not been initialized")
        #num_of_layers = self.getNumLayers(params)
        num_of_layers_orig = params[self._num_layers_idx]

        # move from list_of(index, thickness) -> list_of(material, thickness)
        #decoded_params = decode_raw_material_indexes(self._materials_list, params, self._layers_params_offset, num_of_layers_orig, self._num_layer_fields, (not aXllow_adj_same_mats))
        decoded_params = self.decode_x_point(params)

        #trimmed_layers_data = get_trimmed_layers(decoded_params, num_of_layers_orig, self._max_shield_thick, self._layers_params_offset, self._num_layer_fields, self._sh_trimming_enabled)
        trimmed_layers_data = get_trimmed_layers(decoded_params, num_of_layers_orig, self._max_shield_thick, self._layers_params_offset, self._num_layer_fields, self._sh_trimming_enabled, self._materials_set, self._max_shield_wgt, self._sh_w_trimming_enabled)
        num_of_layers = len(trimmed_layers_data)
        shield_thick_orig = sum(float(decoded_params[self._layers_params_offset + 1 + self._num_layer_fields*i]) for i in range(num_of_layers_orig))
        shield_thick = sum(layer["thickness"] for layer in trimmed_layers_data)
        min_layer_thick = min(layer["thickness"] for layer in trimmed_layers_data)
        if (shield_thick < shield_thick_orig):
            logger.warning(f"[searchsp-adv250814][repfun] The shield was TRIMMED in pre-sim phase to avoid constraints violation: (Num. layers, Thickness): ({num_of_layers_orig}, {shield_thick_orig}) ---> ({num_of_layers}, {shield_thick})")
            repair_function_warnings = build_rep_fun_warnings(num_of_layers, self._min_layers, min_layer_thick, self._min_layer_thick, shield_thick_orig, shield_thick, self._min_shield_thick)
        else:
            logger.debug(f"[searchsp-adv250814] NO SHIELD TRIMMING TOOK PLACE. (Num. layers, Thickness): ({num_of_layers_orig}, {shield_thick_orig}) ---> ({num_of_layers}, {shield_thick})")
        if (shield_has_consec_same_materials(trimmed_layers_data)):
            logger.warning("[searchsp-adv250814] The shield has consecutive layers with same material!")
        return trimmed_layers_data, repair_function_warnings
