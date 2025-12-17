
. ./bin/env.sh

source ${VENV_HOME}/bin/activate

showProps()
{
  python --version
  python -m pip list
}

#o_format=$1

showProps
