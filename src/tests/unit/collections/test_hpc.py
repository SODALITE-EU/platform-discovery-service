from ansible_collections.sodalite.hpc.plugins.module_utils import torque_utils
import pytest


class TestHPCUtils:
    @pytest.fixture
    def torque_node_stdout(self):
        stdout = """
        cloud8
            state = free
            power_state = Running
            np = 40
            properties = batch,gpu
            ntype = cluster
            status = opsys=linux,uname=Linux cloud8 3.10.0-1127.10.1.el7.x86_64 #1 SMP Wed Jun 3 14:28:03 UTC 2020 x86_64,nsessions=0,nusers=0,idletime=12013265,totmem=135777452kb,availmem=123727248kb,physmem=131583152kb,ncpus=40,loadave=0.16,gres=,netload=2262988229356,state=free,varattr= ,cpuclock=Fixed,macaddr=ac:1f:6b:6a:ed:34,version=6.1.3,rectime=1606228864,jobs=
            mom_service_port = 15002
            mom_manager_port = 15003
            gpus = 1
            gpu_status = gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;gpu_fan_speed=25%;gpu_memory_total=11178 MB;gpu_memory_used=0 MB;gpu_mode=Exclusive_Process;gpu_state=Unallocated;gpu_utilization=0%;gpu_memory_utilization=0%;gpu_temperature=40 C,gpu_display=Disabled,driver_ver=450.51.05,timestamp=Tue Nov 24 15:41:03 2020
            total_sockets = 2
            total_numa_nodes = 2
            total_cores = 20
            total_threads = 40
            dedicated_sockets = 0
            dedicated_numa_nodes = 0
            dedicated_cores = 0
            dedicated_threads = 0

        node-6.novalocal
            state = free
            power_state = Running
            np = 40
            properties = batch,cpu
            ntype = cluster
            status = opsys=linux,uname=Linux node-6.novalocal 3.10.0-1062.12.1.el7.x86_64 #1 SMP Tue Feb 4 23:02:59 UTC 2020 x86_64,nsessions=0,nusers=0,idletime=3047614,totmem=131583200kb,availmem=120063364kb,physmem=131583200kb,ncpus=40,loadave=0.01,gres=,netload=1698453148975,state=free,varattr= ,cpuclock=Fixed,macaddr=ac:1f:6b:6a:ec:38,version=6.1.3,rectime=1606228846,jobs=
            mom_service_port = 15002
            mom_manager_port = 15003
            gpus = 1
            gpu_status = gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;gpu_fan_speed=26%;gpu_memory_total=11178 MB;gpu_memory_used=0 MB;gpu_mode=Exclusive_Process;gpu_state=Unallocated;gpu_utilization=2%;gpu_memory_utilization=0%;gpu_temperature=42 C,gpu_display=Disabled,driver_ver=450.51.05,timestamp=Tue Nov 24 14:40:45 2020
            total_sockets = 2
            total_numa_nodes = 2
            total_cores = 20
            total_threads = 40
            dedicated_sockets = 0
            dedicated_numa_nodes = 0
            dedicated_cores = 0
            dedicated_threads = 0
            """
        return stdout

    @pytest.fixture
    def torque_queue_stdout(self):
        stdout = """
        Queue: gpu
            queue_type = Execution
            total_jobs = 0
            state_count = Transit:0 Queued:0 Held:0 Waiting:0 Running:0 Exiting:0 Complete:0
            resources_default.walltime = 01:00:00
            resources_default.nodes = 1
            mtime = 1604051516
            enabled = True
            started = True

        Queue: cpu
            queue_type = Execution
            total_jobs = 0
            state_count = Transit:0 Queued:0 Held:0 Waiting:0 Running:0 Exiting:0 Complete:0
            resources_default.walltime = 01:00:00
            resources_default.nodes = 1
            mtime = 1604051516
            enabled = True
            started = True
        """
        return stdout

    @pytest.fixture
    def torque_gpu_status(self):
        stdout = """
        gpu[1]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;gpu_fan_speed=25%;gpu_memory_total=11178 MB;gpu_memory_used=0 MB;gpu_mode=Exclusive_Process;gpu_state=Unallocated;gpu_utilization=0%;gpu_memory_utilization=0%;gpu_temperature=40 C,gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;gpu_fan_speed=25%;gpu_memory_total=11178 MB;gpu_memory_used=0 MB;gpu_mode=Exclusive_Process;gpu_state=Unallocated;gpu_utilization=0%;gpu_memory_utilization=0%;gpu_temperature=40 C,gpu_display=Disabled,driver_ver=450.51.05,timestamp=Tue Nov 24 15:41:03 2020
        """
        return stdout

    @pytest.fixture
    def torque_node_status(self):
        stdout = """
        opsys=linux,uname=Linux node-6.novalocal 3.10.0-1062.12.1.el7.x86_64 #1 SMP Tue Feb 4 23:02:59 UTC 2020 x86_64,nsessions=0,nusers=0,idletime=3047614,totmem=131583200kb,availmem=120063364kb,physmem=131583200kb,ncpus=40,loadave=0.01,gres=,netload=1698453148975,state=free,varattr= ,cpuclock=Fixed,macaddr=ac:1f:6b:6a:ec:38,version=6.1.3,rectime=1606228846,jobs=
        """
        return stdout

    @pytest.fixture
    def torque_queue_state(self):
        stdout = """
        Transit:0 Queued:0 Held:0 Waiting:0 Running:0 Exiting:0 Complete:0
        """
        return stdout        

    @pytest.fixture
    def torque_node_properties(self):
        stdout = """
        batch,cpu,gpu
        """
        return stdout   

    def test_torque_utils_node(self, torque_node_stdout):
        nodes = torque_utils.parse_node_output(torque_node_stdout)
        assert len(nodes) == 2
        assert nodes[0]["node_name"] == "cloud8"
        assert nodes[1]["power_state"] == "Running"

    def test_torque_utils_queue(self, torque_queue_stdout):
        nodes = torque_utils.parse_queue_output(torque_queue_stdout)
        assert len(nodes) == 2
        assert nodes[0]["queue_name"] == "gpu"
        assert nodes[1]["queue_type"] == "Execution"

    def test_torque_gpu_status(self, torque_gpu_status):
        gpus = torque_utils.parse_gpu(torque_gpu_status)
        assert len(gpus["gpu_list"]) == 2
        assert gpus["driver_ver"] == "450.51.05"

    def test_torque_node_status(self, torque_node_status):
        status = torque_utils.parse_node_status(torque_node_status)
        assert len(status) == 19
        assert status["opsys"] == "linux"
        assert status["nsessions"] == "0"

    def test_torque_queue_state(self, torque_queue_state):
        state = torque_utils.parse_queue_state(torque_queue_state)
        assert len(state) == 7
        assert state["Transit"] == 0

    def test_torque_node_properties(self, torque_node_properties):
        properties = torque_utils.parse_node_properties(torque_node_properties)
        assert len(properties) == 3
        assert properties[1] == "cpu"
