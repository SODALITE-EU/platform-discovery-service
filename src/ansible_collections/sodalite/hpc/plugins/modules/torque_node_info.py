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
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    torque_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcModule
)


class TorqueHpcNodeInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            node=dict(type='str', required=False)
        )
        super(TorqueHpcNodeInfoModule, self).__init__()

    def run_module(self):
        node_name = self.ansible.params['node']
        command = 'pbsnodes {}'.format(node_name) if node_name is not None else 'pbsnodes'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["torque_node"] = torque_utils.parse_node_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse pbsnodes output',
                    details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueHpcNodeInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
