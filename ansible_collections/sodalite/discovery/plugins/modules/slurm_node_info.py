#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
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
module: slurm_node_info
'''

EXAMPLES = '''

'''

RETURN = '''
slurm_node_info:

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible_collections.sodalite.discovery.plugins.module_utils import slurm_utils


def slurm_node_info_argument_spec():

    module_args = dict(
        node=dict(type='str', required=False)
    )

    return module_args


def run_module():

    module = AnsibleModule(slurm_node_info_argument_spec())
    node_name = module.params['node']

    try:
        command = 'scontrol show node {}'.format(node_name) if node_name is not None else 'scontrol show nodes'
        stdin, stdout, stderr = module.run_command(command)
    except Exception as err:
        module.fail_json(
                msg='Failed to execute scontrol command',
                details=to_text(err),
        )

    result = {}
    try:
        result["slurm_node"] = slurm_utils.parse_output(stdout, "NodeName")
    except Exception as err:
        module.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
        )

    for node in result["slurm_node"]:
        if node["Gres"] == "(null)":
            node["GPU"] = 0

    module.exit_json(changed=False, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
