import json
import os

from logging_utils import init_logger
#from materials_list import MaterialsList
from materials_set import MaterialsSet

class MaterialsDatabase:
    def __init__(self):
        self._materials = {}
        #self._num_items = 0
        self._is_initialized = False
        #self._materialsList = []

    def init(self, filePath: str) -> bool:
        logger = init_logger()
        if (filePath is None):
            logger.debug("[matdb] Materials database initialization will NOT take place by user choice")
            return False

        logger.info("[matdb] Materials database initialization ongoing (source: " + filePath + ")")

        # Check if file exists
        if not os.path.isfile(filePath):
            logger.error("[matdb] File not found (or it was impossible to open)");
            return False

        try:
            with open(filePath, 'r') as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("[matdb] Error while opening file: " + type(e).__name__ + ", " + str(e))
            return False

        # Validate structure
        materials = data.get("materials", [])
        if not materials or not isinstance(materials, list):
            logger.error("[matdb] The specified file contents seem not as expected.")
            return False

        iLoaded = 0
        temp_map = {}
        #temp_list = []
        dup_materials = []
        entryIdx = 0
        for entry in materials:
            mname = entry.get("matname")
            mdensity = entry.get("matdensity")
            young_m = entry.get("mat_E")
            if not mname or not isinstance(mdensity, (int, float)) or mdensity <= 0 or not isinstance(young_m, (int, float)) or young_m <= 0:
                logger.error("[matdb] [item #" + str(entryIdx) + "] Error: bad item (name: " + (mname or "n.a.") + ")")
                return False
            if (mname in temp_map):
                if mname not in dup_materials:
                    dup_materials.append(mname)
            else:
                iLoaded = iLoaded + 1
                #temp_map[mname] = mdensity
                mat_dict = {"density": mdensity, "young_m": young_m}
                temp_map[mname] = mat_dict
                #temp_list.append(mname)
                mat_item_desc = ", ".join(f"{k}={v}" for k, v in mat_dict.items())
                logger.debug("[matdb] Item [" + str(iLoaded) + "] loaded: " + mname + " (" + mat_item_desc + ")")
            entryIdx = entryIdx + 1

        if (not (iLoaded > 0)):
            logger.error("[matdb] No item found")
            return False

        num_dups = len(dup_materials)
        if (num_dups > 0):
            dup_mats_as_str = ", ".join(dup_materials)
            logger.warning("[matdb] Found duplicate items (" + str(num_dups) + "): " + dup_mats_as_str + ". Items in the materials database should be distinct, i.e. ALL DIFFERENT!!")
        self._materials = temp_map
        num_items = len(self._materials)
        self._is_initialized = (num_items > 0)
        logger.info("[matdb] Materials database loaded successfully (items: " + str(num_items) + ")")
        return True

    def isInitialized(self) -> bool:
        return (self._is_initialized)

    def getField(self, material_name: str, field_name: str):
        logger = init_logger()
        if (not (self._is_initialized)):
            raise RuntimeError("ERROR. Bad Sequence. 'getgetField' cannot be called here, as the materials database is not initialized")
        retVal = None
        mat_entry = self._materials.get(material_name)
        if (not (mat_entry is None)):
            retVal = mat_entry.get(field_name)
        if (retVal is None):
            logger.warning("[matdb] Item not found (key: " + material_name + ", field: " + field_name + ")")
        else:
            logger.debug("[matdb] Item found (key: " + material_name + ", field: " + field_name + ": " + str(retVal) + ")")
        return retVal


    def getDensity(self, material_name: str):
        return self.getField(material_name, "density")

    def getStiffness(self, material_name: str):
        return self.getField(material_name, "young_m")

    #def contains(self, matList: MaterialsList, withAssertion: bool) -> bool:
    def contains(self, matSet: MaterialsSet, withAssertion: bool) -> bool:
        missing_items = []
        logger = init_logger()
        #listDesc, _, passedList = matList.getMaterials()
        listDesc, _, passedList = matSet.getMaterialsList()
        for curItem in passedList:
            if curItem not in self._materials and curItem not in missing_items:
                missing_items.append(curItem)
        num_missing = len(missing_items)
        if (num_missing > 0):
            missing_as_str = ", ".join(missing_items)
            missingItemsMsg = "[matdb] Materials set (" + listDesc + ") contains items which are missing in the materials database (total: " + str(num_missing) + "): " + missing_as_str
            if (withAssertion):
                logger.error(missingItemsMsg)
            else:
                logger.debug(missingItemsMsg)
            return False

        logger.debug("[matdb] Materials set (" + listDesc + ") is entirely contained in the materials database")
        return True

    #def assertContains(self, matList: MaterialsList):
    #    if (not self.contains(matList, withAssertion=True)):
    #        raise ValueError("ERROR. Materials list contains items that are not contained in the materials database!")
    def assertContains(self, matSet: MaterialsSet):
        if (not self.contains(matSet, withAssertion=True)):
            raise ValueError("ERROR. Materials set  contains items that are not contained in the materials database!")

    def reduceTo(self, materialsLists):
        logger = init_logger()
        if (not (self._is_initialized)):
            raise RuntimeError("ERROR. Bad Sequence. 'reduceTo' cannot be called here, as the materials database is not initialized")
        if (not (len(materialsLists or []) > 0)):
            logger.debug("[matdb] In-memory replica reduction will not take place as no lists were specified, or they were empty.")
            return

        logger.debug("[matdb] Size before reduction: " + str(len(self._materials)))
        keys_to_keep = set(k for sublist in materialsLists for k in sublist)
        num_items_pre = len(self._materials)
        self._materials = {k: v for k, v in self._materials.items() if k in keys_to_keep}
        num_items = len(self._materials)
        if (num_items < num_items_pre):
            logger.info("[matdb] In-memory replica of the materials database has reduced size: " + str(num_items_pre) + " --> " + str(num_items))
