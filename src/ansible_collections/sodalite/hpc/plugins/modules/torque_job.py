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
module: torque_job
author:
  - Alexander Maslennikov (@amaslenn)
short_description: Manage Torque jobs
description:
  - Create, suspend or cancel Torque job.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.torque_job_info
extends_documentation_fragment:
  - sodalite.hpc.job
"""

EXAMPLES = """
- name: run the job
  sodalite.hpc.torque_job:
  job_name: 'test'
  node_count: 1
  process_count_per_node: 1
  job_contents: |
                  sleep 60
                  echo 'test'
  keep_job_script: False
  register: job_info

- name: suspend the job
  become: true
  sodalite.hpc.torque_job:
  job_id: '{{ job_info.jobs[0].job_id }}'
  state: 'paused'

- name: resume the job
  become: true
  sodalite.hpc.torque_job:
  job_id: '{{ job_info.jobs[0].job_id }}'

- name: cancel the job
  sodalite.hpc.torque_job:
  job_id: '{{ job_info.jobs[0].job_id }}'
  state: 'cancelled'
"""

RETURN = """
jobs:
  description: List of Torque jobs that has one element.
  returned: success
  type: list
  elements: dict
"""

from ansible.module_utils._text import to_text
from ..module_utils import torque_utils
from ..module_utils import date_utils
from ..module_utils.hpc_module import HpcJobModule


class TorqueJobModule(HpcJobModule):

    NOTIFICATIONS = {
        "none": "p",
        "begin": "b",
        "end": "e",
        "fail": "f",
        "all": "a",
        "invalid_depend": "a",
        "time_limit": "a"
    }

    def __init__(self):
        super(TorqueJobModule, self).__init__('#PBS', "torque")

    def prepare_file(self):
        params = self.ansible.params
        file_contents = []
        file_contents.append(self.DIRECTIVE + ' -S ' + '/bin/bash')
        file_contents.append('## START OF HEADER ##')
        if params["job_name"]:
            file_contents.append(self.DIRECTIVE + ' -N ' + params['job_name'])
        else:
            self.ansible.fail_json(
                msg="Parameter 'job_name' is required"
            )
        if params["account"]:
            file_contents.append(self.DIRECTIVE + ' -A ' + params['account'])
        if params["queue"]:
            file_contents.append(self.DIRECTIVE + ' -q ' + params['queue'])
        if params["wall_time_limit"]:
            torque_format = date_utils.convert_to_torque(params['wall_time_limit'])
            if not torque_format:
                self.ansible.fail_json(
                    msg="Incorrect 'wall_time_limit' parameter format"
                )
            file_contents.append(self.DIRECTIVE + ' -l walltime=' + torque_format)
        if params["node_count"]:
            node_directive = self.DIRECTIVE + ' -l nodes=' + str(params['node_count'])
            if params["process_count_per_node"]:
                node_directive += ':ppn=' + str(params['process_count_per_node'])
            if params["request_gpus"]:
                # TODO
                node_directive += ',gpus=' + str(params['request_gpus'])
            if params["queue"]:
                node_directive += ':' + str(params['queue'])
            file_contents.append(node_directive)
        if params["core_count"]:
            file_contents.append(self.DIRECTIVE + ' -l procs=' + str(params['core_count']))
        if params["core_count_per_process"]:
            pass
        if params["memory_limit"]:
            # TODO unify memory inputs
            file_contents.append(self.DIRECTIVE + ' -l mem=' + params['memory_limit'])
        if params["minimum_memory_per_processor"]:
            file_contents.append(self.DIRECTIVE + ' -l pmem=' + params['minimum_memory_per_processor'])
        if params["request_specific_nodes"]:
            file_contents.append(self.DIRECTIVE + ' -l nodes=' + params['request_specific_nodes'])
        if params["job_array"]:
            # TODO parse job array output
            file_contents.append(self.DIRECTIVE + ' -t ' + params['job_array'])
        if params["standard_output_file"]:
            file_contents.append(self.DIRECTIVE + ' -o ' + params['standard_output_file'])
        if params["standard_error_file"]:
            file_contents.append(self.DIRECTIVE + ' -e ' + params['standard_error_file'])
        if params["combine_stdout_stderr"]:
            file_contents.append(self.DIRECTIVE + ' -j oe')
        if params["architecture_constraint"]:
            file_contents.append(self.DIRECTIVE + ' -l partition=' + params['architecture_constraint'])
        if params["copy_environment"]:
            file_contents.append(self.DIRECTIVE + ' -V ')
        if params["copy_environment_variable"]:
            file_contents.append(self.DIRECTIVE + ' -v ' + params['copy_environment_variable'])
        if params["job_dependency"]:
            file_contents.append(self.DIRECTIVE + ' -W ' + params['job_dependency'])
        if params["request_event_notification"]:
            file_contents.append(self.DIRECTIVE + ' -m ' + self.convert_notifications(params['request_event_notification']))
        if params["email_address"]:
            file_contents.append(self.DIRECTIVE + ' -M ' + params['email_address'])
        if params["defer_job"]:
            # TODO unify time inputs
            file_contents.append(self.DIRECTIVE + ' -a ' + params['defer_job'])
        if params["node_exclusive"]:
            file_contents.append(self.DIRECTIVE + ' -l naccesspolicy=singlejob')
        if params["job_options"]:
            file_contents.append('## USER DEFINED OPTIONS ## ')
            file_contents.append(params['job_options'])
        file_contents.append('## END OF HEADER ## ')
        if params["job_contents"]:
            file_contents.append(params['job_contents'])
        return file_contents

    def convert_notifications(self, notifications):
        result = "".join([self.NOTIFICATIONS[opt] for opt in notifications])
        return result

    def create_job(self, filename):
        stdout = self.execute_command('qsub {}', filename)

        try:
            job_id = stdout
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse sbatch output',
                details=to_text(err),
            )

        self.wait_state(job_id, ['W', 'R'])

        return True, self.get_job_info(job_id)

    def delete_job(self, job_id):
        state = self.get_job_state(job_id)

        if state in ['C']:
            return False, self.get_job_info(job_id)

        self.execute_command('qdel {0}', job_id)

        new_state = self.wait_state(job_id, ['C'])

        return new_state != state, self.get_job_info(job_id)

    def pause_job(self, job_id):
        state = self.get_job_state(job_id)

        self.execute_command('qhold {0}', job_id)

        new_state = self.wait_state(job_id, ['W', 'H'])

        return new_state != state, self.get_job_info(job_id)

    def resume_job(self, job_id):
        state = self.get_job_state(job_id)

        self.execute_command('qrls {0}', job_id)

        new_state = self.wait_state(job_id, ['W', 'R'])

        return new_state != state, self.get_job_info(job_id)

    def get_job_state(self, job_id):
        return self.get_job_info(job_id)["jobs"][0]["job_state"].upper()

    def get_job_info(self, job_id):
        stdout = self.execute_command('qstat -f {0}', job_id)

        result = {}
        try:
            job_info = torque_utils.parse_job_output(stdout)
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to parse qstat output',
                details=to_text(err),
            )

        if len(job_info) == 1:
            result["jobs"] = job_info
            return result
        else:
            self.ansible.fail_json(
                msg="Incorrect job status output"
            )


def main():
    module = TorqueJobModule()
    module.run_module()


if __name__ == '__main__':
    main()
