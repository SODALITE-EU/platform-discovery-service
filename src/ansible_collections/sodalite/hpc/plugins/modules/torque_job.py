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
module: torque_job
'''

EXAMPLES = '''

'''

RETURN = '''
torque_job:

'''

from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    torque_utils
)
from ansible_collections.sodalite.hpc.plugins.module_utils.hpc_module import (
    HpcJobModule
)


class TorqueHpcJobModule(HpcJobModule):
    def __init__(self):
        super(TorqueHpcJobModule, self).__init__('#PBS')

    def prepare_file(self):
        file_contents = []
        file_contents.append(self.DIRECTIVE + ' -S ' + '/bin/bash')
        file_contents.append('## START OF HEADER ##')
        if self.ansible.params["job_name"]:
            file_contents.append(self.DIRECTIVE + ' -N ' + self.ansible.params['job_name'])
        else:
            self.ansible.fail_json(
                msg="Parameter 'job_name' is required"
            )
        if self.ansible.params["account"]:
            file_contents.append(self.DIRECTIVE + ' -A ' + self.ansible.params['account'])
        if self.ansible.params["queue"]:
            file_contents.append(self.DIRECTIVE + ' -q ' + self.ansible.params['queue'])
        if self.ansible.params["wall_time_limit"]:
            file_contents.append(self.DIRECTIVE + ' -l walltime=' + self.ansible.params['wall_time_limit'])
        if self.ansible.params["node_count"]:
            node_directive = self.DIRECTIVE + ' -l nodes=' + str(self.ansible.params['node_count'])
            if self.ansible.params["process_count_per_node"]:
                node_directive += ':ppn=' + str(self.ansible.params['process_count_per_node'])
            if self.ansible.params["request_gpus"]:
                # TODO
                node_directive += ':gpus=' + str(self.ansible.params['request_gpus'])
            if self.ansible.params["queue"]:
                node_directive += ':' + str(self.ansible.params['queue'])
            file_contents.append(node_directive)
        if self.ansible.params["core_count"]:
            file_contents.append(self.DIRECTIVE + ' -l procs=' + str(self.ansible.params['core_count']))
        if self.ansible.params["core_count_per_process"]:
            pass
        if self.ansible.params["memory_limit"]:
            file_contents.append(self.DIRECTIVE + ' -l mem=' + self.ansible.params['memory_limit'])
        if self.ansible.params["minimum_memory_per_processor"]:
            file_contents.append(self.DIRECTIVE + ' -l pmem=' + self.ansible.params['minimum_memory_per_processor'])
        if self.ansible.params["request_specific_nodes"]:
            file_contents.append(self.DIRECTIVE + ' -l nodes=' + self.ansible.params['request_specific_nodes'])
        if self.ansible.params["job_array"]:
            file_contents.append(self.DIRECTIVE + ' -t ' + self.ansible.params['job_array'])
        if self.ansible.params["standard_output_file"]:
            file_contents.append(self.DIRECTIVE + ' -o ' + self.ansible.params['standard_output_file'])
        if self.ansible.params["standard_error_file"]:
            file_contents.append(self.DIRECTIVE + ' -e ' + self.ansible.params['standard_error_file'])
        if self.ansible.params["combine_stdout_stderr"]:
            file_contents.append(self.DIRECTIVE + ' -j oe' + self.ansible.params['standard_error_file'])
        if self.ansible.params["architecture_constraint"]:
            file_contents.append(self.DIRECTIVE + ' -l partition=' + self.ansible.params['architecture_constraint'])
        if self.ansible.params["copy_environment"]:
            file_contents.append(self.DIRECTIVE + ' -V ')
        if self.ansible.params["copy_environment_variable"]:
            file_contents.append(self.DIRECTIVE + ' -v ' + self.ansible.params['copy_environment_variable'])
        if self.ansible.params["job_dependency"]:
            file_contents.append(self.DIRECTIVE + ' -W ' + self.ansible.params['job_dependency'])
        if self.ansible.params["request_event_notification"]:
            # TODO
            pass
        if self.ansible.params["email_address"]:
            file_contents.append(self.DIRECTIVE + ' -M ' + self.ansible.params['email_address'])
        if self.ansible.params["defer_job"]:
            file_contents.append(self.DIRECTIVE + ' -a ' + self.ansible.params['defer_job'])
        if self.ansible.params["node_exclusive"]:
            file_contents.append(self.DIRECTIVE + ' -l naccesspolicy=singlejob')

        file_contents.append('## END OF HEADER ## ')
        if self.ansible.params["job_contents"]:
            file_contents.append(self.ansible.params['job_contents'])
        return file_contents

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
        state = self.get_job_state( job_id)

        if state in ['C']:
            return False, {"torque_job": state}

        self.execute_command('qdel {}', job_id)

        new_state = self.wait_state(job_id, ['C'])

        return new_state != state, {"torque_job": new_state}

    def pause_job(self, job_id):
        state = self.get_job_state(job_id)

        self.execute_command('qhold {}', job_id)

        new_state = self.wait_state(job_id, ['W', 'H'])

        return new_state != state, {"torque_job": new_state}

    def resume_job(self, job_id):
        state = self.get_job_state(job_id)

        self.execute_command('qrls {}', job_id)

        new_state = self.wait_state(job_id, ['W', 'R'])

        return new_state != state, {"torque_job": new_state}

    def get_job_state(self, job_id):
        return self.get_job_info(job_id)["torque_job"]["job_state"].upper()

    def get_job_info(self, job_id):
        stdout = self.execute_command('qstat -f {}', job_id)

        result = {}
        try:
            result["torque_job"] = torque_utils.parse_job_output(stdout)
            return result
        except Exception as err:
            self.ansible.fail_json(
                    msg='Failed to parse qstat output',
                    details=to_text(err),
            )


def main():
    module = TorqueHpcJobModule()
    module.run_module()


if __name__ == '__main__':
    main()
