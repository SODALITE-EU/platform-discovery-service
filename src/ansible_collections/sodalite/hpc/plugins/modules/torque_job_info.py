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
module: torque_job_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List Torque jobs
description:
  - Retrieve information about jobs on Torque Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.torque_job
options:
  job_id:
    type: str
    description:
      - The ID of the job to retrieve.
"""

EXAMPLES = """
- name: List all jobs
  sodalite.hpc.torque_job_info:
  register: result
- name: List the selected job
  sodalite.hpc.torque_job_info:
    job_id: 2346.cloudserver
  register: result
- name: Show job state
  ansible.builtin.debug:
    msg: "{{ result.jobs[0].state }}"
"""

RETURN = """
jobs:
  description: List of Torque jobs.
  returned: success
  type: list
  elements: dict
"""


from ansible.module_utils._text import to_text
from ..module_utils import torque_utils
from ..module_utils.hpc_module import HpcModule


class TorqueJobInfoModule(HpcModule):
    def __init__(self):
        self.argument_spec = dict(
            job_id=dict(type='str', required=False)
        )
        super(TorqueJobInfoModule, self).__init__()

    def run_module(self):
        job_id = self.ansible.params['job_id']
        if not job_id:
            stdout = self.execute_command('qstat -f')
        else:
            stdout = self.execute_command('qstat -f {}', job_id)

        result = {}
        try:
            result["jobs"] = torque_utils.parse_job_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse qstat output',
                details=to_text(err),
            )
        self.ansible.exit_json(changed=False, **result)


def main():
    module = TorqueJobInfoModule()
    module.run_module()


if __name__ == '__main__':
    main()
