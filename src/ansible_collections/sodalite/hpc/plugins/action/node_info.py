from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ..plugin_utils.hpc_action_plugin import HpcActionModule


class ActionModule(HpcActionModule):
    def run(self, tmp=None, task_vars=None):
        return self.run_hpc_module('sodalite.hpc.slurm_node_info',
                                   'sodalite.hpc.torque_node_info',
                                   tmp, task_vars)
