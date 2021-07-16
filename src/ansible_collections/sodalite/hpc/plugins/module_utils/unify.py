from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from .date_utils import convert_torque_datetime


common_info = {
    "job_id": "str",
    "job_name": "str",
    "start_time": "datetime",
    "job_state": "str",
    "exit_code": "str",
    "work_dir": "str"
}


def transform_workdir(key, value):
    return "work_dir", value


def transform_exit_status(key, value):
    return "exit_code", value + ":0"


def transform_start_time(key, value):
    return "start_time", convert_torque_datetime(value)


def transform_job_state(key, value):
    states = {
        "C": "COMPLETED",
        "H": "SUSPENDED",
        "W": "PENDING",
        "R": "RUNNING",
    }

    return "job_state", states.get(value, value)


torque_to_slurm_info = {
    "init_work_dir": transform_workdir,
    "exit_status": transform_exit_status,
    "job_state": transform_job_state,
    "start_time": transform_start_time,
}


def transform_slurm_job_info(job_info):
    job = {}
    for key, value in job_info.items():
        if key in common_info:
            job[key] = value

    job["raw_output"] = job_info
    return job


def transform_torque_job_info(job_info):
    job = {}
    for key, value in job_info.items():
        transform = torque_to_slurm_info.get(key)
        if transform:
            key, value = transform(key, value)
        if key in common_info:
            job[key] = value

    job["raw_output"] = job_info
    return job
