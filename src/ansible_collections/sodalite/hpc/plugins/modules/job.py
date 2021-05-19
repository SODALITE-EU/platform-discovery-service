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
module: job
author:
  - Alexander Maslennikov (@amaslenn)
short_description: Manage HPC jobs
description:
  - Create, suspend or cancel HPC job.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_job
  - module: sodalite.hpc.torque_job
extends_documentation_fragment:
  - sodalite.hpc.job
"""

EXAMPLES = """
- name: run the job
  sodalite.hpc.job:
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
  sodalite.hpc.job:
  job_id: '{{ job_info.jobs[0].job_id }}'
  state: 'paused'

- name: resume the job
  become: true
  sodalite.hpc.job:
  job_id: '{{ job_info.jobs[0].job_id }}'

- name: cancel the job
  sodalite.hpc.job:
  job_id: '{{ job_info.jobs[0].job_id }}'
  state: 'cancelled'
"""

RETURN = """
jobs:
  description: List of jobs that has one element.
  returned: success
  type: list
  elements: dict
"""
