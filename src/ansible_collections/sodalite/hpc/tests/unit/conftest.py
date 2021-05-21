from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
import textwrap

slurm_job_str = """
    JobId=70 JobName=test
        UserId=user(2015) GroupId=user(2015) MCS_label=N/A
        Priority=0 Nice=0 Account=(null) QOS=(null)
        JobState={0} Reason=None Dependency=(null)
        Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
        RunTime=00:00:06 TimeLimit=UNLIMITED TimeMin=N/A
        SubmitTime=2021-05-06T08:46:46 EligibleTime=2021-05-06T08:46:46
        AccrueTime=2021-05-06T08:46:46
        StartTime=2021-05-06T08:46:47 EndTime=Unknown Deadline=N/A
        SuspendTime=2021-05-06T08:46:53 SecsPreSuspend=6 LastSchedEval=2021-05-06T08:46:47
        Partition=debug AllocNode:Sid=slurmserver:23044
        ReqNodeList=(null) ExcNodeList=(null)
        NodeList=wn1
        BatchHost=wn1
        NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
        TRES=cpu=1,node=1,billing=1
        Socks/Node=* NtasksPerN:B:S:C=1:0:*:* CoreSpec=*
        MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
        Features=(null) DelayBoot=00:00:00
        OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
        Command=/home/user/test.slurm
        WorkDir=/home/user
        StdErr=/home/user/slurm-70.out
        StdIn=/dev/null
        StdOut=/home/user/slurm-70.out
        Power=
        MailUser=user MailType=NONE
    """

torque_job_str = """
    Job Id: 2310.cloudserver
        Job_Name = hpc-test-1
        Job_Owner = user@cloudserver
        resources_used.cput = 00:00:00
        resources_used.vmem = 335048kb
        resources_used.walltime = 00:00:30
        resources_used.mem = 564kb
        resources_used.energy_used = 0
        job_state = {0}
        queue = batch
        server = cloudserver
        Checkpoint = u
        ctime = Thu May  6 17:06:44 2021
        Error_Path = cloudserver:/mnt/nfs/home/
        exec_host = node-1.novalocal/0-19
        Hold_Types = n
        Join_Path = n
        Keep_Files = n
        Mail_Points = abe
        Mail_Users = test@gmail.com
        mtime = Thu May  6 17:07:14 2021
        Output_Path = cloudserver:/mnt/nfs/home/
        Priority = 0
        qtime = Thu May  6 17:06:44 2021
        Rerunable = True
        Resource_List.nodes = 1:ppn=20
        Resource_List.walltime = 00:30:00
        Resource_List.epilogue = /mnt/nfs/home/
        Resource_List.nodect = 1
        session_id = 16944
        Shell_Path_List = /bin/sh
        Variable_List = PBS_O_QUEUE=batch,PBS_O_HOME=/mnt/nfs/home/,
            PBS_O_LOGNAME=user,
            PBS_O_PATH=/usr/local/bin:/usr/local/sbin:/opt/nfs/usr/local/Modules/
            bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/mnt/nfs/home/al
            exander/.local/bin:/mnt/nfs/home/user/bin,
            PBS_O_MAIL=/var/spool/mail/user,PBS_O_SHELL=/bin/bash,
            PBS_O_LANG=en_US.UTF-8,PBS_O_WORKDIR=/mnt/nfs/home/user,
            PBS_O_HOST=cloudserver,PBS_O_SERVER=cloudserver.novalocal
        euser = user
        egroup = user
        queue_type = E
        comment = Job started on Thu May 06 at 17:06
        etime = Thu May  6 17:06:44 2021
        exit_status = 0
        submit_args = hpc-test-1.pbs
        start_time = Thu May  6 17:06:44 2021
        start_count = 1
        fault_tolerant = False
        comp_time = Thu May  6 17:07:14 2021
        job_radix = 0
        total_runtime = 30.314982
        submit_host = cloudserver
        init_work_dir = /mnt/nfs/home/user
        request_version = 1
        req_information.task_count.0 = 1
        req_information.lprocs.0 = 20
        req_information.thread_usage_policy.0 = allowthreads
        req_information.hostlist.0 = node-1.novalocal:ppn=20
        req_information.task_usage.0.task.0.cpu_list = 0-19
        req_information.task_usage.0.task.0.mem_list = 0-1
        req_information.task_usage.0.task.0.cores = 0
        req_information.task_usage.0.task.0.threads = 20
        req_information.task_usage.0.task.0.host = node-1.novalocal
    """


@pytest.fixture
def torque_node_stdout_2():
    stdout = """
    cloud8
        state = free
        power_state = Running
        np = 40
        properties = batch,gpu
        ntype = cluster
        status = opsys=linux,uname=Linux cloud8,nsessions=0,nusers=0,idletime=12013265,totmem=135777452kb,availmem=123727248kb,physmem=131583152kb,ncpus=40
        mom_service_port = 15002
        mom_manager_port = 15003
        gpus = 1
        gpu_status = gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;
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
        status = opsys=linux,uname=Linux cloud8,nsessions=0,nusers=0,idletime=12013265,totmem=135777452kb,availmem=123727248kb,physmem=131583152kb,ncpus=40
        mom_service_port = 15002
        mom_manager_port = 15003
        gpus = 1
        gpu_status = gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;
        total_sockets = 2
        total_numa_nodes = 2
        total_cores = 20
        total_threads = 40
        dedicated_sockets = 0
        dedicated_numa_nodes = 0
        dedicated_cores = 0
        dedicated_threads = 0
        """
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_node_stdout_1():
    stdout = """
    cloud8
        state = free
        power_state = Running
        np = 40
        properties = batch,gpu
        ntype = cluster
        status = opsys=linux,uname=Linux cloud8,nsessions=0,nusers=0,idletime=12013265,totmem=135777452kb,availmem=123727248kb,physmem=131583152kb,ncpus=40
        mom_service_port = 15002
        mom_manager_port = 15003
        gpus = 1
        gpu_status = gpu[0]=gpu_id=00000000:03:00.0;gpu_pci_device_id=453382366;gpu_pci_location_id=00000000:03:00.0;gpu_product_name=GeForce GTX 1080 Ti;
        total_sockets = 2
        total_numa_nodes = 2
        total_cores = 20
        total_threads = 40
        dedicated_sockets = 0
        dedicated_numa_nodes = 0
        dedicated_cores = 0
        dedicated_threads = 0
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_job_stdout_2():
    stdout = """
    Job Id: 2310.cloudserver
        Job_Name = hpc-test-1
        Job_Owner = user@cloudserver
        resources_used.cput = 00:00:00
        resources_used.vmem = 335048kb
        resources_used.walltime = 00:00:30
        resources_used.mem = 564kb
        resources_used.energy_used = 0
        job_state = C
        queue = batch
        server = cloudserver
        Checkpoint = u
        ctime = Thu May  6 17:06:44 2021
        Error_Path = cloudserver:/mnt/nfs/home/
        exec_host = node-1.novalocal/0-19
        Hold_Types = n
        Join_Path = n
        Keep_Files = n
        Mail_Points = abe
        Mail_Users = test@gmail.com
        mtime = Thu May  6 17:07:14 2021
        Output_Path = cloudserver:/mnt/nfs/home/
        Priority = 0
        qtime = Thu May  6 17:06:44 2021
        Rerunable = True
        Resource_List.nodes = 1:ppn=20
        Resource_List.walltime = 00:30:00
        Resource_List.epilogue = /mnt/nfs/home/
        Resource_List.nodect = 1
        session_id = 16944
        Shell_Path_List = /bin/sh
        Variable_List = PBS_O_QUEUE=batch,PBS_O_HOME=/mnt/nfs/home/,
            PBS_O_LOGNAME=user,
            PBS_O_PATH=/usr/local/bin:/usr/local/sbin:/opt/nfs/usr/local/Modules/
            bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/mnt/nfs/home/al
            exander/.local/bin:/mnt/nfs/home/user/bin,
            PBS_O_MAIL=/var/spool/mail/user,PBS_O_SHELL=/bin/bash,
            PBS_O_LANG=en_US.UTF-8,PBS_O_WORKDIR=/mnt/nfs/home/user,
            PBS_O_HOST=cloudserver,PBS_O_SERVER=cloudserver.novalocal
        euser = user
        egroup = user
        queue_type = E
        comment = Job started on Thu May 06 at 17:06
        etime = Thu May  6 17:06:44 2021
        exit_status = 0
        submit_args = hpc-test-1.pbs
        start_time = Thu May  6 17:06:44 2021
        start_count = 1
        fault_tolerant = False
        comp_time = Thu May  6 17:07:14 2021
        job_radix = 0
        total_runtime = 30.314982
        submit_host = cloudserver
        init_work_dir = /mnt/nfs/home/user
        request_version = 1
        req_information.task_count.0 = 1
        req_information.lprocs.0 = 20
        req_information.thread_usage_policy.0 = allowthreads
        req_information.hostlist.0 = node-1.novalocal:ppn=20
        req_information.task_usage.0.task.0.cpu_list = 0-19
        req_information.task_usage.0.task.0.mem_list = 0-1
        req_information.task_usage.0.task.0.cores = 0
        req_information.task_usage.0.task.0.threads = 20
        req_information.task_usage.0.task.0.host = node-1.novalocal

    Job Id: 2311.cloudserver
        Job_Name = hpc-test-1
        Job_Owner = user@cloudserver
        resources_used.cput = 00:00:00
        resources_used.vmem = 355048kb
        resources_used.walltime = 00:00:30
        resources_used.mem = 564kb
        resources_used.energy_used = 0
        job_state = R
        queue = batch
        server = cloudserver
        Checkpoint = u
        ctime = Thu May  6 16:06:44 2021
        Error_Path = cloudserver:/mnt/nfs/home/
        exec_host = node-1.novalocal/0-19
        Hold_Types = n
        Join_Path = n
        Keep_Files = n
        Mail_Points = abe
        Mail_Users = test@gmail.com
        mtime = Thu May  6 17:07:14 2021
        Output_Path = cloudserver:/mnt/nfs/home/
        Priority = 0
        qtime = Thu May  6 18:06:44 2021
        Rerunable = True
        Resource_List.nodes = 1:ppn=20
        Resource_List.walltime = 00:30:00
        Resource_List.epilogue = /mnt/nfs/home/
        Resource_List.nodect = 1
        session_id = 16944
        Shell_Path_List = /bin/sh
        Variable_List = PBS_O_QUEUE=batch,PBS_O_HOME=/mnt/nfs/home/,
            PBS_O_LOGNAME=user,
            PBS_O_PATH=/usr/local/bin:/usr/local/sbin:/opt/nfs/usr/local/Modules/
            bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/mnt/nfs/home/al
            exander/.local/bin:/mnt/nfs/home/user/bin,
            PBS_O_MAIL=/var/spool/mail/user,PBS_O_SHELL=/bin/bash,
            PBS_O_LANG=en_US.UTF-8,PBS_O_WORKDIR=/mnt/nfs/home/user,
            PBS_O_HOST=cloudserver,PBS_O_SERVER=cloudserver.novalocal
        euser = user
        egroup = user
        queue_type = E
        comment = Job started on Thu May 06 at 17:06
        etime = Thu May  6 18:06:44 2021
        exit_status = 0
        submit_args = hpc-test-1.pbs
        start_time = Thu May  6 18:06:44 2021
        start_count = 1
        fault_tolerant = False
        comp_time = Thu May  6 18:07:14 2021
        job_radix = 0
        total_runtime = 30.314982
        submit_host = cloudserver
        init_work_dir = /mnt/nfs/home/user
        request_version = 1
        req_information.task_count.0 = 1
        req_information.lprocs.0 = 20
        req_information.thread_usage_policy.0 = allowthreads
        req_information.hostlist.0 = node-1.novalocal:ppn=20
        req_information.task_usage.0.task.0.cpu_list = 0-19
        req_information.task_usage.0.task.0.mem_list = 0-1
        req_information.task_usage.0.task.0.cores = 0
        req_information.task_usage.0.task.0.threads = 20
        req_information.task_usage.0.task.0.host = node-1.novalocal
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_queue_stdout_2():
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
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_queue_stdout_1():
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
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_node_stdout_2():
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
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_node_stdout_1():
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
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_partition_stdout_2():
    stdout = """
    PartitionName=debug
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=YES QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=0 LLN=NO MaxCPUsPerNode=UNLIMITED
        Nodes=wn[1-2]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=UP TotalCPUs=2 TotalNodes=2 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED

    PartitionName=test
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=YES QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=0 LLN=NO MaxCPUsPerNode=UNLIMITED
        Nodes=wn[1-2]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=UP TotalCPUs=2 TotalNodes=2 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_partition_stdout_1():
    stdout = """
    PartitionName=debug
        AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
        AllocNodes=ALL Default=YES QoS=N/A
        DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
        MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=0 LLN=NO MaxCPUsPerNode=UNLIMITED
        Nodes=wn[1-2]
        PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
        OverTimeLimit=NONE PreemptMode=OFF
        State=UP TotalCPUs=2 TotalNodes=2 SelectTypeParameters=NONE
        JobDefaults=(null)
        DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_job_stdout_3():
    stdout = """
    JobId=70 JobName=test
        UserId=user(2015) GroupId=user(2015) MCS_label=N/A
        Priority=0 Nice=0 Account=(null) QOS=(null)
        JobState=SUSPENDED Reason=None Dependency=(null)
        Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
        RunTime=00:00:06 TimeLimit=UNLIMITED TimeMin=N/A
        SubmitTime=2021-05-06T08:46:46 EligibleTime=2021-05-06T08:46:46
        AccrueTime=2021-05-06T08:46:46
        StartTime=2021-05-06T08:46:47 EndTime=Unknown Deadline=N/A
        SuspendTime=2021-05-06T08:46:53 SecsPreSuspend=6 LastSchedEval=2021-05-06T08:46:47
        Partition=debug AllocNode:Sid=slurmserver:23044
        ReqNodeList=(null) ExcNodeList=(null)
        NodeList=wn1
        BatchHost=wn1
        NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
        TRES=cpu=1,node=1,billing=1
        Socks/Node=* NtasksPerN:B:S:C=1:0:*:* CoreSpec=*
        MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
        Features=(null) DelayBoot=00:00:00
        OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
        Command=/home/user/test.slurm
        WorkDir=/home/user
        StdErr=/home/user/slurm-70.out
        StdIn=/dev/null
        StdOut=/home/user/slurm-70.out
        Power=
        MailUser=user MailType=NONE

    JobId=71 JobName=test
        UserId=user(2015) GroupId=user(2015) MCS_label=N/A
        Priority=0 Nice=0 Account=(null) QOS=(null)
        JobState=SUSPENDED Reason=None Dependency=(null)
        Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
        RunTime=00:00:07 TimeLimit=UNLIMITED TimeMin=N/A
        SubmitTime=2021-05-06T08:48:01 EligibleTime=2021-05-06T08:48:01
        AccrueTime=2021-05-06T08:48:01
        StartTime=2021-05-06T08:48:01 EndTime=Unknown Deadline=N/A
        SuspendTime=2021-05-06T08:48:08 SecsPreSuspend=7 LastSchedEval=2021-05-06T08:48:01
        Partition=debug AllocNode:Sid=slurmserver:24254
        ReqNodeList=(null) ExcNodeList=(null)
        NodeList=wn1
        BatchHost=wn1
        NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
        TRES=cpu=1,node=1,billing=1
        Socks/Node=* NtasksPerN:B:S:C=1:0:*:* CoreSpec=*
        MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
        Features=(null) DelayBoot=00:00:00
        OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
        Command=/home/user/test.slurm
        WorkDir=/home/user
        StdErr=/home/user/slurm-71.out
        StdIn=/dev/null
        StdOut=/home/user/slurm-71.out
        Power=
        MailUser=user MailType=NONE

    JobId=72 JobName=test
        UserId=user(2015) GroupId=user(2015) MCS_label=N/A
        Priority=0 Nice=0 Account=(null) QOS=(null)
        JobState=SUSPENDED Reason=None Dependency=(null)
        Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
        RunTime=00:00:06 TimeLimit=UNLIMITED TimeMin=N/A
        SubmitTime=2021-05-06T08:49:02 EligibleTime=2021-05-06T08:49:02
        AccrueTime=2021-05-06T08:49:02
        StartTime=2021-05-06T08:49:02 EndTime=Unknown Deadline=N/A
        SuspendTime=2021-05-06T08:49:08 SecsPreSuspend=6 LastSchedEval=2021-05-06T08:49:02
        Partition=debug AllocNode:Sid=slurmserver:25439
        ReqNodeList=(null) ExcNodeList=(null)
        NodeList=wn1
        BatchHost=wn1
        NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
        TRES=cpu=1,node=1,billing=1
        Socks/Node=* NtasksPerN:B:S:C=1:0:*:* CoreSpec=*
        MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
        Features=(null) DelayBoot=00:00:00
        OverSubscribe=NO Contiguous=0 Licenses=(null) Network=(null)
        Command=/home/user/test.slurm
        WorkDir=/home/user
        StdErr=/home/user/slurm-72.out
        StdIn=/dev/null
        StdOut=/home/user/slurm-72.out
        Power=
        MailUser=user MailType=NONE
    """
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_job_stdout_1_s():
    stdout = slurm_job_str.format("SUSPENDED")
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_job_stdout_1_r():
    stdout = slurm_job_str.format("RUNNING")
    return textwrap.dedent(stdout)


@pytest.fixture
def slurm_job_stdout_1_c():
    stdout = slurm_job_str.format("CANCELLED")
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_job_stdout_1_s():
    stdout = torque_job_str.format("H")
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_job_stdout_1_r():
    stdout = torque_job_str.format("R")
    return textwrap.dedent(stdout)


@pytest.fixture
def torque_job_stdout_1_c():
    stdout = torque_job_str.format("C")
    return textwrap.dedent(stdout)
