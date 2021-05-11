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


class TorqueHpcQueueInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            queue=dict(type='str', required=False)
        )
        super(TorqueHpcQueueInfoModule, self).__init__()

    def run_module(self):
        queue_name = self.ansible.params['queue']
        command = 'qstat -Q -f -1 {}'.format(queue_name) if queue_name is not None else 'qstat -Q -f -1'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["torque_queue"] = torque_utils.parse_queue_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse qstat output',
                    details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueHpcQueueInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
