
import os
from datetime import datetime

import json

def is_enabled(var_name: str) -> bool:
    return os.getenv(var_name, "").lower() == "on"

def get_env_var(var_name: str, def_val: str) -> str:
    return os.getenv(var_name, def_val)

from datetime import datetime

def get_elapsed_time(t0: datetime, t1: datetime):
    """
    Compute elapsed time between t0 and t1.
    Returns:
      - total minutes (float)
      - formatted string "Dd Hh Mm Ss"
    """
    delta = t1 - t0
    total_minutes = delta.total_seconds() / 60.0

    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted = f"{days}d {hours}h {minutes}m {seconds}s"
    return total_minutes, formatted

def load_params_generic(path, section):
    if (path is None):
        return None
    else:
        with open(path) as f:
            return json.load(f)[section]
