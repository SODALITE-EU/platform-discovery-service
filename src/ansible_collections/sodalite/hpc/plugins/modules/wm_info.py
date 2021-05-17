#!/usr/bin/python

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: torque_node_info
'''

EXAMPLES = '''

'''

RETURN = '''
torque_node_info:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcModule
)


class WmInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict()
        super(WmInfoModule, self).__init__()

    def run_module(self):
        torque_stdin, torque_stdout, torque_stderr = self.ansible.run_command("command -v qsub")
        self.ansible.log("Torque {0} {1} {2}".format(torque_stdin, torque_stdout, torque_stderr))

        slurm_stdin, slurm_stdout, slurm_stderr = self.ansible.run_command("command -v sbatch")
        self.ansible.log("Slurm {0} {1} {2}".format(slurm_stdin, slurm_stdout, slurm_stderr))

        if not torque_stdout and slurm_stdout:
            self.ansible.fail_json(
                    msg='Could not detect any workload manager.'
            )
        result = {}
        result["wm_type"] = []

        if torque_stdout:
            result["wm_type"].append("Torque")
        if slurm_stdout:
            result["wm_type"].append("Slurm")

        self.ansible.exit_json(changed=False, **result)


def main():
    module = WmInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
