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
import re

regex = r"NodeName=(?P<nodeName>\S*) |(?P<name>\w*)=(?P<value>([^=^\[^\]]*\s|[\S]*\s))"


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
    result["slurm_node"] = []
    node = {}
    try:
        matches = re.finditer(regex, stdout, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            if match.group("nodeName") is not None:
                node = {}
                node["NodeName"] = match.group("nodeName")
                result["slurm_node"].append(node)
            else:
                node[match.group("name")] = match.group("value").rstrip()
    except Exception as err:
        module.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
        )

    module.exit_json(changed=False, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
