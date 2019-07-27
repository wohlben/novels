import os


def env_variable(varname, default_value=''):
    if os.environ.get(varname):
        return os.environ[varname]
    else:
        return default_value
