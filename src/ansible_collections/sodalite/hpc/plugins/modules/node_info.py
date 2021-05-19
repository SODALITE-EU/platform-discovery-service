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
module: node_info
author:
  - Alexander Maslennikov (@amaslenn)
short_description: List HPC nodes
description:
  - Retrieve information about nodes on Workload Manager.
version_added: 1.0.0
seealso:
  - module: sodalite.hpc.slurm_node_info
  - module: sodalite.hpc.torque_node_info
options:
  node:
    type: str
    description:
      - Name of the node to retrieve.
"""

EXAMPLES = """
- name: List all nodes
  sodalite.hpc.node_info:
  register: result
- name: List the selected node
  sodalite.hpc.node_info:
    node: my_node
  register: result
- name: Show node
  ansible.builtin.debug:
    msg: "{{ result.nodes[0] }}"
"""

RETURN = """
nodes:
  description: List of HPC nodes.
  returned: success
  type: list
  elements: dict
"""
