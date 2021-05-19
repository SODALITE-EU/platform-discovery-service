from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  job_id:
    description:
      - String identifier of the job.
      - Required if P(state) is C(paused) or C(cancelled).
    type: str
  state:
    description:
      - Target state of the job.
    type: str
    default: queued
    choices: [queued, paused, cancelled]
  job_name:
    description:
      - Name of the job.
      - Required if P(state) is C(queued).
    type: str
  job_options:
    description:
      - Optional workload manager instructions.
    type: str
  job_contents:
    description:
      - Contents of the job.
    type: str
  account:
    description:
      - Charge resources used by this job to specified account.
    type: str
  queue:
    description:
      - Request a specific queue (partition) for the resource allocation.
    type: str
  wall_time_limit:
    description:
      - Set a limit on the total run time of the job allocation.
    type: str
  node_count:
    description:
      - A number of nodes to be allocated to this job.
    type: int
  core_count:
    description:
      - A number of tasks(cores) to be allocated to this job.
    type: int
  process_count_per_node:
    description:
      - Request this number of processes be invoked on each node.
    type: int
  core_count_per_process:
    description:
      - Advise that ensuing job steps will require this number of processors per task.
    type: int
  memory_limit:
    description:
      - Specify the real memory required per node.
    type: str
  minimum_memory_per_processor:
    description:
      - Minimum memory required per allocated CPU.
    type: str
  request_gpus:
    description:
      - Specifies a list of GPU resources.
    type: str
  request_specific_nodes:
    description:
      - Request a specific list of hosts.
    type: str
  job_array:
    description:
      - Submit a job array, multiple jobs to be executed with identical parameters.
    type: str
  standard_output_file:
    description:
      - Connect the job standard output directly to the file name specified.
    type: str
  standard_error_file:
    description:
      - Connect the job standard error directly to the file name specified.
    type: str
  combine_stdout_stderr:
    description:
      - Combine the job standard output with standard error.
    type: bool
  architecture_constraint:
    description:
      - Specify which features are required by the job.
    type: str
  copy_environment:
    description:
      - Propagate all environment variables from the submission environment to the job.
    type: bool
  copy_environment_variable:
    description:
      - Identify which environment variables from the submission environment are propagated to the job.
    type: str
  job_dependency:
    description:
      - Defer the start of this job until the specified dependencies have been completed.
    type: str
  request_event_notification:
    description:
      - Notify user by email when certain event types occur.
    type: str
  email_address:
    description:
      - Email address to receive notifications of state changes.
    type: str
  defer_job:
    description:
      - Defer the allocation of the job until the specified time.
    type: str
  node_exclusive:
    description:
      - The job allocation can not share nodes with other running jobs.
    type: bool
  keep_job_script:
    description:
      - Keep job script file after execution.
    type: bool
    default: True
"""
