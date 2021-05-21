from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import torque_job_info
from mock import patch
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestTorqueJobInfoModule(TestHPCModule):
    def test_list_jobs(self, torque_job_stdout_2):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = torque_job_stdout_2
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                torque_job_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['jobs']) == 2
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'

        mock_run_command.assert_called_once_with("qstat -f")

    def test_get_job(self, torque_job_stdout_1_r):
        set_module_args({"job_id": "2310.cloudserver"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = torque_job_stdout_1_r
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                torque_job_info.main()
            assert result.value.args[0]['changed'] is False
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'

        mock_run_command.assert_called_once_with("qstat -f 2310.cloudserver")

    def test_get_job_fail(self):
        set_module_args({"job_id": "2310.cloudserver"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = ""
            stderr = "Error occurred executing command"
            rc = 1
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                torque_job_info.main()

        mock_run_command.assert_called_once_with("qstat -f 2310.cloudserver")
