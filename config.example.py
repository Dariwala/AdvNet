"""Example local configuration.

Copy this file to ``config.py`` (which is gitignored) and adjust the values for
your machine.

    cp config.example.py config.py

Note: the ns-3 source tree location is configured via the ``ADVNET_NS3_PATH``
environment variable rather than this file, e.g.

    export ADVNET_NS3_PATH=/path/to/ns-3-dev
"""

# Absolute path (WITH a trailing slash) of the directory that contains both this
# AdvNet repo (as "AdvNet/") and the emulator output dirs "packet-logs/" and
# "packet-logs-2/". Backends read traces from <parent_folder>AdvNet/traces/ and
# read/write per-run logs under <parent_folder>packet-logs[-2]/.
#
# Example: if the repo is at /home/you/AdvNet, use
#     parent_folder = "/home/you/"
# and create the log dirs once:
#     mkdir -p /home/you/packet-logs /home/you/packet-logs-2
parent_folder = ""
