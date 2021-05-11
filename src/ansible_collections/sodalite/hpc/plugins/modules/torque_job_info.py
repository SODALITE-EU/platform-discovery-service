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
module: torque_job_info
'''

EXAMPLES = '''

'''

RETURN = '''
torque_job_info:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    torque_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcModule
)


class TorqueHpcJobInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            job_id=dict(type='str', required=True)
        )
        super(TorqueHpcJobInfoModule, self).__init__()

    def run_module(self):
        job_id = self.ansible.params['job_id']
        if not job_id:
            self.ansible.fail_json(
                msg="Parameter 'job_id' is required"
            )
        stdout = self.execute_command('qstat -f {}', job_id)

        result = {}
        try:
            result["torque_job"] = torque_utils.parse_job_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse qstat output',
                    details=to_text(err),
            )
        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueHpcJobInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
