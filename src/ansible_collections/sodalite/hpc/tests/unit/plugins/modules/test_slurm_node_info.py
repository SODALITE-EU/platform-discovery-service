from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import slurm_node_info
from unittest.mock import patch
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestSlurmNodeInfoModule(TestHPCModule):
    def test_list_nodes(self, slurm_node_stdout_2):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = slurm_node_stdout_2
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                slurm_node_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['nodes']) == 2
            assert result.value.args[0]['nodes'][0]['node_name'] == 'compute01'

        mock_run_command.assert_called_once_with("scontrol show nodes")

    def test_get_node(self, slurm_node_stdout_1):
        set_module_args({"node": "compute01"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = slurm_node_stdout_1
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                slurm_node_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['nodes']) == 1
            assert result.value.args[0]['nodes'][0]['node_name'] == 'compute01'

        mock_run_command.assert_called_once_with("scontrol show node compute01")

    def test_get_node_fail(self):
        set_module_args({"node": "compute01"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = ""
            stderr = "Error occurred executing command"
            rc = 1
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                slurm_node_info.main()

        mock_run_command.assert_called_once_with("scontrol show node compute01")
