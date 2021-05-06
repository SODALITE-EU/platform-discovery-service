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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils
)


def slurm_job_info_argument_spec():

    module_args = dict(
        job_id=dict(type='str', required=True)
    )

    return module_args


def run_module():
    module = AnsibleModule(slurm_job_info_argument_spec())
    result = execute_command(module)
    module.exit_json(changed=False, **result)


def execute_command(module):
    job_id = module.params['job_id']

    if not job_id:
        module.fail_json(
            msg="Parameter 'job_id' is required"
        )

    try:
        command = 'scontrol show job {}'.format(job_id)
        stdin, stdout, stderr = module.run_command(command)
    except Exception as err:
        module.fail_json(
                msg='Failed to execute scontrol command',
                details=to_text(err),
        )

    result = {}
    try:
        job_info = slurm_utils.parse_output(stdout, "JobId")
    except Exception as err:
        module.fail_json(
                msg='Failed to parse scontrol output',
                details=to_text(err),
        )

    if len(job_info) == 1:
        result["slurm_job"] = job_info[0]
        return result
    else:
        module.fail_json(
            msg="Incorrect job status output"
        )


def main():
    run_module()


if __name__ == '__main__':
    main()
