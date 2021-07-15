from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ..plugin_utils.hpc_action_plugin import HpcActionModule


class ActionModule(HpcActionModule):
    def run(self, tmp=None, task_vars=None):
        return self.run_hpc_module(None,
                                   'sodalite.hpc.torque_job',
                                   tmp, task_vars)
