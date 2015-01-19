# Batch script for starting GGCMI batch runs

function die {
  echo "Error: $1" >/dev/stderr
  exit 1
}

function require_env {
  varname=$1
  eval value=\$$varname
  if [ -z "$value" ]; then
    die "The environment variable $varname is not set, but it is a required parameter"
  fi
}

require_env DB_USER
require_env DB_PASS
require_env DB_HOST
require_env DB_DATABASE

if [ -z "$DATA_OUTPUT_DIR" ]; then
  export DATA_OUTPUT_DIR=/opt/ggcmi-output
fi
if [ -z "$DATA_INPUT_DIR" ]; then
  export DATA_INPUT_DIR=/opt/ggcmi-input
fi

# ensure output dirs exist
mkdir -p "$DATA_OUTPUT_DIR/logs" && \
mkdir -p "$DATA_OUTPUT_DIR/output" && \
mkdir -p "$DATA_OUTPUT_DIR/shelves" || die "Cannot create subdirectories in '$DATA_OUTPUT_DIR/'"


# First killall running ipython processes
killall -q ipython

# start the GGCMI output processor
screen -S "output processor" -d -m ipython ggcmi_process_results.py

# start the GGCMI main process
screen -S "Main" -d -m ipython ggcmi_main.py

# Start the logserver
screen -S logserver -d -m ipython simple_logserver.py


# run a terminal to not quit
while true; do
    echo "Dropping to shell. "
    echo "Detach with Ctrl-p Ctrl-q. "
    /bin/bash
    sleep 1
done

