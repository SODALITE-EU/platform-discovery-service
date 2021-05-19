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
module: job_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List HPC jobs
description:
  - Retrieve information about jobs on Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_job_info
  - module: sodalite.hpc.torque_job_info
options:
  job_id:
    type: str
    description:
      - The ID of the job to retrieve.
"""

EXAMPLES = """
- name: List all jobs
  sodalite.hpc.job_info:
  register: result
- name: List the selected job
  sodalite.hpc.job_info:
    job_id: my_job
  register: result
- name: Show job
  ansible.builtin.debug:
    msg: "{{ result.jobs[0] }}"
"""

RETURN = """
jobs:
  description: List of HPC jobs.
  returned: success
  type: list
  elements: dict
"""
