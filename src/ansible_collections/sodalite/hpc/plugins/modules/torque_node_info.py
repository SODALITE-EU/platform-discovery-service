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
module: torque_node_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Torque nodes
description:
  - Retrieve information about nodes on Torque Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.torque_queue_info
options:
  node:
    type: str
    description:
      - Name of the node to retrieve.
"""

EXAMPLES = """
- name: List all nodes
  sodalite.hpc.torque_node_info:
  register: result
- name: List the selected node
  sodalite.hpc.torque_node_info:
    node: node-6.novalocal
  register: result
- name: Show node state
  ansible.builtin.debug:
    msg: "{{ result.nodes[0].power_state }}"
"""

RETURN = """
nodes:
  description: List of Torque nodes.
  returned: success
  type: list
  elements: dict
"""


from ansible.module_utils._text import to_text
from ..module_utils import torque_utils
from ..module_utils.hpc_module import HpcModule


class TorqueNodeInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            node=dict(type='str', required=False)
        )
        super(TorqueNodeInfoModule, self).__init__()

    def run_module(self):
        node_name = self.ansible.params['node']
        command = 'pbsnodes {0}'.format(node_name) if node_name is not None else 'pbsnodes'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["nodes"] = torque_utils.parse_node_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse pbsnodes output',
                details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueNodeInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
