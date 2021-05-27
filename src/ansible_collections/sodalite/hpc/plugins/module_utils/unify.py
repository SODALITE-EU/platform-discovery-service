from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def torque_to_slurm(output):
    if "exit_status" in output:
        output["exit_code"] = output["exit_status"] + ":0"
    return output
