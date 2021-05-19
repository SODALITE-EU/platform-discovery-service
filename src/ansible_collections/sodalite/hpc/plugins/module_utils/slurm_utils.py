from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

regex_template = (r"{0}=(?P<{0}>\S+)"
                  r"|(?P<name>\w+)=(?P<value>([^=^\[^\]]*\s|[\S]*\s))")
regex_gres = r"(?P<gpu>gpu):(?P<type>\w+)?:?(?P<number>\d+)"
regex_job = r"Submitted batch job (?P<number>\d+)"
regex_snake_case = r'(?<!^)(?=[A-Z])'


def parse_output(stdout, item_name):
    result = []
    regex = regex_template.format(item_name)
    node = {}
    matches = re.finditer(regex, stdout, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if match.group(item_name) is not None:
            node = {}
            node[to_snake_case(item_name)] = match.group(item_name)
            result.append(node)
        elif match.group("name") == "Gres":
            node[to_snake_case(match.group("name"))] = parse_gres(
                match.group("value").strip())
        else:
            node[to_snake_case(match.group("name"))] = match.group("value").rstrip()

    return result


def parse_gres(gres_string):
    gres = {}
    gres["total_gpu"] = 0
    gres["gpu"] = {}
    matches = re.finditer(regex_gres, gres_string)
    for matchNum, match in enumerate(matches, start=1):
        if match.group("gpu") is not None:
            gres["total_gpu"] += int(match.group("number"))
            if match.group("type") is not None:
                gres["gpu"][match.group("type")] = int(match.group("number"))

    return gres


def parse_job_output(job_string):
    match = re.match(regex_job, job_string.strip(), re.IGNORECASE)
    if match is not None:
        return (int(match.group("number")))

    return None


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
