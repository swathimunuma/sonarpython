# This is a pretty simple set of tests to verify that the ACM v20 template
# does what is expected from the equivalent spreadsheet

import jinja2
import ipaddress
import yaml
import json

from components.scriptgenerator.generic_solution.generic_deployer import generic_constants


def instance_exists(template, vm_instance_name):
    return vm_instance_name in template['vm_instances_specs']


@jinja2.contextfunction
def set_global(ctx, k, v):
    if v:
        ctx["global"][k] = v


class TestTemplates:

    def test_syntax(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR2'
        cust_num = 2
        cust_name = 'Robin'
        num_users = 500
        easg_enable = True
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'num_users': num_users, 'easg_enable': easg_enable}

        # Pre-test the template for valid syntax
        try:
            test_template = template.render(template_variables)
            assert True
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a syntax error in the template")
            assert False

    def test_invalid_parameter(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        datacenter_id = 'NAR2'
        cust_num = 'two'
        cust_name = 'Robin'
        num_users = 500
        easg_enable = True

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'num_users': num_users, 'easg_enable': easg_enable}

        # Run the template render
        try:
            test_template = template.render(template_variables)
            print("This should not pass due to a incorrect variable type")
            assert False
        except TypeError:
            # A failure is expected in this test
            assert True

    def test_dummy_parameters(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR2'
        cust_num = 2
        cust_name = 'Robin'
        num_users = 500
        easg_enable = True

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'num_users': num_users, 'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            template_dump = json.dumps(test_json)
            # Look for the string "dummy_" anywhere in the template output - any instance is a failure
            assert 'dummy_' not in template_dump

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the dummy parameters being replaced in the template")
            assert False

    def test_template_details(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        template_variables = {'template_details': True}

        # Check that the template accepts the special template_details argument
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            assert 'template_name' in test_json['template_specs']
            assert 'template_description' in test_json['template_specs']
            assert 'datacenter_id' in test_json['mandatory_parameters']
            assert 'cust_num' in test_json['mandatory_parameters']
            assert 'cust_name' in test_json['mandatory_parameters']
            assert 'cc_users' in test_json['mandatory_parameters']
            assert 'uc_users' in test_json['mandatory_parameters']
            assert 'primary' in test_json['optional_parameters']
            assert 'secondary' in test_json['optional_parameters']

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template details")
            assert False

    def test_no_env(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 3
        cust_name = 'Robin'
        cc_users = 500
        num_users = 500
        easg_enable = True
        custom_network = False
        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'num_users': num_users, 'easg_enable': easg_enable,
                              'custom_network': custom_network}

        # Check that the template operates correctly for no env parameter
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            assert test_json['vm_instances_specs']['win_instance_1']['ntp'] == '10.130.108.2'
            assert test_json['vm_instances_specs']['win_instance_1']['weblm'] == '10.130.108.10'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template details")
            assert False

    def test_AOC(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 3
        cust_name = 'Robin'
        cc_users = 500
        num_users = 500
        easg_enable = True
        custom_network = False
        env = 'AOC'
        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'num_users': num_users, 'easg_enable': easg_enable,
                              'custom_network': custom_network,
                              'env': env}

        # Check that the template operates correctly for an AOC env parameter
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            assert test_json['vm_instances_specs']['win_instance_1']['ntp'] == '100.66.1.2'
            assert test_json['vm_instances_specs']['win_instance_1']['weblm'] == '100.64.1.10'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template details")
            assert False

    def test_IBM(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        # Dummy Cluster and Datastore parameters to allow operation of the cluster macro
        env.globals["vdc"] = "DC1-ENG"
        env.globals["cluster_id"] = 1
        datacenter_id = 'NAR1'
        cust_num = 3
        cust_name = 'Robin'
        cc_users = 500
        num_users = 500
        easg_enable = True
        custom_network = False
        env = 'IBM'
        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'num_users': num_users, 'easg_enable': easg_enable,
                              'custom_network': custom_network,
                              'env': env}

        # Check that the template operates correctly for an IBM env parameter
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            assert test_json['vm_instances_specs']['win_instance_1']['ntp'] == '100.67.96.2'
            assert test_json['vm_instances_specs']['win_instance_1']['weblm'] == '100.67.96.10'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template details")
            assert False

    def test_42DC(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 3
        cust_name = 'Robin'
        cc_users = 500
        num_users = 500
        easg_enable = True
        # Attempt to override NAR1 from a dc_id of 1 to a dc_id of 8
        dc2_id = {'NAR1': 8, 'NAR2': 9, 'EMEA1': 17, 'EMEA2': 25, 'APAC1': 33, 'APAC2': 41, 'CALA1': 49, 'CALA2': 57}
        custom_network = False
        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'num_users': num_users, 'easg_enable': easg_enable,
                              'custom_network': custom_network,
                              'dc2id': dc2_id}

        # This test is designed to run the template with the 42 DC dc2id feature enabled

        # Check that the template accepts the special template_details argument
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # Check CM Instance 1 has Custom Network parameters
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_1'] == '100.71.10.21'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_2'] == '192.168.52.9'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_address'] == '100.71.10.11'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['hostname'] == 'Robin3dc8cccm1a'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_hostname'] == 'Robin3dc8cccm1v'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['template_size'] == 'DuplexStd'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['default_gateway'] == '100.71.10.1'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['VLAN_ID'] == 1032
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC08_CUST_003_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC08_CUST_003_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group_name'] == 'Duplication Link'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group'] == 'DC08_CUST_003_CM_DUPL'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'NAR1_customer_003'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the 42DC feature")
            assert False

    def test_custom_network(self):
        # Preset the VM options
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader, extensions=["jinja2.ext.do"])
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 3
        cust_name = 'Robin'
        cc_users = 500
        num_users = 500
        easg_enable = True
        custom_network = True
        NAR1_apps_subnet = {'type': 'apps', 'gw': '10.136.116.1', 'vlan': 1000, 'port_grp': 'APPS_LAN', 'prefix': '24'}
        NAR1_oobm_subnet = {'type': 'oobm', 'gw': '10.136.116.1', 'vlan': 1000, 'port_grp': 'OOBM_LAN', 'prefix': '24'}
        NAR1_cm_dup_subnet = {'type': 'cm_dup', 'gw': '192.168.51.1', 'vlan': 1001, 'port_grp': 'CM_DUPL_LAN',
                              'prefix': '24'}
        subnets = {'NAR1': [NAR1_apps_subnet, NAR1_oobm_subnet, NAR1_cm_dup_subnet]}
        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'num_users': num_users, 'easg_enable': easg_enable,
                              'custom_network': custom_network,
                              'subnets': subnets}
        # This test is designed to run the template with the Custom Network feature enabled
        # Check that the template accepts the special template_details argument
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # Check CM Instance 1 has Custom Network parameters
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_1'] == '10.136.116.21'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_2'] == '192.168.52.9'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_address'] == '10.136.116.11'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['hostname'] == 'Robin3dc1cccm1a'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_hostname'] == 'Robin3dc1cccm1v'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['template_size'] == 'DuplexStd'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['default_gateway'] == '10.136.116.1'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['VLAN_ID'] == 1000
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['VLAN_ID_2'] == 1001
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'APPS_LAN'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'OOBM_LAN'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group_name'] == 'Duplication Link'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group'] == 'CM_DUPL_LAN'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'NAR1_customer_003'
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the Custom Network feature")
            assert False

    def test_primary_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR2'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # It should generate:
            # 2 AADS, 2 AAMs, 2 AAWGs, 2 AAWG_MSs,
            # 2 AES, 1 AMS, 2 Breeze/PS, 2 CMs, 1 CMS,
            # 2 AADS, 2 AAMs, 2 AES, 1 AMS, 2 Breeze/PS, 2 CMs, 1 CMS,
            # 2 EQCONFAPPs and 1 EQCONFMED
            # 3 IXMs
            # 1 Preconfig
            # 1 SAL, 1 SBC EMS,
            # 2 SBC RW, 2 SBC Trunk, 2 SM, 1 SMGR, and 1 Windows AD on the Primary
            # AAWG is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +4
            # Equinox is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +3
            assert len(test_json['vm_instances_specs']) == 26

            assert True
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a syntax error in the template")
            assert False

    def test_secondary_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # It should generate:
            # 2 AADS, 2 AAMs, 2 AAWGs, 2 AAWG_MSs,
            # 2 AES, 1 AMS. 2 Breeze/PS, 1 CMS, 1 ESS,
            # 2 AADS, 2 AAMs, 2 AES, 1 AMS. 2 Breeze/PS, 1 CMS, 1 ESS,
            # 1 EQCONFAPPs and 1 EQCONFMED
            # 3 IXMs
            # 1 Preconfig
            # 1 SAL, 1 SBC EMS,
            # 2 SBC RW, 2 SBC Trunk, 2 SM, 1 SMGR, and 1 Windows AD on the Secondary
            # AAWG is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +4
            # Equinox is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +3
            assert len(test_json['vm_instances_specs']) == 25

            assert True
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a syntax error in the template")
            assert False

    def test_primary_huge(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR2'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 32000
        uc_users = 0
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template with the largest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # It should generate:
            # 2 AADSs, 5 AAMs, 3 AAWGs, 7 AAWG_MSs,
            # 16 AESs, 10 AMSs, 3 Breeze, 16 CMs, 8 CMSs,
            # 2 AADSs, 5 AAMs, 16 AESs, 10 AMSs, 3 Breeze, 16 CMs, 8 CMSs,
            # 2 EQCONFAPPs and 16 EQCONFMEDs
            # 7 IXMs
            # 1 Preconfig
            # 1 SAL, 1 SBC EMS,
            # 16 SBC RW, 16 SBC Trunk, 2 SMs, 1 SMGR, and 1 Windows AD on the Primary
            # AAWG is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +10
            # Equinox is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +18
            assert len(test_json['vm_instances_specs']) == 106

            assert True
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a syntax error in the template")
            assert False

    def test_secondary_huge(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'NAR1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 32000
        uc_users = 0
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template with the largest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # It should generate:
            # 2 AADSs, 3 AAWGs, 7 AAWG_MSs,
            # 5 AAMs, 16 AESs, 10 AMSs, 3 Breeze/PS, 8 CMSs, 8 ESSs,
            # 2 AADSs, 5 AAMs, 16 AESs, 10 AMSs, 3 Breeze/PS, 8 CMSs, 8 ESSs,
            # 1 EQCONFAPPs and 16 EQCONFMEDs
            # 7 IXMs
            # 1 Preconfig
            # 1 SAL, SBC EMS,
            # 16 SBC RW, 16 SBC Trunk, 2 SMs, 1 SMGR, and 1 Windows AD on the Primary
            # AAWG is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +10
            # Equinox is currently disabled so the following update has been commented out
            # assert len(test_json['vm_instances_specs']) == +17
            assert len(test_json['vm_instances_specs']) == 98

            assert True
        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a syntax error in the template")
            assert False

    def test_full_primary_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA2'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = True
        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)
            # Check CM Instance 1
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_1'] == '100.88.6.21'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['ip_address_2'] == '192.168.52.5'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_address'] == '100.88.6.11'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['hostname'] == 'Robin2dc25cccm1a'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['virtual_ip_hostname'] == 'Robin2dc25cccm1v'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['template_size'] == 'DuplexStd'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group_name'] == 'Duplication Link'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group'] == 'DC25_CUST_002_CM_DUPL'
            assert test_json['vm_instances_specs']['cm_duplex_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check CM Instance 2
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['ip_address_1'] == '100.88.6.31'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['ip_address_2'] == '192.168.52.6'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['virtual_ip_address'] == '100.88.6.11'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['hostname'] == 'Robin2dc25cccm1b'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['virtual_ip_hostname'] == 'Robin2dc25cccm1v'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['template_size'] == 'DuplexStd'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group_name'] == 'Duplication Link'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs']['virtual_network'][2][
                       'virtual_port_group'] == 'DC25_CUST_002_CM_DUPL'
            assert test_json['vm_instances_specs']['cm_duplex_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SMGR Instance 1
            assert test_json['vm_instances_specs']['smgr_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['smgr_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['smgr_instance_1']['ip_address_1'] == '100.88.6.60'
            assert test_json['vm_instances_specs']['smgr_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['smgr_instance_1']['hostname'] == 'Robin2dc25smgrpri'
            assert test_json['vm_instances_specs']['smgr_instance_1']['template_size'] == '250Kuser'
            assert test_json['vm_instances_specs']['smgr_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['smgr_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check Windows Instance 1
            assert test_json['vm_instances_specs']['win_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['win_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['win_instance_1']['ip_address_1'] == '100.88.6.90'
            assert test_json['vm_instances_specs']['win_instance_1']['prefix'] == 24
            assert test_json['vm_instances_specs']['win_instance_1']['hostname'] == 'Robin2dc25dp'
            assert test_json['vm_instances_specs']['win_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['win_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check CMS Instance 1
            assert test_json['vm_instances_specs']['cms_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cms_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cms_instance_1']['ip_address_1'] == '100.88.6.151'
            assert test_json['vm_instances_specs']['cms_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cms_instance_1']['hostname'] == 'Robin2dc25cccmspri1'
            assert test_json['vm_instances_specs']['cms_instance_1']['template_size'] == 'profile2'
            assert test_json['vm_instances_specs']['cms_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['cms_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['cms_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == '10.129.183 Subnet'
            assert test_json['vm_instances_specs']['cms_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check AMS Instance 1
            assert test_json['vm_instances_specs']['ams_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['ams_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['ams_instance_1']['ip_address_1'] == '100.88.7.158'
            assert test_json['vm_instances_specs']['ams_instance_1']['netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['ams_instance_1']['hostname'] == 'Robin2dc25ams1'
            assert test_json['vm_instances_specs']['ams_instance_1']['template_size'] == 'profile6'
            assert test_json['vm_instances_specs']['ams_instance_1']['default_gateway'] == '100.88.7.129'
            assert test_json['vm_instances_specs']['ams_instance_1']['VLAN_ID'] == 1023
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'AMS_Public'
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_AMS'
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check Session Manager Instance 1
            assert test_json['vm_instances_specs']['sm_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sm_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sm_instance_1']['ip_address_1'] == '100.88.6.61'
            assert test_json['vm_instances_specs']['sm_instance_1']['ip_address_2'] == '100.88.6.62'
            assert test_json['vm_instances_specs']['sm_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['sm_instance_1']['hostname'] == 'Robin2dc25sm1'
            assert test_json['vm_instances_specs']['sm_instance_1']['template_size'] == '23300devices'
            assert test_json['vm_instances_specs']['sm_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['sm_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check Session Manager Instance 2
            assert test_json['vm_instances_specs']['sm_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sm_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sm_instance_2']['ip_address_1'] == '100.88.6.63'
            assert test_json['vm_instances_specs']['sm_instance_2']['ip_address_2'] == '100.88.6.64'
            assert test_json['vm_instances_specs']['sm_instance_2']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['sm_instance_2']['hostname'] == 'Robin2dc25sm2'
            assert test_json['vm_instances_specs']['sm_instance_2']['template_size'] == '23300devices'
            assert test_json['vm_instances_specs']['sm_instance_2']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['sm_instance_2']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SBC EMS Instance 1
            assert test_json['vm_instances_specs']['sbcems_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['ip_address_1'] == '100.88.7.10'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['hostname'] == 'Robin2dc25emspri'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['template_size'] == 'ems'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['m1_gateway'] == '100.88.7.1'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SBC RW Instance 1
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['ip_address_1'] == '100.88.7.11'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['hostname'] == 'Robin2dc25sbcrw1a'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['m1_gateway'] == '100.88.7.1'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SBC RW Instance 2
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['ip_address_1'] == '100.88.7.21'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['hostname'] == 'Robin2dc25sbcrw1b'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['m1_gateway'] == '100.88.7.1'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SBC Trunk Instance 1
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['ip_address_1'] == '100.88.7.81'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['hostname'] == 'Robin2dc25sbctg1a'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['m1_gateway'] == '100.88.7.1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check SBC Trunk Instance 2
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['ip_address_1'] == '100.88.7.91'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['hostname'] == 'Robin2dc25sbctg1b'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['m1_gateway'] == '100.88.7.1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check AES Pair Instance 1A
            assert test_json['vm_instances_specs']['aes_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['aes_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['aes_instance_1']['ip_address_1'] == '100.88.6.161'
            assert test_json['vm_instances_specs']['aes_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['aes_instance_1']['hostname'] == 'Robin2dc25aes1a'
            assert test_json['vm_instances_specs']['aes_instance_1']['template_size'] == 'aesFootprint-profile3'
            assert test_json['vm_instances_specs']['aes_instance_1']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['aes_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['aes_instance_1']['virtual_ip_address'] == '100.88.6.51'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # Check AES Pair Instance 1b
            assert test_json['vm_instances_specs']['aes_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['aes_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['aes_instance_2']['ip_address_1'] == '100.88.6.171'
            assert test_json['vm_instances_specs']['aes_instance_2']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['aes_instance_2']['hostname'] == 'Robin2dc25aes1b'
            assert test_json['vm_instances_specs']['aes_instance_2']['template_size'] == 'aesFootprint-profile3'
            assert test_json['vm_instances_specs']['aes_instance_2']['default_gateway'] == '100.88.6.1'
            assert test_json['vm_instances_specs']['aes_instance_2']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['aes_instance_2']['virtual_ip_address'] == '100.88.6.51'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC25_CUST_002_APPS'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA2_customer_002'

            # # Check Equinox Application Server Instance 1
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['ip_address_1'] == '100.88.6.130'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['netmask'] == '255.255.255.0'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['hostname'] == 'Robin2dc25eqmgtg1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['template_size'] == 'medium_high'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['default_gateway'] == '100.88.6.1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['VLAN_ID'] == 1022
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC25_CUST_002_APPS'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA2_customer_002'

            # # Check Equinox Application Server Instance 2
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['ip_address_1'] == '100.88.6.131'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['netmask'] == '255.255.255.0'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['hostname'] == 'Robin2dc25eqmgtl1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['template_size'] == 'medium_high'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['default_gateway'] == '100.88.6.1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['VLAN_ID'] == 1022
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC25_CUST_002_APPS'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_2']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA2_customer_002'

            # # Check Equinox Media Server Instance 1
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['ip_address_1'] == '100.88.7.131'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['netmask'] == '255.255.255.128'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['hostname'] == 'Robin2dc25eqms1'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['template_size'] == 'ultra_high'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['default_gateway'] == '100.88.7.129'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['VLAN_ID'] == 1023
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC25_CUST_002_AMS'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA2_customer_002'

            # # Check Equinox Media Server Instance 2
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['ip_address_1'] == '100.88.7.132'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['netmask'] == '255.255.255.128'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['hostname'] == 'Robin2dc25eqms2'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['template_size'] == 'ultra_high'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['default_gateway'] == '100.88.7.129'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['VLAN_ID'] == 1023
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC25_CUST_002_AMS'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA2_customer_002'

            # # Check Breeze Instance 1
            # assert test_json['vm_instances_specs']['brz_instance_1']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['brz_instance_1']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['brz_instance_1']['ip_address_1'] == '100.88.6.100'
            # assert test_json['vm_instances_specs']['brz_instance_1']['ip_address_2'] == '100.88.6.101'
            # assert test_json['vm_instances_specs']['brz_instance_1']['netmask'] == '255.255.255.0'
            # assert test_json['vm_instances_specs']['brz_instance_1']['hostname'] == 'Robin2dc25eqbrz1'
            # assert test_json['vm_instances_specs']['brz_instance_1']['template_size'] == 'GPLargeCluster'
            # assert test_json['vm_instances_specs']['brz_instance_1']['default_gateway'] == '100.88.6.1'
            # assert test_json['vm_instances_specs']['brz_instance_1']['VLAN_ID'] == 1022
            # assert test_json['vm_instances_specs']['brz_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['brz_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC25_CUST_002_APPS'
            # assert test_json['vm_instances_specs']['brz_instance_1']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA2_customer_002'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_full_secondary_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = False
        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            # Check ESS Instance 1
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['ip_address_1'] == '100.80.6.11'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['hostname'] == 'Robin2dc17ccess1'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['template_size'] == 'Large'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['cm_ess_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SMGR Instance 1
            assert test_json['vm_instances_specs']['smgr_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['smgr_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['smgr_instance_1']['ip_address_1'] == '100.80.6.60'
            assert test_json['vm_instances_specs']['smgr_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['smgr_instance_1']['hostname'] == 'Robin2dc17smgrgeo'
            assert test_json['vm_instances_specs']['smgr_instance_1']['template_size'] == '250Kuser'
            assert test_json['vm_instances_specs']['smgr_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['smgr_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['smgr_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check Windows Instance 1
            assert test_json['vm_instances_specs']['win_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['win_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['win_instance_1']['ip_address_1'] == '100.80.6.90'
            assert test_json['vm_instances_specs']['win_instance_1']['prefix'] == 24
            assert test_json['vm_instances_specs']['win_instance_1']['hostname'] == 'Robin2dc17ds'
            assert test_json['vm_instances_specs']['win_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['win_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check CMS Instance 1
            assert test_json['vm_instances_specs']['cms_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['cms_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['cms_instance_1']['ip_address_1'] == '100.80.6.151'
            assert test_json['vm_instances_specs']['cms_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['cms_instance_1']['hostname'] == 'Robin2dc17cccmssec1'
            assert test_json['vm_instances_specs']['cms_instance_1']['template_size'] == 'profile2'
            assert test_json['vm_instances_specs']['cms_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['cms_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['cms_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == '10.129.183 Subnet'
            assert test_json['vm_instances_specs']['cms_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['win_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check AMS Instance 1
            assert test_json['vm_instances_specs']['ams_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['ams_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['ams_instance_1']['ip_address_1'] == '100.80.7.158'
            assert test_json['vm_instances_specs']['ams_instance_1']['netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['ams_instance_1']['hostname'] == 'Robin2dc17ams1'
            assert test_json['vm_instances_specs']['ams_instance_1']['template_size'] == 'profile6'
            assert test_json['vm_instances_specs']['ams_instance_1']['default_gateway'] == '100.80.7.129'
            assert test_json['vm_instances_specs']['ams_instance_1']['VLAN_ID'] == 1023
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'AMS_Public'
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_AMS'
            assert test_json['vm_instances_specs']['ams_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check Session Manager Instance 1
            assert test_json['vm_instances_specs']['sm_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sm_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sm_instance_1']['ip_address_1'] == '100.80.6.61'
            assert test_json['vm_instances_specs']['sm_instance_1']['ip_address_2'] == '100.80.6.62'
            assert test_json['vm_instances_specs']['sm_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['sm_instance_1']['hostname'] == 'Robin2dc17sm1'
            assert test_json['vm_instances_specs']['sm_instance_1']['template_size'] == '23300devices'
            assert test_json['vm_instances_specs']['sm_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['sm_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check Session Manager Instance 2
            assert test_json['vm_instances_specs']['sm_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sm_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sm_instance_2']['ip_address_1'] == '100.80.6.63'
            assert test_json['vm_instances_specs']['sm_instance_2']['ip_address_2'] == '100.80.6.64'
            assert test_json['vm_instances_specs']['sm_instance_2']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['sm_instance_2']['hostname'] == 'Robin2dc17sm2'
            assert test_json['vm_instances_specs']['sm_instance_2']['template_size'] == '23300devices'
            assert test_json['vm_instances_specs']['sm_instance_2']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['sm_instance_2']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group_name'] == 'Out of Band Management'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs']['virtual_network'][1][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['sm_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SBC EMS Instance 1
            assert test_json['vm_instances_specs']['sbcems_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['ip_address_1'] == '100.80.7.10'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['hostname'] == 'Robin2dc17emssec'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['template_size'] == 'ems'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['m1_gateway'] == '100.80.7.1'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcems_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SBC RW Instance 1
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['ip_address_1'] == '100.80.7.11'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['hostname'] == 'Robin2dc17sbcrw1a'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['m1_gateway'] == '100.80.7.1'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcrw_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SBC RW Instance 2
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['ip_address_1'] == '100.80.7.21'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['hostname'] == 'Robin2dc17sbcrw1b'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['m1_gateway'] == '100.80.7.1'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbcrw_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SBC Trunk Instance 1
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['ip_address_1'] == '100.80.7.81'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['hostname'] == 'Robin2dc17sbctg1a'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['m1_gateway'] == '100.80.7.1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbctrunking_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check SBC Trunk Instance 2
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['ip_address_1'] == '100.80.7.91'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['m1_netmask'] == '255.255.255.128'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['hostname'] == 'Robin2dc17sbctg1b'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['template_size'] == 'sbc'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['m1_gateway'] == '100.80.7.1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['VLAN_ID'] == 1029
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'M1'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_SBC_MGMT'
            assert test_json['vm_instances_specs']['sbctrunking_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check AES Pair Instance 1A
            assert test_json['vm_instances_specs']['aes_instance_1']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['aes_instance_1']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['aes_instance_1']['ip_address_1'] == '100.80.6.161'
            assert test_json['vm_instances_specs']['aes_instance_1']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['aes_instance_1']['hostname'] == 'Robin2dc17aes1a'
            assert test_json['vm_instances_specs']['aes_instance_1']['template_size'] == 'aesFootprint-profile3'
            assert test_json['vm_instances_specs']['aes_instance_1']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['aes_instance_1']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['aes_instance_1']['virtual_ip_address'] == '100.80.6.51'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['aes_instance_1']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # Check AES Pair Instance 1b
            assert test_json['vm_instances_specs']['aes_instance_2']['platform'] == 'VMWARE'
            assert test_json['vm_instances_specs']['aes_instance_2']['deployment_type'] == 'OVA'
            assert test_json['vm_instances_specs']['aes_instance_2']['ip_address_1'] == '100.80.6.171'
            assert test_json['vm_instances_specs']['aes_instance_2']['netmask'] == '255.255.255.0'
            assert test_json['vm_instances_specs']['aes_instance_2']['hostname'] == 'Robin2dc17aes1b'
            assert test_json['vm_instances_specs']['aes_instance_2']['template_size'] == 'aesFootprint-profile3'
            assert test_json['vm_instances_specs']['aes_instance_2']['default_gateway'] == '100.80.6.1'
            assert test_json['vm_instances_specs']['aes_instance_2']['VLAN_ID'] == 1022
            assert test_json['vm_instances_specs']['aes_instance_2']['virtual_ip_address'] == '100.80.6.51'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group_name'] == 'Public'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs']['virtual_network'][0][
                       'virtual_port_group'] == 'DC17_CUST_002_APPS'
            assert test_json['vm_instances_specs']['aes_instance_2']['vmware_env_specs'][
                       'vm_folder_name'] == 'EMEA1_customer_002'

            # # Check Equinox Application Server Instance 1
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['ip_address_1'] == '100.80.6.130'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['netmask'] == '255.255.255.0'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['hostname'] == 'Robin2dc17eqmgtg1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['template_size'] == 'medium_high'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['default_gateway'] == '100.80.6.1'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['VLAN_ID'] == 1022
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC17_CUST_002_APPS'
            # assert test_json['vm_instances_specs']['eqconfapps_instance_1']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA1_customer_002'

            # # Check Equinox Media Server Instance 1
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['ip_address_1'] == '100.80.7.131'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['netmask'] == '255.255.255.128'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['hostname'] == 'Robin2dc17eqms1'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['template_size'] == 'ultra_high'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['default_gateway'] == '100.80.7.129'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['VLAN_ID'] == 1023
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC17_CUST_002_AMS'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_1']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA1_customer_002'

            # # Check Equinox Media Server Instance 2
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['platform'] == 'VMWARE'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['deployment_type'] == 'OVA'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['ip_address_1'] == '100.80.7.132'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['netmask'] == '255.255.255.128'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['hostname'] == 'Robin2dc17eqms2'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['template_size'] == 'ultra_high'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['default_gateway'] == '100.80.7.129'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['VLAN_ID'] == 1023
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group_name'] == 'Public'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs']['virtual_network'][0][
            #            'virtual_port_group'] == 'DC17_CUST_002_AMS'
            # assert test_json['vm_instances_specs']['eqconfmeds_instance_2']['vmware_env_specs'][
            #            'vm_folder_name'] == 'EMEA1_customer_002'

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_uc_only_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 0
        uc_users = 500
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'ams_instance_1',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            unexpected_instances = ['cms_instance_1', 'aes_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {}\n, expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

            for instance in unexpected_instances:
                assert not instance_exists(test_json, instance), "Unexpected {} exists".format(instance)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_uc_only_large(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 0
        uc_users = 32000
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3', 'aawg_ms_instance_1',
                                  # 'aawg_ms_instance_2', 'aawg_ms_instance_3', 'aawg_ms_instance_4',
                                  # 'aawg_ms_instance_5', 'aawg_ms_instance_6', 'aawg_ms_instance_7',
                                  'aam_instance_1', 'aam_instance_2', 'aam_instance_3', 'aam_instance_4',
                                  'aam_instance_5',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3', 'ams_instance_4',
                                  'ams_instance_5', 'ams_instance_6', 'ams_instance_7', 'ams_instance_8',
                                  'ams_instance_9', 'ams_instance_10',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2', 'cm_duplex_instance_3',
                                  'cm_duplex_instance_4',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  # 'eqconfmeds_instance_5', 'eqconfmeds_instance_6', 'eqconfmeds_instance_7',
                                  # 'eqconfmeds_instance_8', 'eqconfmeds_instance_9', 'eqconfmeds_instance_10',
                                  # 'eqconfmeds_instance_11', 'eqconfmeds_instance_12', 'eqconfmeds_instance_13',
                                  # 'eqconfmeds_instance_14', 'eqconfmeds_instance_15', 'eqconfmeds_instance_16',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3', 'ixm_instance_4',
                                  'ixm_instance_5', 'ixm_instance_6', 'ixm_instance_7',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2', 'ps_instance_3',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbcrw_instance_5',
                                  'sbcrw_instance_6', 'sbcrw_instance_7', 'sbcrw_instance_8', 'sbcrw_instance_9',
                                  'sbcrw_instance_10', 'sbcrw_instance_11', 'sbcrw_instance_12', 'sbcrw_instance_13',
                                  'sbcrw_instance_14', 'sbcrw_instance_15', 'sbcrw_instance_16',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            unexpected_instances = ['cms_instance_1', 'aes_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

            for instance in unexpected_instances:
                assert not instance_exists(test_json, instance), "Unexpected {} exists".format(instance)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_secondary_uc_only_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 0
        uc_users = 500
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1',
                                  'ams_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'cm_ess_instance_1',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfmeds_instance_1',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_1',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            unexpected_instances = ['cms_instance_1', 'aes_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

            for instance in unexpected_instances:
                assert not instance_exists(test_json, instance), "Unexpected {} exists".format(instance)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_secondary_uc_only_large(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 0
        uc_users = 32000
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2', 'aam_instance_3', 'aam_instance_4',
                                  'aam_instance_5',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3', 'aawg_ms_instance_1',
                                  # 'aawg_ms_instance_2', 'aawg_ms_instance_3', 'aawg_ms_instance_4',
                                  # 'aawg_ms_instance_5', 'aawg_ms_instance_6', 'aawg_ms_instance_7',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3', 'ams_instance_4',
                                  'ams_instance_5', 'ams_instance_6', 'ams_instance_7', 'ams_instance_8',
                                  'ams_instance_9', 'ams_instance_10',
                                  'cm_ess_instance_1', 'cm_ess_instance_2',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  # 'eqconfmeds_instance_5', 'eqconfmeds_instance_6', 'eqconfmeds_instance_7',
                                  # 'eqconfmeds_instance_8', 'eqconfmeds_instance_9', 'eqconfmeds_instance_10',
                                  # 'eqconfmeds_instance_11', 'eqconfmeds_instance_12', 'eqconfmeds_instance_13',
                                  # 'eqconfmeds_instance_14', 'eqconfmeds_instance_15', 'eqconfmeds_instance_16',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3', 'ixm_instance_4',
                                  'ixm_instance_5', 'ixm_instance_6', 'ixm_instance_7',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2', 'ps_instance_3',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbcrw_instance_5', 'sbcrw_instance_6', 'sbcrw_instance_7', 'sbcrw_instance_8',
                                  'sbcrw_instance_9', 'sbcrw_instance_10', 'sbcrw_instance_11', 'sbcrw_instance_12',
                                  'sbcrw_instance_13', 'sbcrw_instance_14', 'sbcrw_instance_15', 'sbcrw_instance_16',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            unexpected_instances = ['cms_instance_1', 'aes_instance_1', 'cm_duplex_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

            for instance in unexpected_instances:
                assert not instance_exists(test_json, instance), "Unexpected {} exists".format(instance)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_cc_only_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'aes_instance_1', 'aes_instance_2',
                                  'ams_instance_1',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2',
                                  'cms_instance_1',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {}\n, expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_cc_only_large(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 32000
        us_users = 0
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'us_users': us_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_2', 'aam_instance_2', 'aam_instance_3', 'aam_instance_4',
                                  'aam_instance_5',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3', 'aawg_ms_instance_1',
                                  # 'aawg_ms_instance_2', 'aawg_ms_instance_3', 'aawg_ms_instance_4',
                                  # 'aawg_ms_instance_5', 'aawg_ms_instance_6', 'aawg_ms_instance_7',
                                  'aes_instance_1', 'aes_instance_2', 'aes_instance_3', 'aes_instance_4',
                                  'aes_instance_5', 'aes_instance_6', 'aes_instance_7', 'aes_instance_8',
                                  'aes_instance_9', 'aes_instance_10', 'aes_instance_11', 'aes_instance_12',
                                  'aes_instance_13', 'aes_instance_14', 'aes_instance_15', 'aes_instance_16',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3', 'ams_instance_4',
                                  'ams_instance_5', 'ams_instance_6', 'ams_instance_7', 'ams_instance_8',
                                  'ams_instance_9', 'ams_instance_10',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2', 'cm_duplex_instance_3',
                                  'cm_duplex_instance_4', 'cm_duplex_instance_5', 'cm_duplex_instance_6',
                                  'cm_duplex_instance_7', 'cm_duplex_instance_8', 'cm_duplex_instance_9',
                                  'cm_duplex_instance_10', 'cm_duplex_instance_11', 'cm_duplex_instance_12',
                                  'cm_duplex_instance_13', 'cm_duplex_instance_14', 'cm_duplex_instance_15',
                                  'cm_duplex_instance_16',
                                  'cms_instance_1', 'cms_instance_2', 'cms_instance_3', 'cms_instance_4',
                                  'cms_instance_5', 'cms_instance_6', 'cms_instance_7', 'cms_instance_8',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  # 'eqconfmeds_instance_5', 'eqconfmeds_instance_6', 'eqconfmeds_instance_7',
                                  # 'eqconfmeds_instance_8', 'eqconfmeds_instance_9', 'eqconfmeds_instance_10',
                                  # 'eqconfmeds_instance_11', 'eqconfmeds_instance_12', 'eqconfmeds_instance_13',
                                  # 'eqconfmeds_instance_14', 'eqconfmeds_instance_15', 'eqconfmeds_instance_16',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3', 'ixm_instance_4',
                                  'ixm_instance_5', 'ixm_instance_6', 'ixm_instance_7',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2', 'ps_instance_3',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbcrw_instance_5', 'sbcrw_instance_6', 'sbcrw_instance_7', 'sbcrw_instance_8',
                                  'sbcrw_instance_9', 'sbcrw_instance_10', 'sbcrw_instance_11', 'sbcrw_instance_12',
                                  'sbcrw_instance_13', 'sbcrw_instance_14', 'sbcrw_instance_15', 'sbcrw_instance_16',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4', 'sbctrunking_instance_5', 'sbctrunking_instance_6',
                                  'sbctrunking_instance_7', 'sbctrunking_instance_8', 'sbctrunking_instance_9',
                                  'sbctrunking_instance_10', 'sbctrunking_instance_11', 'sbctrunking_instance_12',
                                  'sbctrunking_instance_13', 'sbctrunking_instance_14', 'sbctrunking_instance_15',
                                  'sbctrunking_instance_16',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_secondary_cc_only_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 2
        cust_name = 'Robin'
        cc_users = 500
        uc_users = 0
        num_users = 500
        easg_enable = True

        # This test is designed to run the template with the smallest size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'aes_instance_1', 'aes_instance_2',
                                  'ams_instance_1',
                                  'cm_ess_instance_1',
                                  'cms_instance_1',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfmeds_instance_1',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1', ]

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_mixture_large(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 16000
        uc_users = 16000
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template a mixture of CC and UC to the maximum size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2', 'aam_instance_3', 'aam_instance_4',
                                  'aam_instance_5',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3', 'aawg_ms_instance_1',
                                  # 'aawg_ms_instance_2', 'aawg_ms_instance_3', 'aawg_ms_instance_4',
                                  # 'aawg_ms_instance_5', 'aawg_ms_instance_6', 'aawg_ms_instance_7',
                                  'aes_instance_1', 'aes_instance_2', 'aes_instance_3', 'aes_instance_4',
                                  'aes_instance_5', 'aes_instance_6', 'aes_instance_7', 'aes_instance_8',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3', 'ams_instance_4',
                                  'ams_instance_5', 'ams_instance_6', 'ams_instance_7', 'ams_instance_8',
                                  'ams_instance_9', 'ams_instance_10',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2', 'cm_duplex_instance_3',
                                  'cm_duplex_instance_4', 'cm_duplex_instance_5', 'cm_duplex_instance_6',
                                  'cm_duplex_instance_7', 'cm_duplex_instance_8', 'cm_duplex_instance_9',
                                  'cm_duplex_instance_10',
                                  'cms_instance_1', 'cms_instance_2', 'cms_instance_3', 'cms_instance_4',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  # 'eqconfmeds_instance_5', 'eqconfmeds_instance_6', 'eqconfmeds_instance_7',
                                  # 'eqconfmeds_instance_8', 'eqconfmeds_instance_9', 'eqconfmeds_instance_10',
                                  # 'eqconfmeds_instance_11', 'eqconfmeds_instance_12', 'eqconfmeds_instance_13',
                                  # 'eqconfmeds_instance_14', 'eqconfmeds_instance_15', 'eqconfmeds_instance_16',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3', 'ixm_instance_4',
                                  'ixm_instance_5', 'ixm_instance_6', 'ixm_instance_7',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2', 'ps_instance_3',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbcrw_instance_5', 'sbcrw_instance_6', 'sbcrw_instance_7', 'sbcrw_instance_8',
                                  'sbcrw_instance_9', 'sbcrw_instance_10', 'sbcrw_instance_11', 'sbcrw_instance_12',
                                  'sbcrw_instance_13', 'sbcrw_instance_14', 'sbcrw_instance_15', 'sbcrw_instance_16',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4', 'sbctrunking_instance_5', 'sbctrunking_instance_6',
                                  'sbctrunking_instance_7', 'sbctrunking_instance_8', 'sbctrunking_instance_9',
                                  'sbctrunking_instance_10',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_secondary_mixture_large(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA2'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 16000
        uc_users = 16000
        num_users = 32000
        easg_enable = True

        # This test is designed to run the template a mixture of CC and UC to the maximum size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  'aam_instance_3', 'aam_instance_4', 'aam_instance_5',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3', 'aawg_ms_instance_1',
                                  # 'aawg_ms_instance_2', 'aawg_ms_instance_3', 'aawg_ms_instance_4',
                                  # 'aawg_ms_instance_5', 'aawg_ms_instance_6', 'aawg_ms_instance_7',
                                  'aes_instance_1', 'aes_instance_2', 'aes_instance_3', 'aes_instance_4',
                                  'aes_instance_5', 'aes_instance_6', 'aes_instance_7', 'aes_instance_8',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3', 'ams_instance_4',
                                  'ams_instance_5', 'ams_instance_6', 'ams_instance_7', 'ams_instance_8',
                                  'ams_instance_9', 'ams_instance_10',
                                  'cm_ess_instance_1', 'cm_ess_instance_2', 'cm_ess_instance_3', 'cm_ess_instance_4',
                                  'cm_ess_instance_5',
                                  'cms_instance_1', 'cms_instance_2', 'cms_instance_3', 'cms_instance_4',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  # 'eqconfmeds_instance_5', 'eqconfmeds_instance_6', 'eqconfmeds_instance_7',
                                  # 'eqconfmeds_instance_8', 'eqconfmeds_instance_9', 'eqconfmeds_instance_10',
                                  # 'eqconfmeds_instance_11', 'eqconfmeds_instance_12', 'eqconfmeds_instance_13',
                                  # 'eqconfmeds_instance_14', 'eqconfmeds_instance_15', 'eqconfmeds_instance_16',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3', 'ixm_instance_4',
                                  'ixm_instance_5', 'ixm_instance_6', 'ixm_instance_7',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2', 'ps_instance_3',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbcrw_instance_5', 'sbcrw_instance_6', 'sbcrw_instance_7', 'sbcrw_instance_8',
                                  'sbcrw_instance_9', 'sbcrw_instance_10', 'sbcrw_instance_11', 'sbcrw_instance_12',
                                  'sbcrw_instance_13', 'sbcrw_instance_14', 'sbcrw_instance_15', 'sbcrw_instance_16',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4', 'sbctrunking_instance_5', 'sbctrunking_instance_6',
                                  'sbctrunking_instance_7', 'sbctrunking_instance_8', 'sbctrunking_instance_9',
                                  'sbctrunking_instance_10',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_primary_mixture_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA1'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 4000
        uc_users = 4000
        num_users = 8000
        easg_enable = True

        # This test is designed to run the template a mixture of CC and UC in the minimum size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3',
                                  # 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'aes_instance_1', 'aes_instance_2',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3',
                                  'cm_duplex_instance_1', 'cm_duplex_instance_2', 'cm_duplex_instance_3',
                                  'cm_duplex_instance_4',
                                  'cms_instance_1',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfapps_instance_2', 'eqconfmeds_instance_1',
                                  # 'eqconfmeds_instance_2', 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2',
                                  'sal_instance_1',
                                  'sbcems_instance_1', 'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3',
                                  'sbcrw_instance_4',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False

    def test_secondary_mixture_small(self):
        template_loader = jinja2.FileSystemLoader(searchpath="../templates/ACP_Template_0_3")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template('ACP_Template_0_3.tmpl')
        env.globals["set_global"] = set_global
        env.globals["ip_net"] = lambda addr, prefix: ipaddress.ip_network(f"{addr}/{prefix}", strict=False)
        datacenter_id = 'EMEA2'
        cust_num = 1
        cust_name = 'Robin'
        cc_users = 4000
        uc_users = 4000
        num_users = 8000
        easg_enable = True

        # This test is designed to run the template a mixture of CC and UC in the minimum size

        # Preset the VM options
        template_variables = {'datacenter_id': datacenter_id, 'cust_num': cust_num, 'cust_name': cust_name,
                              'cc_users': cc_users, 'uc_users': uc_users, 'num_users': num_users,
                              'easg_enable': easg_enable}

        # Run the template render
        try:
            test_yaml = (template.render(template_variables))
            test_json = yaml.safe_load(test_yaml)

            expected_instances = ['aads_instance_1', 'aads_instance_2',
                                  'aam_instance_1', 'aam_instance_2',
                                  # AAWG is currently disabled so the following update has been commented out
                                  # 'aawg_instance_1', 'aawg_instance_2', 'aawg_instance_3',
                                  # 'aawg_ms_instance_1', 'aawg_ms_instance_2',
                                  'aes_instance_1', 'aes_instance_2',
                                  'ams_instance_1', 'ams_instance_2', 'ams_instance_3',
                                  'cm_ess_instance_1', 'cm_ess_instance_2',
                                  'cms_instance_1',
                                  # Equinox is currently disabled so the following update has been commented out
                                  # 'eqconfapps_instance_1', 'eqconfmeds_instance_1', 'eqconfmeds_instance_2',
                                  # 'eqconfmeds_instance_3', 'eqconfmeds_instance_4',
                                  'ixm_instance_1', 'ixm_instance_2', 'ixm_instance_3',
                                  'precheck_instance_1',
                                  'ps_instance_1', 'ps_instance_2',
                                  'sal_instance_1',
                                  'sbcems_instance_1',
                                  'sbcrw_instance_1', 'sbcrw_instance_2', 'sbcrw_instance_3', 'sbcrw_instance_4',
                                  'sbctrunking_instance_1', 'sbctrunking_instance_2', 'sbctrunking_instance_3',
                                  'sbctrunking_instance_4',
                                  'sm_instance_1', 'sm_instance_2',
                                  'smgr_instance_1',
                                  'win_instance_1']

            for instance in expected_instances:
                assert instance_exists(test_json, instance), "{} doesn't exist".format(instance)

            assert len(test_json['vm_instances_specs'].keys()) == len(expected_instances), \
                "actual vms: {},\n expected vms: {}".format(test_json['vm_instances_specs'].keys(), expected_instances)

        except jinja2.exceptions.TemplateSyntaxError:
            print("Looks like there is a problem with the template")
            assert False
