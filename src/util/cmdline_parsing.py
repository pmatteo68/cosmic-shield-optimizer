import argparse

def _auto_cast(v: str):
    lowc = v.lower()
    if lowc == "true":
        return True, "bool"
    if lowc == "false":
        return False, "bool"
    try:
        return int(v), "int"
    except ValueError:
        try:
            return float(v), "float"
        except ValueError:
            return v, "str"

class ParametersHolder:
    def __init__(self, sw_name, args=None, flag="--param"):

        self._params = {}

        parser = argparse.ArgumentParser(description = sw_name, add_help = False)
        parser.add_argument(flag, nargs="+", action="append", required=False, metavar=("KEY", "VALUE"), help=f"Specify parameters as: {flag} key value [value ...]. Repeatable.")
        parsedArgs = parser.parse_args(args)
        groups = parsedArgs.__dict__[flag.lstrip("-").replace("-", "_")] or []

        for g in groups:
            key, *vals = g
            if key in self._params:
                raise ValueError(f"Duplicate parameter '{key}' not allowed")
            #self._params[key] = vals[0] if len(vals) == 1 else vals
            if len(vals) == 1:
                val, tname = _auto_cast(vals[0])
                self._params[key] = (val, tname)
            else:
                casted = [_auto_cast(v) for v in vals]
                self._params[key] = ([v for v, _ in casted], "list[" + ",".join(t for _, t in casted) + "]")


    def get(self, name, default=None):
        if name in self._params:
            #return self._params[name]
            return self._params[name][0]
        if default is not None:
            return default
        raise KeyError(f"Parameter '{name}' not found")

    def dump(self, logger):
        """Print all parameters in order, showing lists properly."""
        for k in sorted(self._params):
            val, tname = self._params[k]
            if isinstance(val, list):
                v_str = "[" + ", ".join(map(str, val)) + "]"
            else:
                v_str = str(val)
            str_to_print = f"    {k}: {v_str} ({tname})"
            if (logger is None):
                print(str_to_print)
            else:
                logger.info(str_to_print)

