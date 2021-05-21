from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible.errors import AnsibleActionFail
from ansible.playbook.task import Task
from ansible_collections.sodalite.hpc.plugins.action import job_info


# We can test only one action plugin, as their implementation is basically equal
class TestRun:
    def test_success(self, mocker):
        task = mocker.MagicMock(Task, async_val=0, args=dict(
            name="test/job",
            version="1.2.3",
        ))
        action = job_info.ActionModule(
            task, mocker.MagicMock(), mocker.MagicMock(), loader=None,
            templar=None, shared_loader_obj=None,
        )
        action._execute_module = mocker.MagicMock()
        action._execute_module.side_effect = [{"wm_type": ["Slurm"]}, "success"]

        result = action.run()

        assert result == "success"

    def test_fail(self, mocker):
        task = mocker.MagicMock(Task, async_val=0, args=dict(
            name="test/job",
            version="1.2.3",
        ))
        action = job_info.ActionModule(
            task, mocker.MagicMock(), mocker.MagicMock(), loader=None,
            templar=None, shared_loader_obj=None,
        )
        action._execute_module = mocker.MagicMock()
        action._execute_module.side_effect = [{"wm_type": ["Non_Supported"]}]

        with pytest.raises(AnsibleActionFail) as result:
            action.run()

        assert str(result.value) == "Unsupported workload manager"
