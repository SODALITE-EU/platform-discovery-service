import re

regex_template = r"{0}=(?P<{0}>\S+)|(?P<name>\w+)=(?P<value>([^=^\[^\]]*\s|[\S]*\s))"


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
