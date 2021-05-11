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
module: slurm_job_info
'''

EXAMPLES = '''

'''

RETURN = '''
slurm_job_info:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcModule
)


class SlurmHpcJobInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            job_id=dict(type='str', required=True)
        )
        super(SlurmHpcJobInfoModule, self).__init__()

    def run_module(self):
        job_id = self.ansible.params['job_id']

        if not job_id:
            self.ansible.fail_json(
                msg="Parameter 'job_id' is required"
            )

        result = self.get_job_info(job_id)

        self.ansible.exit_json(changed=False, **result)

    def get_job_state(self, job_id):
        return self.get_job_info(job_id)["slurm_job"]["JobState"]

    def get_job_info(self, job_id):
        stdout = self.execute_command('scontrol show job {}', job_id)

        result = {}
        try:
            job_info = slurm_utils.parse_output(stdout, "JobId")
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse scontrol output',
                    details=to_text(err),
            )

        if len(job_info) == 1:
            result["slurm_job"] = job_info[0]
            return result
        else:
            self.ansible.fail_json(
                msg="Incorrect job status output"
            )


def main():
    module = SlurmHpcJobInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
