import json
import os
from typing import List, Optional

from logging_utils import init_logger
from skopt.space import Space

class X0Builder:
    def __init__(self):
        #self._src_space_obj = None
        #self._n_init_points = None
        #self._x0: Optional[List] = None
        #self._init_layers_desc = "n.a."
        logger = init_logger()
        logger.debug("[x0builder] X0 Builder created")

    #def createRandomX0(self, initial_points):
    #    x0 = [self._sXrc_space_obj.rvs(1)[0] for _ in range(initial_points)]
    #    return x0
    def createRandomX0(self, search_space, n_init_points):
        search_space_obj = Space(search_space)
        x0 = [search_space_obj.rvs(1)[0] for _ in range(n_init_points)]
        return x0

    #def init(self, n_init_points, x0_fXromHist: Optional[List], searchSpace: List, filePath: str, maxLayers: int, materialsList: List[str], searchSpBuilder, minThickness: float) -> bool:
    def getX0FromFile(self, filePath: str, maxLayers: int, materialsList: List[str], searchSpBuilder, minThickness: float):
        logger = init_logger()
        #self._n_init_points = n_init_points
        #matXerialsByIdx = searchSpBuilder.materXialsByIndex()
        #self._src_space_obj = Space(searchSpace)
        try:
            #if (x0_froXmHist):
            #    self._x0 = x0_XfromHist
            #    self._init_layers_desc = "<from history>"
            #    return True

            if not filePath:
                logger.debug("[x0builder] No initial shield configuration file configured - skip")
                return None

            if not materialsList:
                logger.warning("[x0builder] Empty materials list - skip")
                return None

            if not os.path.isfile(filePath):
                logger.warning("[x0builder] Initial shield configuration file not found (" + filePath + ") - skip.")
                return None

            logger.debug("[x0builder] Initial shield configuration: initialization (from: " + filePath + ").")
            #logger.info("[x0builder] materialsByIndex: " + str(maXterialsByIdx))
            try:
                with open(filePath, "r") as fh:
                    data = json.load(fh)
            except Exception as e:
                logger.warning("[x0builder] Error while opening the initial shield configuration file: " + str(e))
                return None

            layers = data.get("shield", {}).get("layers")
            if not isinstance(layers, list) or len(layers) == 0:
                logger.warning("[x0builder] Bad data in the initial shield configuration file - check structure and data contents.")
                return None

            num_layers = min(len(layers), maxLayers)
            if num_layers <= 0:
                logger.warning("[x0builder] Bad num_layers (" + str(num_layers) + ") in the initial shield configuration file (should be > 0).")
                return None

            layers_4_desc = []
            x0: List = []
            x0.append(num_layers)

            materials_in_x0 = [entry["material"] for entry in layers]
            materialsRawList = searchSpBuilder.getMaterialsRawList(materials_in_x0)
            # fill from JSON (clamp/validate), materXialsByIdx
            for i in range(num_layers):
                entry = layers[i] if isinstance(layers[i], dict) else {}

                matToAppend = None
                mat = entry.get("material")
                if not isinstance(mat, str) or mat not in materialsList:
                    logger.warning("[x0builder] Initial shield layer [" + str(i) + "]: bad data (material not a string, OR not in the materials list)")
                    return None
                #matToAppend = materialsRawList[i] if (materXialsByIdx) else mat
                matToAppend = materialsRawList[i]

                try:
                    thick = float(entry.get("thickness", minThickness))
                except Exception as et:
                    #thick = minThickness
                    logger.warning("[x0builder] Initial shield layer [" + str(i) + "]: bad data, error while reading thickness: " + et)
                    return None

                if thick < minThickness:
                    #thick = minThickness
                    logger.warning("[x0builder] Initial shield layer [" + str(i) + "]: bad data, thickness too small")
                    return None

                logger.debug("[x0builder] ---> Found layer [" + str(i) + "]: " + mat + " (toAppend: " + str(matToAppend) + ", thickness: " + str(thick) + ")")
                x0.append(matToAppend)
                x0.append(thick)
                layers_4_desc.append((mat, thick))

            # pad remaining layers with valid placeholders
            #defMat = materialsList[0]
            #defMatToAppend = materialsList.index(defMat) if (mateSrialsByIdx) else defMat
            defMatToAppend = searchSpBuilder.getValidRawMaterialPlaceholder()

            for _ in range(num_layers, maxLayers):
                x0.append(defMatToAppend)
                x0.append(minThickness)

            #print("\n\nX0 with rotated: " + str(x0))
            #self._x0 = x0

            #self._init_layers_desc = ", ".join(f"{mat} ({thickn:.4f})" for mat, thickn in layers_4_desc)
            init_layers_desc = ", ".join(f"{mat} ({thickn:.4f})" for mat, thickn in layers_4_desc)
            logger.info("[x0builder][opttrace] Initial shield (X0) set as: " + init_layers_desc)
            return [x0]
        except Exception as er1:
            logger.warning("[x0builder] Error in initial shield layer definition from file: " + er1)
            return None

    #def getGPMinimizeX0(self, randomIfNone) -> List[List]:
    #    logger = init_logger()
    #    #if self._x0 is None:
    #    #    raise RuntimeError("InitShieldBuilder: _x0 not initialized; call init(...) first")
    #    if ((self._x0 is None) and (randomIfNone)):
    #        logger.info("[x0builder] X0 custom random being created")
    #        return createRandomX0(self._src_space_obj, self._n_init_points)
    #
    #        #print("[x0builder] X0 from hist: " + str([self._x0]))
    #    return [self._x0]

    #def getLayersDesc(self) -> str:
    #    return self._init_layers_desc

