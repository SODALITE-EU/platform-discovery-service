from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_action_plugin import (
    HpcActionModule
)


class ActionModule(HpcActionModule):
    def run(self, tmp=None, task_vars=None):
        return self.run_hpc_module('sodalite.hpc.slurm_job_info',
                                   'sodalite.hpc.torque_job_info',
                                   tmp, task_vars)
