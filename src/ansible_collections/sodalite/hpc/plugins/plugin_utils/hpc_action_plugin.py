from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils._text import to_text
from ansible.errors import AnsibleActionFail, AnsibleFileNotFound
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
        source = module_args.get('job_src', None)
        contents = module_args.get('job_contents', None)
        if source and contents is not None:
            raise AnsibleActionFail('src and content are mutually exclusive')

        if source is not None:
            try:
                (b_file_data, show_content) = self._loader._get_file_contents(source)

                contents = to_text(b_file_data, errors='surrogate_or_strict')
                del module_args['job_src']
                module_args['job_contents'] = contents

            except AnsibleFileNotFound as e:
                raise AnsibleActionFail("could not find src=%s, %s" % (source, to_text(e)))

        wm_info = self._execute_module(module_name='sodalite.hpc.wm_info',
                                       module_args=dict(),
                                       task_vars=task_vars,
                                       tmp=tmp)
        display.debug("Facts %s" % wm_info)

        if not wm_info or "wm_type" not in wm_info:
            raise AnsibleActionFail('Could not detect any workload manager to use')
        wrap_async = self._task.async_val
        if slurm_module_name and "Slurm" in wm_info["wm_type"]:
            return self._execute_module(module_name=slurm_module_name,
                                        module_args=module_args,
                                        task_vars=task_vars, tmp=tmp, wrap_async=wrap_async)
        if torque_module_name and "Torque" in wm_info["wm_type"]:
            return self._execute_module(module_name=torque_module_name,
                                        module_args=module_args,
                                        task_vars=task_vars, tmp=tmp, wrap_async=wrap_async)

        raise AnsibleActionFail('Unsupported workload manager')
