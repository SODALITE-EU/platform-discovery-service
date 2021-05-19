from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


class HpcActionModule(ActionBase):
    def run_hpc_module(self,
                       slurm_module_name,
                       torque_module_name,
                       tmp=None,
                       task_vars=None):

        super(HpcActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()
        wm_info = self._execute_module(module_name='sodalite.hpc.wm_info',
                                       module_args=dict(),
                                       task_vars=task_vars,
                                       tmp=tmp)
        display.debug("Facts %s" % wm_info)

        if not wm_info:
            raise AnsibleActionFail('Could not detect any workload manager to use')

        if "Slurm" in wm_info["wm_type"]:
            return self._execute_module(module_name=slurm_module_name,
                                        module_args=module_args,
                                        task_vars=task_vars, tmp=tmp)
        if "Torque" in wm_info["wm_type"]:
            return self._execute_module(module_name=torque_module_name,
                                        module_args=module_args,
                                        task_vars=task_vars, tmp=tmp)

        raise AnsibleActionFail('Unsupported workload manager')
