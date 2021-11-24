#
# (c) 2020 Red Hat Inc.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
filter: parse_show_run_interface
short_description: Parse interface information
description:
  - A plugin what parses information from interface structure and 
    return dictionary
author:
    - SK
version_added: 2.0.1
requirements:
    - re
"""


EXAMPLES = r"""
# lookup sample
- name: set connection info
  set_fact:
    connection_args:
        vcenter_hostname: "vcenter.test"
        vcenter_username: "administrator@vsphere.local"
        vcenter_password: "1234"
- name: lookup MoID of the object
  debug: msg="{{ lookup('vmware.vmware_rest.host_moid', '/my_dc/host/my_cluster/esxi1.test', **connection_args) }}"
- name: lookup MoID of the object inside the path
  debug: msg="{{ lookup('vmware.vmware_rest.host_moid', '/my_dc/host/my_cluster/') }}"
"""


import re
from copy import deepcopy


def _valid_regx_match(regex, string, key):
    if regex.search(string):
        return regex.search(string).groupdict()
    else:
        if isinstance(key, str):
            return {key: "N/A"}

        elif isinstance(key, list):
            _d = {}
            for k in key:
                _d[k] = "N/A"
            return _d


class FilterModule(object):
    def filters(self):
        return {
            "parse_show_run_interface": self.parse_show_run_interface
            # 'parse_show_subscriber_info': self.parse_show_subscriber_info,
            # 'parse_show_interface': self.parse_show_interface,
        }

    # @staticmethod
    # def parse_show_interface(show_interface_raw):
    #     input_rate_regex = re.compile(r'^.*input\s+rate\s+(?P<input_rate>\d+)',re.MULTILINE )
    #     output_rate_regex = re.compile(r'^.*output\s+rate\s+(?P<output_rate>\d+)',re.MULTILINE )
    #     interface_status_regex = re.compile(r'^(?P<port>\S+)\s+is\s+(?P<port_status>.+?),',re.MULTILINE )

    #     return {
    #             **_valid_regx_match(input_rate_regex,show_interface_raw,'input_rate'),
    #             **_valid_regx_match(output_rate_regex,show_interface_raw,'output_rate'),
    #             **_valid_regx_match(interface_status_regex,show_interface_raw,['port','port_status'])

    #     }

    @staticmethod
    def parse_show_run_interface(show_run_raw):
        """Parse show run interface and return nice data structure"""
        description_regex = re.compile(
            r"description\s+(?P<description>.*$)", re.MULTILINE
        )
        qos_policy_regex = re.compile(
            r"service-policy output\s+(?P<qos_policy>\S+)", re.MULTILINE
        )
        ip_addr_regex = re.compile(r"ipv4 unnumbered\s+(?P<ip_addr>\S+)", re.MULTILINE)
        ip_pool_regex = re.compile(
            r"service-policy\s+type\s+control\s+subscriber\s+(?P<ip_pool>\S+)",
            re.MULTILINE,
        )
        vlan_regex = re.compile(
            r"encapsulation\s+ambiguous\s+dot1q\s+(?P<s_vlan>\S+)\s+second-dot1q\s+(?P<c_vlan>\S+)",
            re.MULTILINE,
        )

        return {
            **_valid_regx_match(description_regex, show_run_raw, "description"),
            **_valid_regx_match(qos_policy_regex, show_run_raw, "qos_policy"),
            **_valid_regx_match(ip_addr_regex, show_run_raw, "ip_addr"),
            **_valid_regx_match(ip_pool_regex, show_run_raw, "ip_pool"),
            **_valid_regx_match(vlan_regex, show_run_raw, ["s_vlan", "c_vlan"]),
        }

    # @staticmethod
    # def parse_show_subscriber_info(show_subscriber_raw):
    #     state_regex = re.compile(r'Session Counts by State:.*?connected\s+\d+\s+(?P<ipoe_connected>\d+).*?activated\s+\d+\s+(?P<ipoe_activated>\d+).*?idle\s+\d+\s+(?P<ipoe_idle>\d+)',re.MULTILINE | re.DOTALL )
    #     session_regex = re.compile(r'Session\s+Counts\s+by\s+Address-Family\/LAC:.*?ipv4-only\s+\d+\s+(?P<ipoe_ipv4>\d+).*?ipv6-only\s+\d+\s+(?P<ipoe_ipv6>\d+).*?dual-up\s+\d+\s+(?P<ipoe_dual_stack>\d+)',re.MULTILINE | re.DOTALL)

    #     return {
    #             **_valid_regx_match(state_regex , show_subscriber_raw ,['ipoe_connected','ipoe_activated','ipoe_idle']),
    #             **_valid_regx_match(session_regex , show_subscriber_raw ,['ipoe_ipv4','ipoe_ipv6','ipoe_dual_stack'])

    #     }
