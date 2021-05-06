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

import os
from time import sleep

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils
)


def slurm_job_argument_spec():

    module_args = dict(
        job_id=dict(type='str', required=False),
        state=dict(default='queued', choices=['queued', 'paused', 'cancelled']),
        job_name=dict(type='str', required=False),
        job_options=dict(type='str', required=False),
        job_contents=dict(type='str', required=False),
        account=dict(type='str', required=False),
        queue=dict(type='str', required=False),
        wall_time_limit=dict(type='str', required=False),
        node_count=dict(type='int', required=False),
        core_count=dict(type='int', required=False),
        process_count_per_node=dict(type='int', required=False),
        core_count_per_process=dict(type='int', required=False),
        memory_limit=dict(type='str', required=False),
        minimum_memory_per_processor=dict(type='str', required=False),
        request_gpus=dict(type='str', required=False),
        request_specific_nodes=dict(type='str', required=False),
        job_array=dict(type='str', required=False),
        standard_output_file=dict(type='str', required=False),
        standard_error_file=dict(type='str', required=False),
        combine_stdout_stderr=dict(type='str', required=False),
        architecture_constraint=dict(type='str', required=False),
        copy_environment=dict(type='str', required=False),
        copy_environment_variable=dict(type='str', required=False),
        job_dependency=dict(type='str', required=False),
        request_event_notification=dict(type='str', required=False),
        email_address=dict(type='str', required=False),
        defer_job=dict(type='str', required=False),
        node_exclusive=dict(type='str', required=False),
        keep_job_script=dict(type='bool', default=True)
    )

    return module_args


def run_module():

    module = AnsibleModule(slurm_job_argument_spec())

    state = module.params['state']

    if state == 'queued' and not (module.params["job_name"] or module.params["job_id"]):
        module.fail_json(
            msg="Parameter 'job_name' or 'job_id' is required if state == 'queued'"
        )

    if state == 'cancelled' and not module.params["job_id"]:
        module.fail_json(
            msg="Parameter 'job_id' is required if state == 'cancelled'"
        )

    if state == 'paused' and not module.params["job_id"]:
        module.fail_json(
            msg="Parameter 'job_id' is required if state == 'paused'"
        )

    if state == 'queued':
        if module.params["job_name"]:
            contents = prepare_file(module)
            filename = write_file("{}.slurm".format(module.params["job_name"]), contents)
            changed, result = create_job(module, filename)
            if not module.params["keep_job_script"]:
                module.add_cleanup_file(filename)
        else:
            changed, result = resume_job(module, module.params["job_id"])
    if state == 'cancelled':
        changed, result = delete_job(module, module.params["job_id"])
    if state == 'paused':
        changed, result = pause_job(module, module.params["job_id"])

    module.exit_json(changed=changed, **result)


def write_file(filename, contents):
    filename = os.path.expandvars(os.path.expanduser(filename))
    fh = open(filename, 'w')
    fh.writelines(line + '\n' for line in contents)
    fh.close()
    return filename


def prepare_file(module):
    DIRECTIVE = '#SBATCH'
    file_contents = []
    file_contents.append('#!/bin/bash')
    file_contents.append('## START OF HEADER ##')
    if module.params["job_name"]:
        file_contents.append(DIRECTIVE + ' -J ' + module.params['job_name'])
    else:
        module.fail_json(
            msg="Parameter 'job_name' is required"
        )
    if module.params["account"]:
        file_contents.append(DIRECTIVE + ' -A ' + module.params['account'])
    if module.params["queue"]:
        file_contents.append(DIRECTIVE + ' --partition=' + module.params['queue'])
    if module.params["wall_time_limit"]:
        file_contents.append(DIRECTIVE + ' --time=' + module.params['wall_time_limit'])
    if module.params["node_count"]:
        file_contents.append(DIRECTIVE + ' -N ' + str(module.params['node_count']))
    if module.params["core_count"]:
        file_contents.append(DIRECTIVE + ' -n ' + str(module.params['core_count']))
    if module.params["process_count_per_node"]:
        file_contents.append(DIRECTIVE + ' --ntasks-per-node=' + str(module.params['process_count_per_node']))
    if module.params["core_count_per_process"]:
        file_contents.append(DIRECTIVE + ' ----cpus-per-task=' + str(module.params['core_count_per_process']))
    if module.params["memory_limit"]:
        file_contents.append(DIRECTIVE + ' --mem=' + module.params['memory_limit'])
    if module.params["minimum_memory_per_processor"]:
        file_contents.append(DIRECTIVE + ' --mem-per-cpu=' + module.params['minimum_memory_per_processor'])
    if module.params["request_gpus"]:
        pass
    if module.params["request_specific_nodes"]:
        file_contents.append(DIRECTIVE + ' --nodelist=' + module.params['request_specific_nodes'])
    if module.params["job_array"]:
        file_contents.append(DIRECTIVE + ' -a ' + module.params['job_array'])
    if module.params["standard_output_file"]:
        file_contents.append(DIRECTIVE + ' --output=' + module.params['standard_output_file'])
    if module.params["standard_error_file"]:
        file_contents.append(DIRECTIVE + ' --error=' + module.params['standard_error_file'])
    if module.params["combine_stdout_stderr"]:
        pass
    if module.params["architecture_constraint"]:
        file_contents.append(DIRECTIVE + ' -C ' + module.params['architecture_constraint'])
    if module.params["copy_environment"]:
        file_contents.append(DIRECTIVE + ' --export=ALL ')
    if module.params["copy_environment_variable"]:
        file_contents.append(DIRECTIVE + ' --export=' + module.params['copy_environment_variable'])
    if module.params["job_dependency"]:
        file_contents.append(DIRECTIVE + ' --dependency=' + module.params['job_dependency'])
    if module.params["email_address"]:
        file_contents.append(DIRECTIVE + ' --mail-user=' + module.params['email_address'])
    if module.params["defer_job"]:
        file_contents.append(DIRECTIVE + ' --begin=' + module.params['defer_job'])
    if module.params["node_exclusive"]:
        file_contents.append(DIRECTIVE + ' --exclusive')
    if module.params["job_contents"]:
        file_contents.append(module.params['job_contents'])
    return file_contents


def create_job(module, filename):
    stdout = _execute_command(module, 'sbatch {}', filename)

    try:
        job_id = slurm_utils.parse_job_output(stdout)
    except Exception as err:
        module.fail_json(
                msg='Failed to parse sbatch output',
                details=to_text(err),
        )

    _wait_state(module, job_id, ['PENDING', 'RUNNING'])

    return True, _get_job_info(module, job_id)


def delete_job(module, job_id):
    state = _get_job_state(module, job_id).upper()

    if state in ['COMPLETED']:
        return False, {"slurm_job": state}

    _execute_command(module, 'scancel {}', job_id)

    new_state = _wait_state(module, job_id, ['CANCELLED'])

    return new_state != state, {"slurm_job": new_state}


def pause_job(module, job_id):
    state = _get_job_state(module, job_id).upper()

    if state == 'RUNNING':
        _execute_command(module, 'scontrol suspend {}', job_id)
    if state == 'PENDING':
        _execute_command(module, 'scontrol hold {}', job_id)

    new_state = _wait_state(module, job_id, ['PENDING', 'SUSPENDED'])

    return new_state != state, {"slurm_job": new_state}


def resume_job(module, job_id):
    state = _get_job_info(module, job_id)["slurm_job"]["JobState"]

    if state == 'PENDING':
        _execute_command(module, 'scontrol release {}', job_id)
    if state == 'SUSPENDED':
        _execute_command(module, 'scontrol resume {}', job_id)

    new_state = _wait_state(module, job_id, ['PENDING', 'RUNNING'])

    return new_state != state, {"slurm_job": new_state}


def _get_job_state(module, job_id):
    return _get_job_info(module, job_id)["slurm_job"]["JobState"].lower()


def _get_job_info(module, job_id):
    stdout = _execute_command(module, 'scontrol show job {}', job_id)

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


def _wait_state(module, job_id, states):
    delay = 1.0
    total_wait = 0
    max_wait = 10
    while total_wait < max_wait:
        state = _get_job_state(module, job_id).upper()
        if state in states:
            return state
        sleep(delay)
        total_wait += delay
    msg = "Timeout of {1} seconds exceeded while waiting for job '{0}'. State {2}"
    module.fail_json(msg=msg.format(job_id, max_wait, state))


def _execute_command(module, command, *args):
    try:
        command = command.format(*args)
        stdin, stdout, stderr = module.run_command(command)
        if stdin != 0:
            module.fail_json(
                    msg='{} command returned an error'.format(command),
                    details=to_text(stderr),
            )
    except Exception as err:
        module.fail_json(
                msg='Failed to execute {} command'.format(command),
                details=to_text(err),
        )

    return stdout


def main():
    run_module()


if __name__ == '__main__':
    main()
