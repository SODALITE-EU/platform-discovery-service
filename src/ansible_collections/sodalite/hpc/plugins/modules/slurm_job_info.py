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
module: slurm_job_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Slurm jobs
description:
  - Retrieve information about jobs on Slurm Workload Manager.
  - For more information, refer to the Slurm documentation at
    U(https://slurm.schedmd.com/scontrol.html).
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_job
options:
  job_id:
    type: str
    description:
      - The ID of the job to retrieve.
"""

EXAMPLES = """
- name: List all jobs
  sodalite.hpc.slurm_job_info:
  register: result
- name: List the selected job
  sodalite.hpc.slurm_job_info:
    job_id: 72
  register: result
- name: Show job state
  ansible.builtin.debug:
    msg: "{{ result.jobs[0].state }}"
"""

RETURN = """
jobs:
  description: List of Slurm jobs.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils._text import to_text
from ..module_utils import slurm_utils
from ..module_utils.hpc_module import HpcModule


class SlurmHpcJobInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            job_id=dict(type='str', required=False)
        )
        super(SlurmHpcJobInfoModule, self).__init__()

    def run_module(self):
        job_id = self.ansible.params['job_id']
        if not job_id:
            stdout = self.execute_command('scontrol show job')
        else:
            stdout = self.execute_command('scontrol show job {}', job_id)

        result = {}
        try:
            job_info = slurm_utils.parse_output(stdout, "JobId")
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
            )

        result["jobs"] = job_info

        self.ansible.exit_json(changed=False, **result)


def main():
    module = SlurmHpcJobInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
