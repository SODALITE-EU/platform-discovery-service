from ansible_collections.sodalite.hpc.plugins.module_utils import (
    slurm_utils)
from ansible_collections.sodalite.hpc.plugins.modules import (
    slurm_node_info, slurm_partition_info)
from ansible.module_utils.basic import AnsibleModule
import pytest


class TestTorqueHPCUtils:

    @pytest.fixture
    def slurm_node(self):
        stdout = """
        NodeName=compute01 Arch=x86_64 CoresPerSocket=6
            CPUAlloc=0 CPUTot=24 CPULoad=0.00
            AvailableFeatures=intel,gpu,v100
            ActiveFeatures=intel,gpu,v100
            Gres=gpu:4(S:0-1)
            NodeAddr=compute01 NodeHostName=compute01 Version=20.02.6
            OS=Linux 5.7.12-1.el8.elrepo.x86_64 #1 SMP Fri Jul 31 16:22:54 EDT 2020
            RealMemory=257000 AllocMem=0 FreeMem=256138 Sockets=2 Boards=1
            State=IDLE ThreadsPerCore=2 TmpDisk=0 Weight=1000 Owner=N/A MCS_label=N/A
            Partitions=compute
            BootTime=2020-11-24T15:08:24 SlurmdStartTime=2020-11-27T13:15:19
            CfgTRES=cpu=24,mem=257000M,billing=62
            AllocTRES=
            CapWatts=n/a
            CurrentWatts=0 AveWatts=0
            ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s

        NodeName=wn2 Arch=x86_64 CoresPerSocket=1
            CPUAlloc=0 CPUTot=1 CPULoad=0.01
            AvailableFeatures=(null)
            ActiveFeatures=(null)
            Gres=(null)
            NodeAddr=wn2 NodeHostName=wn2
            OS=Linux 3.10.0-1127.13.1.el7.x86_64 #1 SMP Tue Jun 23 15:46:38 UTC 2020
            RealMemory=1 AllocMem=0 FreeMem=N/A Sockets=1 Boards=1
            State=DOWN* ThreadsPerCore=1 TmpDisk=0 Weight=1 Owner=N/A MCS_label=N/A
            Partitions=debug
            BootTime=2020-09-21T13:57:57 SlurmdStartTime=2020-09-21T14:01:11
            CfgTRES=cpu=1,mem=1M,billing=1
            AllocTRES=
            CapWatts=n/a
            CurrentWatts=0 AveWatts=0
            ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s
            Reason=Not responding [root@2020-09-21T14:31:24]
        """
        return stdout

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

    def test_slurm_node(self, slurm_node):
        nodes = slurm_utils.parse_output(slurm_node, "NodeName")
        assert len(nodes) == 2

    def test_slurm_node_gres(self, slurm_node_gres1, slurm_node_gres2):
        gres = slurm_utils.parse_gres(slurm_node_gres1)
        assert gres["total_gpu"] == 4
        gres = slurm_utils.parse_gres(slurm_node_gres2)
        assert gres["total_gpu"] == 4

    def test_slurm_node_info(self, mocker, slurm_node):
        module = mocker.patch.object(AnsibleModule,
                                     'run_command', return_value=True)
        module.return_value = slurm_node, None, None
        result = slurm_node_info.execute_command(module)
        assert result == {}
        mocker.patch("ansible.module_utils.basic.AnsibleModule.exit_json", return_value=None)
        mocker.patch("ansible.module_utils.basic.AnsibleModule.__init__", return_value=None)
        mocker.patch("ansible_collections.sodalite.hpc.plugins.modules.slurm_node_info.execute_command")
        slurm_node_info.run_module()

    def test_slurm_partition_info(self, mocker, slurm_node):
        module = mocker.patch.object(AnsibleModule, 'run_command')
        module.return_value = "", None, None

        result = slurm_partition_info.execute_command(module)
        assert result == {}
        mocker.patch("ansible.module_utils.basic.AnsibleModule.exit_json", return_value=None)
        mocker.patch("ansible.module_utils.basic.AnsibleModule.__init__", return_value=None)
        mocker.patch("ansible_collections.sodalite.hpc.plugins.modules.slurm_partition_info.execute_command")
        slurm_partition_info.run_module()
