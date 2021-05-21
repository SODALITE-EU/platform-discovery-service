from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from ansible_collections.sodalite.hpc.plugins.module_utils import slurm_utils


class TestTorqueUtils:
    @pytest.fixture
    def slurm_node_gres1(self):
        stdout = """
        Gres=gpu:tesla:2,gpu:kepler:2,mps:400,bandwidth:lustre:no_consume:4G
        """
        return stdout

    @pytest.fixture
    def slurm_node_gres2(self):
        stdout = """
        Gres=gpu:4(S:0-1)
        """
        return stdout

    def test_slurm_node(self, slurm_node_stdout_1, slurm_node_stdout_2):
        nodes = slurm_utils.parse_output(slurm_node_stdout_1, "NodeName")
        assert len(nodes) == 1
        assert nodes[0]['node_name'] == 'compute01'
        assert nodes[0]['arch'] == 'x86_64'
        assert nodes[0]['cores_per_socket'] == '6'
        assert nodes[0]['cpu_alloc'] == '0'
        assert nodes[0]['cpu_tot'] == '24'
        assert nodes[0]['cpu_load'] == '0.00'

        nodes = slurm_utils.parse_output(slurm_node_stdout_2, "NodeName")
        assert len(nodes) == 2
        assert nodes[1]['node_name'] == 'wn2'
        assert nodes[1]['arch'] == 'x86_64'
        assert nodes[1]['cores_per_socket'] == '1'
        assert nodes[1]['cpu_alloc'] == '0'
        assert nodes[1]['cpu_tot'] == '1'
        assert nodes[1]['cpu_load'] == '0.01'

    def test_slurm_job(self, slurm_job_stdout_3, slurm_job_stdout_1_r):
        jobs = slurm_utils.parse_output(slurm_job_stdout_1_r, "JobId")
        assert len(jobs) == 1
        assert jobs[0]['job_id'] == '70'
        assert jobs[0]['job_name'] == 'test'
        assert jobs[0]['priority'] == '0'
        assert jobs[0]['job_state'] == 'RUNNING'

        jobs = slurm_utils.parse_output(slurm_job_stdout_3, "JobId")
        assert len(jobs) == 3
        assert jobs[1]['job_id'] == '71'
        assert jobs[1]['job_name'] == 'test'
        assert jobs[1]['priority'] == '0'
        assert jobs[1]['job_state'] == 'SUSPENDED'

    def test_slurm_partition(self, slurm_partition_stdout_1, slurm_partition_stdout_2):
        partitions = slurm_utils.parse_output(slurm_partition_stdout_1, "PartitionName")
        assert len(partitions) == 1
        assert partitions[0]['partition_name'] == 'debug'
        assert partitions[0]['allow_groups'] == 'ALL'
        assert partitions[0]['over_time_limit'] == 'NONE'

        partitions = slurm_utils.parse_output(slurm_partition_stdout_2, "PartitionName")
        assert len(partitions) == 2
        assert partitions[1]['partition_name'] == 'test'
        assert partitions[1]['allow_groups'] == 'ALL'
        assert partitions[1]['over_time_limit'] == 'NONE'

    def test_slurm_node_gres(self, slurm_node_gres1, slurm_node_gres2):
        gres = slurm_utils.parse_gres(slurm_node_gres1)
        assert gres["total_gpu"] == 4
        gres = slurm_utils.parse_gres(slurm_node_gres2)
        assert gres["total_gpu"] == 4
