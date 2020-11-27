#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: os_security_group_info

short_description: This is my test module

version_added: "2.4"

description:
    - "This is my longer description explaining my test module"

options:
    name:
        description:
            - This is the message to send to the test module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_test:
    name: fail me
'''

RETURN = '''
openstack_security_group:
    description: has all the openstack information about the security group
    returned: always, but can be null
    type: complex
    contains:
        id:
            description: Unique UUID.
            returned: success
            type: str
        name:
            description: Name given to the security group.
            returned: success
            type: str
        description:
            description: Security group description.
            returned: success
            type: str
        location:
            description: Security group location.
            returned: success
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module, openstack_module_kwargs

def run_module():
    argument_spec = openstack_full_argument_spec(
        security_group=dict(required=False),
        properties=dict(default=None, type='dict'),
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        if module.params['security_group']:
            security_group = cloud.get_security_group(module.params['security_group'])
            module.exit_json(changed=False, openstack_security_group=security_group)
        else:
            security_groups = cloud.search_security_groups()
            module.exit_json(changed=False, openstack_security_group=security_groups)

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))

def main():
    run_module()

if __name__ == '__main__':
    main()