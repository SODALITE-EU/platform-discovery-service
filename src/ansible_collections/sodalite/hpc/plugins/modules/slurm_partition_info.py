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
module: slurm_partition_info
'''

EXAMPLES = '''

'''

RETURN = '''
slurm_partition_info:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcModule
)


class SlurmHpcPartitionInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            partition=dict(type='str', required=False)
        )
        super(SlurmHpcPartitionInfoModule, self).__init__()

    def run_module(self):
        partition_name = self.ansible.params['partition']
        command = 'scontrol show partition {}'.format(partition_name) if partition_name is not None else 'scontrol show partition'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["slurm_partition"] = slurm_utils.parse_output(stdout, "PartitionName")
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse scontrol output',
                    details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = SlurmHpcPartitionInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
