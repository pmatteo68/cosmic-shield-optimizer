import os

from logging_utils import init_logger

class MaterialsSet:
    def __init__(self):
        #self._materials = []
        self._materials_list = []
        self._materials_dict = {}
        self._num_items = 0
        self._desc = "n.a."
        self._parent_db_ref = None
        self._is_initialized = False

    def initByFile(self, mats_file: str, materialsDb):
        self._parent_db_ref = materialsDb
        self._desc = mats_file
        logger = init_logger()
        num_raw_mats = 0
        if os.path.exists(mats_file):
            logger.info("[matset][" + mats_file + "] Materials set in scope for the optimization is being initialized.")
            with open(mats_file) as f:
                materials_raw = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        else:
            #self._desc = "default"
            #logger.error("[matset] Materials list file (" + mats_file + ") NOT FOUND, default materials list will apply")
            #materials_raw = ['G4_Pb', 'G4_Ti', 'G4_POLYETHYLENE']
            raise ValueError("[matset][" + mats_file + "] ERROR. Initialization failure: the file cannot be found, or cannot be opened")
        dup_materials = []
        for item in materials_raw:
            if item not in self._materials_list:
                curWgt = None
                if (materialsDb and materialsDb.isInitialized()):
                    curWgt = materialsDb.getDensity(item)
                    curE = materialsDb.getStiffness(item)
                #self._materials.append((item, curWgt, curE))
                self._materials_list.append(item)
                self._materials_dict[item] = { "mDensity": curWgt, "mStiffness": curE }
            else:
                if item not in dup_materials:
                    dup_materials.append(item)

        self._num_items = len(self._materials_list)
        num_dups = len(dup_materials)
        if (num_dups > 0):
            dup_mats_as_str = ", ".join(dup_materials)
            logger.warning("[matset][" + mats_file + "] Found duplicate materials (" + str(num_dups) + "): " + dup_mats_as_str + ". Items in the materials file should be distinct, i.e. ALL DIFFERENT!!")

        if (not (self._num_items > 0)):
            raise ValueError("[matset][" + mats_file + "] Bad data, materials set must contain at least one item")

        self._is_initialized = (self._num_items > 0)
        logger.info("[matset][" + mats_file + "] Materials set loaded successfully (items: " + str(self._num_items) + ")")

    def GetParentDb(self):
        if (not (self._is_initialized)):
            raise RuntimeError("[matset][" + self._desc + "] ERROR. Bad Sequence. 'GetParentDb' cannot be called here, as the materials set is not initialized")
        return self._parent_db_ref

    def getMaterialsList(self):
        logger = init_logger()
        if (not (self._is_initialized)):
            raise RuntimeError("[matset][" + self._desc + "] ERROR. Bad Sequence. 'getMaterialsList' cannot be called here, as the materials set is not initialized")
        logger.debug("[matset][" + self._desc + "] Returning materials list (items: " + str(self._num_items) + ")")
        return self._desc, self._num_items, self._materials_list

    def getField(self, matName, fName):
        if (not (self._is_initialized)):
            raise RuntimeError("[matset][" + self._desc + "] ERROR. Bad Sequence. 'getField' cannot be called here, as the materials set is not initialized")
        return (self._materials_dict[matName][fName])

    def getDensity(self, matName):
        return (self.getField(matName, "mDensity"))

    def getStiffness(self, matName):
        return (self.getField(matName, "mStiffness"))
