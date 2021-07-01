#!/usr/bin/python

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
module: slurm_partition_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Slurm partitions
description:
  - Retrieve information about partitions on Slurm Workload Manager.
  - For more information, refer to the Slurm documentation at
    U(https://slurm.schedmd.com/scontrol.html).
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_node_info
options:
  partition:
    type: str
    description:
      - Name of the partition to retrieve.
"""

EXAMPLES = """
- name: List all partitions
  sodalite.hpc.slurm_partition_info:
  register: result
- name: List the selected partition
  sodalite.hpc.slurm_partition_info:
    partition: test
  register: result
- name: Show partition
  ansible.builtin.debug:
    msg: "{{ result.partitions[0] }}"
"""

RETURN = """
partitions:
  description: List of Slurm partitions (queues).
  returned: success
  type: list
  elements: dict
"""


from ansible.module_utils._text import to_text
from ..module_utils import slurm_utils
from ..module_utils.hpc_module import HpcModule


class SlurmPartitionInfoModule(HpcModule):
    def __init__(self):
        argument_spec = dict(
            partition=dict(type='str', required=False)
        )
        super(SlurmPartitionInfoModule, self).__init__(argument_spec)

    def run_module(self):
        partition_name = self.ansible.params['partition']
        command = 'scontrol show partition {0}'.format(partition_name) if partition_name is not None else 'scontrol show partition'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["partitions"] = slurm_utils.parse_output(stdout, "PartitionName")
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = SlurmPartitionInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
