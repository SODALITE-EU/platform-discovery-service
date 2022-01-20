from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import slurm_job
from unittest.mock import patch, call
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestSlurmJobModule(TestHPCModule):
    def test_job_create(self, slurm_job_stdout_1_r):
        set_module_args({"job_name": "my_job", "job_contents": "sleep 30", "keep_job_script": False})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout_submit = "Submitted batch job 70"

            mock_run_command.side_effect = [(0, stdout_submit, ""),
                                            (0, slurm_job_stdout_1_r, ""),
                                            (0, slurm_job_stdout_1_r, "")]

            with pytest.raises(AnsibleExitJson) as result:
                slurm_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '70'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'RUNNING'

        mock_run_command.assert_has_calls([call("sbatch my_job.slurm"),
                                           call("scontrol show job 70"),
                                           call("scontrol show job 70")])

    def test_job_pause(self, slurm_job_stdout_1_r, slurm_job_stdout_1_s):
        set_module_args({"job_id": "70", "state": "paused"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, slurm_job_stdout_1_r, ""),
                                            (0, "", ""),
                                            (0, slurm_job_stdout_1_s, ""),
                                            (0, slurm_job_stdout_1_s, "")]

            with pytest.raises(AnsibleExitJson) as result:
                slurm_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '70'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'SUSPENDED'

        mock_run_command.assert_has_calls([call("scontrol show job 70"),
                                           call("scontrol suspend 70"),
                                           call("scontrol show job 70"),
                                           call("scontrol show job 70")])

    def test_job_resume(self, slurm_job_stdout_1_r, slurm_job_stdout_1_s):
        set_module_args({"job_id": "70"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, slurm_job_stdout_1_s, ""),
                                            (0, "", ""),
                                            (0, slurm_job_stdout_1_r, ""),
                                            (0, slurm_job_stdout_1_r, "")]

            with pytest.raises(AnsibleExitJson) as result:
                slurm_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '70'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'RUNNING'

        mock_run_command.assert_has_calls([call("scontrol show job 70"),
                                           call("scontrol resume 70"),
                                           call("scontrol show job 70"),
                                           call("scontrol show job 70")])

    def test_job_cancel(self, slurm_job_stdout_1_r, slurm_job_stdout_1_c):
        set_module_args({"job_id": "70", "state": "cancelled"})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, slurm_job_stdout_1_r, ""),
                                            (0, "", ""),
                                            (0, slurm_job_stdout_1_c, ""),
                                            (0, slurm_job_stdout_1_c, "")]

            with pytest.raises(AnsibleExitJson) as result:
                slurm_job.main()
            assert result.value.args[0]['changed'] is True
            assert len(result.value.args[0]['jobs']) == 1
            assert result.value.args[0]['jobs'][0]['job_id'] == '70'
            assert result.value.args[0]['jobs'][0]['job_state'] == 'CANCELLED'

        mock_run_command.assert_has_calls([call("scontrol show job 70"),
                                           call("scancel 70"),
                                           call("scontrol show job 70"),
                                           call("scontrol show job 70")])

    def test_get_job_timeout_fail(self, slurm_job_stdout_1_s):
        set_module_args({"job_name": "my_job", "job_contents": "sleep 30", "keep_job_script": False})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout_submit = "Submitted batch job 70"
            stdout_status = slurm_job_stdout_1_s

            mock_run_command.side_effect = [(0, stdout_submit, ""),
                                            (0, stdout_status, ""),
                                            (0, stdout_status, "")]

            with pytest.raises(AnsibleFailJson) as result:
                slurm_job.main()
            assert result.value.args[0]['failed'] is True
            assert result.value.args[0]['msg'] == "Failed to execute scontrol show job 70 command"

        mock_run_command.assert_has_calls([call("sbatch my_job.slurm"),
                                           call("scontrol show job 70"),
                                           call("scontrol show job 70")])

    def test_get_job_params_fail(self, slurm_job_stdout_1_r):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = slurm_job_stdout_1_r
            stderr = ''
            rc = 0
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleFailJson):
                slurm_job.main()

        assert not mock_run_command.called
