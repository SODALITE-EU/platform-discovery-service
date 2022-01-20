from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import torque_queue_info
from unittest.mock import patch
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestTorqueQueueInfoModule(TestHPCModule):
    def test_list_queues(self, torque_queue_stdout_2):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = torque_queue_stdout_2
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                torque_queue_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['queues']) == 2
            assert result.value.args[0]['queues'][0]['queue_name'] == 'gpu'

        mock_run_command.assert_called_once_with("qstat -Q -f -1")

    def test_get_queue(self, torque_queue_stdout_1):
        set_module_args({"queue": "gpu"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = torque_queue_stdout_1
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                torque_queue_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['queues']) == 1
            assert result.value.args[0]['queues'][0]['queue_name'] == 'gpu'

        mock_run_command.assert_called_once_with("qstat -Q -f -1 gpu")

    def test_get_queue_fail(self):
        set_module_args({"queue": "gpu"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = ""
            stderr = "Error occurred executing command"
            rc = 1
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                torque_queue_info.main()

        mock_run_command.assert_called_once_with("qstat -Q -f -1 gpu")
