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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    torque_utils
)


def torque_queue_info_argument_spec():

    module_args = dict(
        queue=dict(type='str', required=False)
    )

    return module_args


def run_module():

    module = AnsibleModule(torque_queue_info_argument_spec())
    queue_name = module.params['queue']

    try:
        command = 'qstat -Q -f -1 {}'.format(queue_name) if queue_name is not None else 'qstat -Q -f -1'
        stdin, stdout, stderr = module.run_command(command)
    except Exception as err:
        module.fail_json(
                msg='Failed to execute qstat command',
                details=to_text(err),
        )

    result = {}
    try:
        result["torque_queue"] = torque_utils.parse_queue_output(stdout)
    except Exception as err:
        module.fail_json(
                msg='Failed to parse qstat output',
                details=to_text(err),
        )

    module.exit_json(changed=False, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
