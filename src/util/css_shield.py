from logging_utils import init_logger
#from materials_db import MaterialsDatabase
from materials_set import MaterialsSet

class CssShield:
    def __init__(self):
        self._layers = []
        self._layers_geom = []
        self._tot_thickness = 0
        self._stiffness = 0
        self._max_eff_layer_thick = 0
        self._tot_weight = None
        self._nbr_of_layers = 0
        self._tco = 0
        #self._cf_factor = None
        #self._has_consec_same_layers = False
        self._is_initialized = False

    #def init(self, simParams, searchSpaceBldr, matSet: MaterialsSet):
    def init(self, layersDataDict, matSet: MaterialsSet, cf_factor):
        logger = init_logger()
        logger.debug("[shield] Initializing shield")
        #self._cf_factor = cf_factor
        tStiffness = 0
        tLayers = []
        tLayers_geom = []
        tThick = 0
        tWeight = None
        isDbInitialized = (matSet and matSet.GetParentDb().isInitialized())
        if (isDbInitialized):
            tWeight = 0

        #layersDataDict = searchSpaceBldr.getLayersData(simParams)
        num_layers = len(layersDataDict)

        for curLayer in layersDataDict:
            material, thickness = curLayer["material"], curLayer["thickness"]
            tThick = tThick + thickness
            curWeight = None
            curStiff = 0
            wgtDesc = "n.a."
            if (isDbInitialized):
                #thickness is in mm, density in g/cm3, their product is Kg/m2
                #curWeight = thickness * matDb.getDensity(material)
                curWeight = thickness * matSet.getDensity(material)
                tWeight = tWeight + curWeight
                wgtDesc = str(curWeight)
                curStiff = thickness * matSet.getStiffness(material)
                curStiffDesc = str(curStiff)
                tStiffness = tStiffness + curStiff

            logger.debug("[shield] Shield init. Appending layer {" + material + ", thick: " + str(thickness) + ", wgt: " + wgtDesc + ", stiff.: " + curStiffDesc + "}")
            tLayers.append((material, thickness, curWeight, curStiff))
            tLayers_geom.append((material, thickness))
        #print("xxx from internal: " + str(tLayers_geom))
        if (tThick > 0):
            tStiffness = (cf_factor * tStiffness) / tThick
            logger.info("[shield] Stiffness evaluated (CF: " + str(cf_factor) + "): " + str(tStiffness))
        else:
            tStiffness = 0
            logger.warning("[shield] **** Division by zero --> shield stiffness forced to zero")
        self._stiffness = tStiffness

        self._layers = tLayers
        self._layers_geom = tLayers_geom
        logger.debug("[shield] Shield init. Setting tot. thickness: " + str(tThick))
        self._tot_thickness = tThick
        twgt_as_str = "n.a." if tWeight is None else str(tWeight)
        logger.debug("[shield] Shield init. Setting tot. weight: " + twgt_as_str)
        self._tot_weight = tWeight
        self._nbr_of_layers = num_layers

        #merged_layers will merge together the consecutive layers made of same materials, adding the thicknesses
        merged_layers = []
        foundConsecSameMats = 0
        for material, thickness, _, _ in self._layers:
            if (merged_layers and merged_layers[-1][0] == material):
                merged_layers[-1] = (material, merged_layers[-1][1] + thickness)
                foundConsecSameMats = foundConsecSameMats + 1
            else:
                merged_layers.append((material, thickness))
        self._max_eff_layer_thick = max(thickness for _, thickness in merged_layers)
        logger.debug("[shield] Shield init. Max layer effective thickness: " + str(self._max_eff_layer_thick))

        #self._has_consec_same_layers = (foundConsecSameMats > 0)
        if (foundConsecSameMats > 0):
            logger.debug("[shield] **** The shield has consecutive layers made of the same material (occurrences: " + str(foundConsecSameMats) + ") ***")

        self._is_initialized = True

    #def getLayers(self):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[shield] ERROR. Bad Sequence: 'getLayers' cannot be called here, as the shield has not been initialized!")
    #    return self._layers


    def getStiffness(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getStiffness' cannot be called here, as the shield has not been initialized!")
        return self._stiffness

    # Total Cost of Ownership - to be implemented
    def getTCO(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getTCO' cannot be called here, as the shield has not been initialized!")
        return self._tco

    #returns ONLY fields that are useful to build geom, to incapsulate only here other details
    def getLayersGeomInfo(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getLayersGeomInfo' cannot be called here, as the shield has not been initialized!")
        return self._layers_geom

    def getNumOfLayers(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getNumOfLayers' cannot be called here, as the shield has not been initialized!")
        return self._nbr_of_layers

    def getTotWeight(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getTotWeight' cannot be called here, as the shield has not been initialized!")
        return self._tot_weight

    def getTotThickness(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getTotThickness' cannot be called here, as the shield has not been initialized!")
        return self._tot_thickness

    #returns the size of the largest layer. Takes into account consecutive identical layer, eg if we have, consecutively, (plastic, 2.1), (plastic, 3.2)
    #this will be regarded as (plastic 5.3)
    def getLargestEffLayerSz(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getLargestEffLayerSz' cannot be called here, as the shield has not been initialized!")
        return self._max_eff_layer_thick

    #def hasConsecutiveDupMaterials(self):
    #    if (not self._is_initialized):
    #        raise RuntimeError("[shield] ERROR. Bad Sequence: 'hasConsecutiveDupMaterials' cannot be called here, as the shield has not been initialized!")
    #    return self._has_consec_same_layers
    ##    logger = init_logger()
    ##    logger.debug("[shield] Evaluating consecutive layers of the same material")
    ##    layers = self._layers
    ##    for i in range(len(layers) - 1):
    ##        if layers[i][0] == layers[i + 1][0]:
    ##            logger.debug("Duplicate layers found: #" + str(i) + " and subsequent")
    ##            return True
    ##    return False

    def getLayersDesc(self):
        if (not self._is_initialized):
            raise RuntimeError("[shield] ERROR. Bad Sequence: 'getLayersDesc' cannot be called here, as the shield has not been initialized!")
        layers_desc = ", ".join(f"{mat} ({thickn:.4f})" for mat, thickn, _, _ in self._layers)
        return (layers_desc)

