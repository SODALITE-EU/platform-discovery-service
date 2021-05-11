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
module: slurm_job
'''

EXAMPLES = '''

'''

RETURN = '''
slurm_job:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcJobModule
)


class SlurmHpcJobModule(HpcJobModule):
    def __init__(self):
        super(SlurmHpcJobModule, self).__init__('#SBATCH')

    def prepare_file(self):
        params = self.ansible.params
        file_contents = []
        file_contents.append('#!/bin/bash')
        file_contents.append('## START OF HEADER ##')
        if params["job_name"]:
            file_contents.append(self.DIRECTIVE + ' -J ' + params['job_name'])
        else:
            self.ansible.fail_json(
                msg="Parameter 'job_name' is required"
            )
        if params["account"]:
            file_contents.append(self.DIRECTIVE + ' -A ' + params['account'])
        if params["queue"]:
            file_contents.append(self.DIRECTIVE + ' --partition=' + params['queue'])
        if params["wall_time_limit"]:
            file_contents.append(self.DIRECTIVE + ' --time=' + params['wall_time_limit'])
        if params["node_count"]:
            file_contents.append(self.DIRECTIVE + ' -N ' + str(params['node_count']))
        if params["core_count"]:
            file_contents.append(self.DIRECTIVE + ' -n ' + str(params['core_count']))
        if params["process_count_per_node"]:
            file_contents.append(self.DIRECTIVE + ' --ntasks-per-node=' + str(params['process_count_per_node']))
        if params["core_count_per_process"]:
            file_contents.append(self.DIRECTIVE + ' ----cpus-per-task=' + str(params['core_count_per_process']))
        if params["memory_limit"]:
            file_contents.append(self.DIRECTIVE + ' --mem=' + params['memory_limit'])
        if params["minimum_memory_per_processor"]:
            file_contents.append(self.DIRECTIVE + ' --mem-per-cpu=' + params['minimum_memory_per_processor'])
        if params["request_gpus"]:
            pass
        if params["request_specific_nodes"]:
            file_contents.append(self.DIRECTIVE + ' --nodelist=' + params['request_specific_nodes'])
        if params["job_array"]:
            file_contents.append(self.DIRECTIVE + ' -a ' + params['job_array'])
        if params["standard_output_file"]:
            file_contents.append(self.DIRECTIVE + ' --output=' + params['standard_output_file'])
        if params["standard_error_file"]:
            file_contents.append(self.DIRECTIVE + ' --error=' + params['standard_error_file'])
        if params["combine_stdout_stderr"]:
            pass
        if params["architecture_constraint"]:
            file_contents.append(self.DIRECTIVE + ' -C ' + params['architecture_constraint'])
        if params["copy_environment"]:
            file_contents.append(self.DIRECTIVE + ' --export=ALL ')
        if params["copy_environment_variable"]:
            file_contents.append(self.DIRECTIVE + ' --export=' + params['copy_environment_variable'])
        if params["job_dependency"]:
            file_contents.append(self.DIRECTIVE + ' --dependency=' + params['job_dependency'])
        if params["request_event_notification"]:
            # TODO
            pass
        if params["email_address"]:
            file_contents.append(self.DIRECTIVE + ' --mail-user=' + params['email_address'])
        if params["defer_job"]:
            file_contents.append(self.DIRECTIVE + ' --begin=' + params['defer_job'])
        if params["node_exclusive"]:
            file_contents.append(self.DIRECTIVE + ' --exclusive')

        file_contents.append('## END OF HEADER ## ')
        if params["job_contents"]:
            file_contents.append(params['job_contents'])
        return file_contents

    def create_job(self, filename):
        stdout = self.execute_command('sbatch {}', filename)

        try:
            job_id = slurm_utils.parse_job_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse sbatch output',
                    details=to_text(err),
            )

        self.wait_state(job_id, ['PENDING', 'RUNNING'])

        return True, self.get_job_info(job_id)

    def delete_job(self, job_id):
        state = self.get_job_state(job_id)

        if state in ['COMPLETED']:
            return False, {"slurm_job": state}

        self.execute_command('scancel {}', job_id)

        new_state = self.wait_state(job_id, ['CANCELLED'])

        return new_state != state, {"slurm_job": new_state}

    def pause_job(self, job_id):
        state = self.get_job_state(job_id)

        if state == 'RUNNING':
            self.execute_command('scontrol suspend {}', job_id)
        if state == 'PENDING':
            self.execute_command('scontrol hold {}', job_id)

        new_state = self.wait_state(job_id, ['PENDING', 'SUSPENDED'])

        return new_state != state, {"slurm_job": new_state}

    def resume_job(self, job_id):
        state = self.get_job_state(job_id)

        if state == 'PENDING':
            self.execute_command('scontrol release {}', job_id)
        if state == 'SUSPENDED':
            self.execute_command('scontrol resume {}', job_id)

        new_state = self.wait_state(job_id, ['PENDING', 'RUNNING'])

        return new_state != state, {"slurm_job": new_state}

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
    module = SlurmHpcJobModule()
    module.run_module()


if __name__ == '__main__':
    main()