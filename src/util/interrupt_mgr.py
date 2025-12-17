import threading
import os
from datetime import datetime

from logging_utils import init_logger

SFTIMESTAMP_FMT = "%y%m%d%H%M%S"

class IRQManager:
    _sig_kill_detected = False
    _class_lock = threading.Lock()  # class-level lock

    @staticmethod
    def setKillSignalDetected():
        logger = init_logger()
        with IRQManager._class_lock:
            if (not IRQManager._sig_kill_detected):
                IRQManager._sig_kill_detected = True
                logger.info("[irq] Kill signal detected, entering early optimization termination sequence")

    @staticmethod
    def isKillOngoing():
        ret_val = False
        with IRQManager._class_lock:
            ret_val = IRQManager._sig_kill_detected
        return ret_val

    def __init__(self):
        self._stop_file = None
        self._is_initialized = False

    def init(self, stop_file: str):
        logger = init_logger()
        if (not stop_file):
            sf_tstamp = datetime.now().strftime(SFTIMESTAMP_FMT)
            sf_name = "./css_opt_stop_" + sf_tstamp + ".txt"
            #raise ValueError("[irq] A not-null file path for the stop file has to be specified!")
        else:
            sf_name = stop_file

        self._stop_file = sf_name
        self._is_initialized = True
        logger.info("[irq] Stop file for this run is: " + self._stop_file)

    #def isInterruptRequested(self):
    #    return (os.path.exists(self._stop_file))

    def getStopFilePath(self):
        if (not self._is_initialized):
            raise RuntimeError("[irq] Error. Bad Sequence. 'getStopFilePath' cannot be called here, as the interrupt manager has not been initialized")
        return self._stop_file


    def foundIRQ(self):
        logger = init_logger()

        if IRQManager.isKillOngoing():
            return True

        if (not self._is_initialized):
            raise RuntimeError("[irq] Error. Bad Sequence. 'foundIRQ' cannot be called here, as the interrupt manager has not been initialized")
        try:
            if (os.path.exists(self._stop_file)):
                logger.info("[irq] Stop file FOUND (" + self._stop_file + "), entering early optimization termination sequence")
                return True
            else:
                return False
        except Exception as e:
            logger.warning(f"[irq] Error while checking stop file '{self._stop_file}': {e}")
            return False

    def processIRQ(self):
        logger = init_logger()
        if IRQManager.isKillOngoing():
            return

        if (not self._is_initialized):
            raise RuntimeError("[irq] Error. Bad Sequence. 'processIRQ' cannot be called here, as the interrupt manager has not been initialized")
        logger.debug("[irq] Processing IRQ")
        try:
            if (os.path.exists(self._stop_file)):
                os.remove(self._stop_file)
                logger.debug("[irq] Stop file removed")
        except Exception as e:
            logger.warning(f"[irq] Error in stop file '{self._stop_file}' deletion: {e}")

