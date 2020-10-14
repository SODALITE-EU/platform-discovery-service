import re

regex_template = r"{0}=(?P<{0}>\S*)|(?P<name>\w*)=(?P<value>([^=^\[^\]]*\s|[\S]*\s))"


def parse_output(stdout, item_name):
    result = []
    regex = regex_template.format(item_name)
    node = {}
    matches = re.finditer(regex, stdout, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if match.group(item_name) is not None:
            node = {}
            node[item_name] = match.group(item_name)
            result.append(node)
        else:
            node[match.group("name")] = match.group("value").rstrip()

    return result

if __name__ == '__main__':
    output = """PartitionName=debug
   AllowGroups=ALL AllowAccounts=ALL AllowQos=ALL
   AllocNodes=ALL Default=YES QoS=N/A
   DefaultTime=NONE DisableRootJobs=NO ExclusiveUser=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=0 LLN=NO MaxCPUsPerNode=UNLIMITED
   Nodes=wn[1-4]
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=OFF
   State=UP TotalCPUs=4 TotalNodes=4 SelectTypeParameters=NONE
   JobDefaults=(null)
   DefMemPerNode=UNLIMITED MaxMemPerNode=UNLIMITED"""
    parse_output(output, "PartitionName")