from skopt.space import Categorical, Real, Integer

from logging_utils import init_logger

from searchsp_util import shield_has_consec_same_materials, get_trimmed_layers, encodeMaterialsToRaw, is_shield_trimming_on, is_shield_wgt_trimming_on

# -------------------------------------
# Same as Base250801 search space builder, PLUS:
# - the shield is trimmed in its tail (i.e. last layers) if its total thickness exceeds maxShieldThick OR if total weight exceeds max shield weight
# -------------------------------------

class SearchSpaceBuilderAdv250813:
    def __init__(self):
        self._materials_by_index = False
        self._max_shield_thick = None
        self._search_space = []
        self._num_layers_idx = None
        self._num_layer_fields = None
        self._layers_params_offset = None
        self._sh_trimming_enabled = is_shield_trimming_on()
        self._materials_set = None
        self._sh_w_trimming_enabled = is_shield_wgt_trimming_on()

        #this class is not equipped for any different. do not modify
        self._allow_adjacent_same_materials = True

        self._is_initialized = False

    def hasShieldTrimming(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'hasShieldTrimming' cannot be called here, as the search space builder has not been initialized")
        return self._sh_trimming_enabled

    def hasShieldTrimming_Wgt(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'hasShieldTrimming_Wgt' cannot be called here, as the search space builder has not been initialized")
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


        logger = init_logger()
        logger.info("[searchsp-adv250813] Search space definition - begin (materialsByIndex: " + str(self._materials_by_index) + ")")
        logger.info("[searchsp-adv250813] Has shield trimming (by thickness): " + str(self._sh_trimming_enabled))
        logger.info("[searchsp-adv250813] Has shield trimming (by weight): " + str(self._sh_w_trimming_enabled))
        self._materials_list = materialsList
        self._max_shield_thick = maxShieldThick
        self._materials_set = materialsSet
        self._max_shield_wgt = maxShieldWeight

        #We slice params like this:
        # First: num layers (index: 0)
        currIdx = 0
        search_sp = [Integer(minLayers, maxLayers, name="num_layers")]
        self._num_layers_idx = currIdx
        logger.info("[searchsp-adv250813]    Search space - added num. layers parameter [" + str(currIdx) + "]")
        currIdx = currIdx + 1

        # then , offset (index after which layers params start)
        self._layers_params_offset = currIdx

        # then, the layers, one after another, first material then thickness (from index 1 onwards)
        for i in range(maxLayers):
            fieldCount = 0

            #material
            search_sp.append(Categorical(materialsList, name=f"material_{i+1}"))
            currIdx = currIdx + 1
            fieldCount = fieldCount + 1
            logger.debug("[searchsp-adv250813]      added material #" + str(i) + " parameter [" + str(currIdx) + "]")

            #thickness
            search_sp.append(Real(minLayerThick, maxLayerThick, name=f"thickness_{i+1}"))
            currIdx = currIdx + 1
            fieldCount = fieldCount + 1
            logger.debug("[searchsp-adv250813]      added thickness #" + str(i) + " parameter [" + str(currIdx) + "]")

            if (not self._num_layer_fields):
                self._num_layer_fields = fieldCount
                logger.debug("[searchsp-adv250813] Set _num_layer_fields: " + str(self._num_layer_fields))

        logger.info("[searchsp-adv250813]    Search space - added materials and thickness parameters")
        self._search_space = search_sp
        logger.info("[searchsp-adv250813] Search space definition - complete")

        self._is_initialized = True

    def decode_x_point(self, params):
        #As this implementation does not do any encoding/decoding, and raw-actual structures and formats are the same, this is simply an identity
        return params

    def getMaterialsRawList(self, materials_in_x0):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getMaterialsRawList' cannot be called here, as the search space builder has not been initialized")
        materialsRawList = encodeMaterialsToRaw(self._materials_list, materials_in_x0, self._materials_by_index, self._allow_adjacent_same_materials)
        return materialsRawList

    def getValidRawMaterialPlaceholder(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getValidRawMaterialPlaceholder' cannot be called here, as the search space builder has not been initialized")
        defMat = self._materials_list[0]
        #defMat = materialsList[0]
        defRawMatToAppend = self._materials_list.index(defMat) if (self._materials_by_index) else defMat
        return defRawMatToAppend

    def adjacentSameMaterialAllowed(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'adjacentSameMaterialAllowed' cannot be called here, as the search space builder has not been initialized")
        return self._allow_adjacent_same_materials

    def materialsByIndex(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'materialsByIndex' cannot be called here, as the search space builder has not been initialized")
        return self._materials_by_index

    def getSearchSpace(self):
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getSearchSpace' cannot be called here, as the search space builder has not been initialized")
        return self._search_space

    #def getNumLayers(self, params):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getNumLayers' cannot be called here, as the search space builder has not been initialized")
    #    return params[self._num_layers_idx]

    #def getLayerData(self, params, layerIndex):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getLayerData' cannot be called here, as the search space builder has not been initialized")
    #    layerStartIdx = self._layers_params_offset + self._num_layer_fields * layerIndex
    #    #material, thickness
    #    #return (params[layerStartIdx], params[layerStartIdx + 1])
    #    #
    #    # This will return a tuple with exactly num_layer_fields elements starting from layerStartIdx
    #    return tuple(params[layerStartIdx : layerStartIdx + self._num_layer_fields])

    def getLayersData(self, params):
        repair_fun_warnings = []
        logger = init_logger()
        if (not self._is_initialized):
            raise RuntimeError("[searchsp-adv250813] Error. Bad Sequence. 'getLayersData' cannot be called here, as the search space builder has not been initialized")
        #num_of_layers = self.getNumLayers(params)
        num_of_layers_orig = params[self._num_layers_idx]
        trimmed_layers_data = get_trimmed_layers(params, num_of_layers_orig, self._max_shield_thick, self._layers_params_offset, self._num_layer_fields, self._sh_trimming_enabled, self._materials_set, self._max_shield_wgt, self._sh_w_trimming_enabled)
        num_of_layers = len(trimmed_layers_data)
        shield_thick_orig = sum(float(params[self._layers_params_offset + 1 + self._num_layer_fields*i]) for i in range(num_of_layers_orig))
        shield_thick = sum(layer["thickness"] for layer in trimmed_layers_data)
        if (shield_thick < shield_thick_orig):
            logger.warning(f"[searchsp-adv250813] The shield was TRIMMED in pre-sim phase to avoid constraints violation: (Num. layers, Thickness): ({num_of_layers_orig}, {shield_thick_orig}) ---> ({num_of_layers}, {shield_thick})")
        else:
            logger.debug(f"[searchsp-adv250813] NO SHIELD TRIMMING TOOK PLACE. (Num. layers, Thickness): ({num_of_layers_orig}, {shield_thick_orig}) ---> ({num_of_layers}, {shield_thick})")
        if (shield_has_consec_same_materials(trimmed_layers_data)):
            logger.warning("[searchsp-adv250813] The shield has consecutive layers with same material!")
        return trimmed_layers_data, repair_fun_warnings
