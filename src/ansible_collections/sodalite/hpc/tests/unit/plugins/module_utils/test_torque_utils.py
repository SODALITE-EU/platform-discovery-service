from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from ansible_collections.sodalite.hpc.plugins.module_utils import torque_utils


class TestTorqueUtils:
    def test_torque_node(self, torque_node_stdout_1, torque_node_stdout_2):
        nodes = torque_utils.parse_node_output(torque_node_stdout_1)
        assert len(nodes) == 1
        assert nodes[0]['node_name'] == 'cloud8'
        assert nodes[0]['state'] == 'free'
        assert nodes[0]['power_state'] == 'Running'
        assert nodes[0]['np'] == '40'
        assert nodes[0]['properties'] == ['batch', 'gpu']
        assert nodes[0]['ntype'] == 'cluster'

        nodes = torque_utils.parse_node_output(torque_node_stdout_2)
        assert len(nodes) == 2
        assert nodes[1]['node_name'] == 'node-6.novalocal'
        assert nodes[1]['state'] == 'free'
        assert nodes[1]['power_state'] == 'Running'
        assert nodes[1]['np'] == '40'
        assert nodes[1]['properties'] == ['batch', 'cpu']
        assert nodes[1]['ntype'] == 'cluster'

    def test_torque_job(self, torque_job_stdout_2, torque_job_stdout_1_c):
        jobs = torque_utils.parse_job_output(torque_job_stdout_1_c)
        assert len(jobs) == 1
        assert jobs[0]['job_id'] == '2310.cloudserver'
        assert jobs[0]['Job_Name'] == 'hpc-test-1'
        assert jobs[0]['Job_Owner'] == 'user@cloudserver'
        assert jobs[0]['job_state'] == 'C'

        jobs = torque_utils.parse_job_output(torque_job_stdout_2)
        assert len(jobs) == 2
        assert jobs[1]['job_id'] == '2311.cloudserver'
        assert jobs[1]['Job_Name'] == 'hpc-test-1'
        assert jobs[1]['Job_Owner'] == 'user@cloudserver'
        assert jobs[1]['job_state'] == 'R'

    def test_torque_queue(self, torque_queue_stdout_1, torque_queue_stdout_2):
        partitions = torque_utils.parse_queue_output(torque_queue_stdout_1)
        assert len(partitions) == 1
        assert partitions[0]['queue_name'] == 'gpu'
        assert partitions[0]['queue_type'] == 'Execution'
        assert partitions[0]['total_jobs'] == '0'

        partitions = torque_utils.parse_queue_output(torque_queue_stdout_2)
        assert len(partitions) == 2
        assert partitions[1]['queue_name'] == 'cpu'
        assert partitions[1]['queue_type'] == 'Execution'
        assert partitions[1]['total_jobs'] == '0'
