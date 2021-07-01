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
module: torque_queue_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Torque queues
description:
  - Retrieve information about queues on Torque Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.torque_node_info
options:
  queue:
    type: str
    description:
      - Name of the queue to retrieve.
"""

EXAMPLES = """
- name: List all queues
  sodalite.hpc.torque_queue_info:
  register: result
- name: List the selected queue
  sodalite.hpc.torque_queue_info:
    queue: cpu
  register: result
- name: Show queue jobs number
  ansible.builtin.debug:
    msg: "{{ result.queues[0].total_jobs }}"
"""

RETURN = """
queues:
  description: List of Torque queues.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils._text import to_text
from ..module_utils import torque_utils
from ..module_utils.hpc_module import HpcModule


class TorqueQueueInfoModule(HpcModule):
    def __init__(self):
        argument_spec = dict(
            queue=dict(type='str', required=False)
        )
        super(TorqueQueueInfoModule, self).__init__(argument_spec)

    def run_module(self):
        queue_name = self.ansible.params['queue']
        command = 'qstat -Q -f -1 {0}'.format(queue_name) if queue_name is not None else 'qstat -Q -f -1'
        stdout = self.execute_command(command)

        result = {}
        try:
            result["queues"] = torque_utils.parse_queue_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse qstat output',
                details=to_text(err),
            )

        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueQueueInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
