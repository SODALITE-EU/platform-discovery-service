from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from time import sleep
from abc import abstractmethod
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text

import os


class HpcModule(object):

    argument_spec = {}
    module_kwargs = {}

    def __init__(self):
        self.ansible = AnsibleModule(argument_spec=self.argument_spec,
                                     **self.module_kwargs)

    def execute_command(self, command, *args):
        try:
            command = command.format(*args)
            stdin, stdout, stderr = self.ansible.run_command(command)
            if stdin != 0:
                self.ansible.fail_json(
                    msg='{0} command returned an error'.format(command),
                    details=to_text(stderr),
                )
        except Exception as err:
            self.ansible.fail_json(
                msg='Failed to execute {0} command'.format(command),
                details=to_text(err),
            )

        return stdout

    @abstractmethod
    def get_job_state(self, job_id):
        pass

    @abstractmethod
    def get_job_info(self, job_id):
        pass


class HpcJobModule(HpcModule):
    def __init__(self, directive, job_file_ext):
        self.DIRECTIVE = directive
        self.job_file_ext = job_file_ext
        self.argument_spec = dict(
            job_id=dict(type='str', required=False),
            state=dict(default='queued', choices=['queued', 'paused', 'cancelled']),
            job_name=dict(type='str', required=False),
            job_options=dict(type='str', required=False),
            job_src=dict(type='str', required=False),
            job_contents=dict(type='str', required=False),
            job_workspace=dict(type='str', required=False),
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
            combine_stdout_stderr=dict(type='bool', required=False),
            architecture_constraint=dict(type='str', required=False),
            copy_environment=dict(type='bool', required=False),
            copy_environment_variable=dict(type='str', required=False),
            job_dependency=dict(type='str', required=False),
            request_event_notification=dict(
                type='list',
                elements="str",
                default='none',
                choices=['begin', 'end', 'fail', 'invalid_depend', 'time_limit', 'none', 'all']),
            email_address=dict(type='str', required=False),
            defer_job=dict(type='str', required=False),
            node_exclusive=dict(type='bool', required=False),
            keep_job_script=dict(type='bool', default=True)
        )

        super(HpcJobModule, self).__init__()

    def wait_state(self, job_id, states):
        delay = 1.0
        total_wait = 0
        max_wait = 10
        while total_wait < max_wait:
            state = self.get_job_state(job_id)
            if state in states:
                return state
            sleep(delay)
            total_wait += delay
        msg = "Timeout of {1} seconds exceeded while waiting for job '{0}'. State {2}"
        self.ansible.fail_json(msg=msg.format(job_id, max_wait, state))

    def write_file(self, workspace, filename, contents):
        if workspace:
            filename = os.path.join(workspace, filename)
        else:
            filename = os.path.expandvars(os.path.expanduser(filename))
        fh = open(filename, 'w')
        fh.writelines(line + '\n' for line in contents)
        fh.close()
        return filename

    def run_module(self):
        state = self.ansible.params['state']

        if state == 'queued' and not (self.ansible.params["job_name"] or self.ansible.params["job_id"]):
            self.ansible.fail_json(
                msg="Parameter 'job_name' or 'job_id' is required if state == 'queued'"
            )

        if state == 'cancelled' and not self.ansible.params["job_id"]:
            self.ansible.fail_json(
                msg="Parameter 'job_id' is required if state == 'cancelled'"
            )

        if state == 'paused' and not self.ansible.params["job_id"]:
            self.ansible.fail_json(
                msg="Parameter 'job_id' is required if state == 'paused'"
            )

        if state == 'queued':
            if self.ansible.params["job_name"]:
                contents = self.prepare_file()
                filename = self.write_file(self.ansible.params["job_workspace"],
                                           "{0}.{1}".format(self.ansible.params["job_name"],
                                                            self.job_file_ext),
                                           contents)
                changed, result = self.create_job(filename)
                if not self.ansible.params["keep_job_script"]:
                    self.ansible.add_cleanup_file(filename)
            else:
                changed, result = self.resume_job(self.ansible.params["job_id"])
        if state == 'cancelled':
            changed, result = self.delete_job(self.ansible.params["job_id"])
        if state == 'paused':
            changed, result = self.pause_job(self.ansible.params["job_id"])

        self.ansible.exit_json(changed=changed, **result)

    @abstractmethod
    def prepare_file(self):
        pass

    @abstractmethod
    def create_job(self, job_id):
        pass

    @abstractmethod
    def delete_job(self, job_id):
        pass

    @abstractmethod
    def pause_job(self, job_id):
        pass

    @abstractmethod
    def resume_job(self, job_id):
        pass
