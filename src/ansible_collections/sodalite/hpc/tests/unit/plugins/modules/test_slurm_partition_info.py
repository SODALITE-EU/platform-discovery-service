from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import slurm_partition_info
from mock import patch
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestSlurmPartitionInfoModule(TestHPCModule):
    def test_list_partitions(self, slurm_partition_stdout_2):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = slurm_partition_stdout_2
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                slurm_partition_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['partitions']) == 2
            assert result.value.args[0]['partitions'][0]['partition_name'] == 'debug'

        mock_run_command.assert_called_once_with("scontrol show partition")

    def test_get_partition(self, slurm_partition_stdout_1):
        set_module_args({"partition": "debug"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = slurm_partition_stdout_1
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                slurm_partition_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['partitions']) == 1
            assert result.value.args[0]['partitions'][0]['partition_name'] == 'debug'

        mock_run_command.assert_called_once_with("scontrol show partition debug")

    def test_get_partition_fail(self):
        set_module_args({"partition": "debug"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = ""
            stderr = "Error occurred executing command"
            rc = 1
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                slurm_partition_info.main()

        mock_run_command.assert_called_once_with("scontrol show partition debug")
