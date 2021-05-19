from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

regex_nodes = r"(?P<itemname>\S+)\n|((?P<name>\S+) = (?P<value>(.+\n?)))"
regex_status = r"(?P<name>[^,]+)=(?P<value>([^,]*))"
regex_gpu = (r"gpu\[(?P<gpu_num>\d+)\]=(?P<gpu_status>[^,]+)|"
             r"(?P<name>[^,]+)=(?P<value>([^,]*))")
regex_gpu_status = r"(?P<name>[^;]+)=(?P<value>([^;]*))"
regex_queue_state = r"(?P<state>\w+):(?P<value>\d+)"
regex_node_properties = r"(?P<name>[^,]+)"
regex_memory = r"(?P<number>\d+)\s*(?P<measure>kb|mb|)$"

regex_job_info = r"Job Id: (?P<itemname>\S+)\n|((?P<name>\S+)(?=\s=\s)(\s=\s)(?P<value>(.+\n?)))"
regex_var_list = r"(?P<item_name>[^,]+)=(?P<item_value>[^,]+),?"


def parse_node_output(stdout):
    node = {}
    result = []
    matches = re.finditer(regex_nodes, stdout, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if match.group("itemname") is not None:
            node = {}
            node["node_name"] = match.group("itemname")
            result.append(node)
        elif match.group("name") == "gpu_status":
            node[match.group("name")] = parse_gpu(
                match.group("value").strip())
        elif match.group("name") == "status":
            node[match.group("name")] = parse_node_status(
                match.group("value").strip())
        elif match.group("name") == "properties":
            node[match.group("name")] = parse_node_properties(
                match.group("value").strip())
        else:
            node[match.group("name")] = match.group("value").strip()

    return result


def parse_queue_output(stdout):
    node = {}
    result = []
    matches = re.finditer(regex_nodes, stdout, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if match.group("itemname") is not None:
            node = {}
            node["queue_name"] = match.group("itemname")
            result.append(node)
        elif match.group("name") == "state_count":
            node[match.group("name")] = parse_queue_state(
                match.group("value").rstrip()
            )
        else:
            node[match.group("name")] = match.group("value").strip()

    return result


def parse_queue_state(state_string):
    state = {}
    matches = re.finditer(regex_queue_state, state_string.strip())
    for matchNum, match in enumerate(matches, start=1):
        state[match.group("state")] = int(match.group("value").strip())

    return state


def parse_node_status(status_string):
    status = {}
    matches = re.finditer(regex_status, status_string.strip())
    for matchNum, match in enumerate(matches, start=1):
        status[match.group("name")] = parse_num_values(
            match.group("value").strip()
        )

    return status


def parse_node_properties(properties_string):
    properties = []
    matches = re.finditer(regex_node_properties, properties_string.strip())
    for matchNum, match in enumerate(matches, start=1):
        properties.append(match.group("name").strip())

    return properties


def parse_gpu(gpu_status_string):
    gpus = {}
    gpus["gpu_list"] = []

    matches = re.finditer(regex_gpu, gpu_status_string.strip())
    for matchNum, match in enumerate(matches, start=1):
        if match.group("gpu_num") is not None:
            gpu = {}
            gpu_matches = re.finditer(
                regex_gpu_status, match.group("gpu_status")
            )
            for gpuMatchNum, gpu_match in enumerate(gpu_matches, start=1):
                gpu[gpu_match.group("name")] = parse_num_values(
                    gpu_match.group("value").strip()
                )
            gpus["gpu_list"].append(gpu)
        elif match.group("name") is not None:
            gpus[match.group("name")] = match.group("value").strip()

    return gpus


def parse_num_values(memory_string):
    match = re.match(regex_memory, memory_string.strip(), re.IGNORECASE)
    if match is not None:
        if(
            match.group("measure") is None
            or match.group("measure").lower() == "mb"
        ):
            return int(match.group("number"))
        elif match.group("measure").lower() == "kb":
            return int(round(int(match.group("number")) / 1024))

    return memory_string


def parse_job_output(stdout):
    job = {}
    result = []
    normalized = re.sub("\n {8,}", "", stdout)
    matches = re.finditer(regex_job_info, normalized, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if match.group("itemname") is not None:
            job = {}
            job["job_id"] = match.group("itemname")
            result.append(job)
        else:
            var_matches = re.finditer(regex_var_list, match.group("value"), re.IGNORECASE)
            job[match.group("name")] = match.group("value").strip()

    return result


def parse_var_list(list_string):
    variables = {}
    matches = re.finditer(regex_var_list, list_string.strip())
    for matchNum, match in enumerate(matches, start=1):
        variables[match.group("item_name").strip()] = match.group("item_value").strip()

    return variables
