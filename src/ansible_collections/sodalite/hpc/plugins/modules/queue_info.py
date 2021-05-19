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
module: queue_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List HPC queues
description:
  - Retrieve information about queues on Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_partition_info
  - module: sodalite.hpc.torque_queue_info
options:
  queue:
    type: str
    description:
      - Name of the queue to retrieve.
"""

EXAMPLES = """
- name: List all queues
  sodalite.hpc.queue_info:
  register: result
- name: List the selected node
  sodalite.hpc.queue_info:
    queue: my_queue
  register: result
- name: Show queue
  ansible.builtin.debug:
    msg: "{{ result.queues[0] }}"
"""

RETURN = """
queues:
  description: List of HPC queues.
  returned: success
  type: list
  elements: dict
"""
