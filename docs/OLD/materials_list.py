import os

from logging_utils import init_logger

class MaterialsList:
    def __init__(self):
        self._materials = []
        self._num_items = 0
        self._desc = "n.a."
        self._is_initialized = False

    def initByFile(self, mats_file: str):
        self._desc = mats_file
        logger = init_logger()
        num_raw_mats = 0
        if os.path.exists(mats_file):
            logger.info("[MATERIALS_LIST][" + mats_file + "] Initialization")
            with open(mats_file) as f:
                materials_raw = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        else:
            #self._desc = "default"
            #logger.error("[MATERIALS_LIST] Materials list file (" + mats_file + ") NOT FOUND, default materials list will apply")
            #materials_raw = ['G4_Pb', 'G4_Ti', 'G4_POLYETHYLENE']
            raise ValueError("[MATERIALS_LIST][" + mats_file + "] ERROR. Initialization failure: the file cannot be found, or cannot be opened")
        dup_materials = []
        for item in materials_raw:
            if item not in self._materials:
                self._materials.append(item)
            else:
                if item not in dup_materials:
                    dup_materials.append(item)

        self._num_items = len(self._materials)
        num_dups = len(dup_materials)
        if (num_dups > 0):
            dup_mats_as_str = ", ".join(dup_materials)
            logger.warning("[MATERIALS_LIST][" + mats_file + "] Found duplicate materials (" + str(num_dups) + "): " + dup_mats_as_str + ". Items in the materials file should be distinct, i.e. ALL DIFFERENT!!")

        if (not (self._num_items > 0)):
            raise ValueError("[MATERIALS_LIST][" + mats_file + "] Bad data, materials list must contain at least one item")

        self._is_initialized = (self._num_items > 0)
        logger.info("[MATERIALS_LIST][" + mats_file + "] Materials list loaded successfully (items: " + str(self._num_items) + ")")


    def getMaterials(self):
        logger = init_logger()
        if (not (self._is_initialized)):
            raise RuntimeError("[MATERIALS_LIST][" + self._desc + "] ERROR. Bad Sequence. 'getList' cannot be called here, as the materials list is not initialized")
        logger.debug("[MATERIALS_LIST][" + self._desc + "] Returning materials list (items: " + str(self._num_items) + ")")
        return self._desc, self._num_items, self._materials

