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
module: slurm_node_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Slurm nodes
description:
  - Retrieve information about nodes on Slurm Workload Manager.
  - For more information, refer to the Slurm documentation at
    U(https://slurm.schedmd.com/scontrol.html).
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_partition_info
options:
  node:
    type: str
    description:
      - Name of the node to retrieve.
"""

EXAMPLES = """
- name: List all nodes
  sodalite.hpc.slurm_node_info:
  register: result
- name: List the selected node
  sodalite.hpc.slurm_node_info:
    node: wn1
  register: result
- name: Show node
  ansible.builtin.debug:
    msg: "{{ result.nodes[0] }}"
"""

RETURN = """
nodes:
  description: List of Slurm nodes.
  returned: success
  type: list
  elements: dict
"""


from ansible.module_utils._text import to_text
from ..module_utils import slurm_utils
from ..module_utils.hpc_module import HpcModule


class SlurmNodeInfoModule(HpcModule):
    def __init__(self):
        argument_spec = dict(
            node=dict(type='str', required=False)
        )
        super(SlurmNodeInfoModule, self).__init__(argument_spec)

    def run_module(self):
        node_name = self.ansible.params['node']
        command = 'scontrol show node {0}'.format(node_name) if node_name is not None else 'scontrol show nodes'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["nodes"] = slurm_utils.parse_output(stdout, "NodeName")
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = SlurmNodeInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
