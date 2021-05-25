from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import torque_job
from mock import patch, call
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestTorqueJobModule(TestHPCModule):
    def test_job_create(self, torque_job_stdout_1_r):
        set_module_args({"job_name": "my_job", "job_contents": "sleep 30", "keep_job_script": False})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout_submit = "2310.cloudserver"

            mock_run_command.side_effect = [(0, stdout_submit, ""),
                                            (0, torque_job_stdout_1_r, ""),
                                            (0, torque_job_stdout_1_r, "")]

            with pytest.raises(AnsibleExitJson) as result:
                torque_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'R'

        mock_run_command.assert_has_calls([call("qsub my_job.torque"),
                                           call("qstat -f 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver")])

    def test_job_pause(self, torque_job_stdout_1_r, torque_job_stdout_1_s):
        set_module_args({"job_id": "2310.cloudserver", "state": "paused"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, torque_job_stdout_1_r, ""),
                                            (0, "", ""),
                                            (0, torque_job_stdout_1_s, ""),
                                            (0, torque_job_stdout_1_s, "")]

            with pytest.raises(AnsibleExitJson) as result:
                torque_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'H'

        mock_run_command.assert_has_calls([call("qstat -f 2310.cloudserver"),
                                           call("qhold 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver")])

    def test_job_resume(self, torque_job_stdout_1_r, torque_job_stdout_1_s):
        set_module_args({"job_id": "2310.cloudserver"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, torque_job_stdout_1_s, ""),
                                            (0, "", ""),
                                            (0, torque_job_stdout_1_r, ""),
                                            (0, torque_job_stdout_1_r, "")]

            with pytest.raises(AnsibleExitJson) as result:
                torque_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'R'

        mock_run_command.assert_has_calls([call("qstat -f 2310.cloudserver"),
                                           call("qrls 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver")])

    def test_job_cancel(self, torque_job_stdout_1_r, torque_job_stdout_1_c):
        set_module_args({"job_id": "2310.cloudserver", "state": "cancelled"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, torque_job_stdout_1_r, ""),
                                            (0, "", ""),
                                            (0, torque_job_stdout_1_c, ""),
                                            (0, torque_job_stdout_1_c, "")]

            with pytest.raises(AnsibleExitJson) as result:
                torque_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '2310.cloudserver'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'C'

        mock_run_command.assert_has_calls([call("qstat -f 2310.cloudserver"),
                                           call("qdel 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver")])

    def test_get_job_timeout_fail(self, torque_job_stdout_1_s):
        set_module_args({"job_name": "my_job", "job_contents": "sleep 30", "keep_job_script": False})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout_submit = "2310.cloudserver"
            stdout_status = torque_job_stdout_1_s

            mock_run_command.side_effect = [(0, stdout_submit, ""),
                                            (0, stdout_status, ""),
                                            (0, stdout_status, "")]

            with pytest.raises(AnsibleFailJson) as result:
                torque_job.main()
            assert result.value.args[0]['failed'] is True
            assert result.value.args[0]['msg'] == "Failed to execute qstat -f 2310.cloudserver command"

        mock_run_command.assert_has_calls([call("qsub my_job.torque"),
                                           call("qstat -f 2310.cloudserver"),
                                           call("qstat -f 2310.cloudserver")])

    def test_get_job_params_fail(self, torque_job_stdout_1_r):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = torque_job_stdout_1_r
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                torque_job.main()

        assert not mock_run_command.called
