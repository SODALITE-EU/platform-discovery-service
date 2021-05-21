from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import basic
from ansible_collections.sodalite.hpc.plugins.modules import wm_info
from mock import patch, call
import pytest

from .utils import (
    AnsibleExitJson, AnsibleFailJson, TestHPCModule, set_module_args,
)


class TestSlurmJobInfoModule(TestHPCModule):
    def test_list_jobs(self):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            mock_run_command.side_effect = [(0, "yes", ""),
                                            (0, "", "")]

            with pytest.raises(AnsibleExitJson) as result:
                wm_info.main()
            assert result.value.args[0]['changed'] is False
            assert result.value.args[0]['wm_type'] == ["Torque"]

        mock_run_command.assert_has_calls([call("command -v qsub"),
                                           call("command -v sbatch")])

    def test_get_job_fail(self):
        set_module_args({})

        with patch.object(basic.AnsibleModule, 'run_command') as mock_run_command:
            stdout = ""
            stderr = "Error occurred executing command"
            rc = 1
            mock_run_command.return_value = rc, stdout, stderr

            with pytest.raises(AnsibleExitJson) as result:
                wm_info.main()
            assert result.value.args[0]['changed'] is False
            assert result.value.args[0]['wm_type'] == []

        mock_run_command.assert_has_calls([call("command -v qsub"),
                                           call("command -v sbatch")])
