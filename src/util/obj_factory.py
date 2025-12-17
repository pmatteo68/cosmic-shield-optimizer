import importlib
from logging_utils import init_logger

class CO_ObjectFactory:
    def __init__(self):
        logger = init_logger()
        logger.debug("[objf] CO Object factory created.")

    def createObject(self, objDesc, module_name, class_name, defObject):
        classRef = None
        logger = init_logger()
        logger.info(f"[objf][{objDesc}] Creating object: '{module_name}.{class_name}.")
        try:
            logger.debug(f"[objf] Importing module '{module_name}'.")
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.warning(f"[objf][{objDesc}] Module '{module_name}' not found, falling back to default object.")
            return None

        try:
            logger.debug(f"[objf] Creating class '{class_name}'")
            classRef = getattr(module, class_name)
        except AttributeError:
            logger.warning(f"[objf][{objDesc}] Class '{class_name}' not found in module '{module_name}', falling back to default object.")
            return None

        if (classRef):
            logger.info(f"[objf][{objDesc}] Object CREATED (instance of class: '{class_name}')")
            return classRef()
        else:
            logger.info(f"[objf][{objDesc}] Object results None, falling back to default object.")
            return defObject
 
