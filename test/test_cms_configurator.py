import logging
import os as os
import subprocess

import pytest

from components.dbscripts import DbConstants as dbC
from components.dbscripts import mongo_io as db
from components.scriptgenerator import CustomerDetails
from components.scriptgenerator import ScriptGeneratorConstants as SGConstants
from components.scriptgenerator.configurationlibrary import CommonConfigurator
from components.scriptgenerator.configurationlibrary.cms_config import CMSConfigurator as cms_configurator
from components.scriptgenerator.configurationlibrary.cms_config import CMSConstants as cmsC, config
from components.scriptgenerator.fileutils import FileSystemHelper
from components.scriptgenerator.generic_solution.generic_deployer import generic_function_library
from components.scriptgenerator.generic_solution.template_handler import template_constants
from components.scriptgenerator.healthcheck import basicvmhealthcheck as health_check
from components.scriptgenerator.sshutils import SshUtilHelper as ssh
from components.scriptgenerator.vmwarehelper import data_helper, VmwareDeployHelper


@pytest.mark.cms
def test_parse_optional_statement():
    line = "abc"
    line, optional, step = cms_configurator.parse_optional_statement(line)
    assert line == "abc"
    assert not optional
    assert step == 1

    line = "[*n*]"
    line, optional, step = cms_configurator.parse_optional_statement(line)
    assert line == ""
    assert optional
    assert step == 1

    line = "[*n9*]"
    line, optional, step = cms_configurator.parse_optional_statement(line)
    assert line == ""
    assert optional
    assert step == 9


@pytest.mark.cms
def test_parse_timeout_option_statement():
    # call method

    line = "abc"
    line, timeout = cms_configurator.parse_timeout_option_statement(line)
    assert line == "abc"
    assert timeout == -1

    line = "<10>"
    line, timeout = cms_configurator.parse_timeout_option_statement(line)
    assert line == ""
    assert timeout == 10

    line = "<20>abc"
    line, timeout = cms_configurator.parse_timeout_option_statement(line)
    assert line == "abc"
    assert timeout == 20


@pytest.mark.cms
def test_parse_interactions():
    # call method
    lines = ['## comment 1', 'Enter choice', '## comment 2', 'input:10', 'Enter choice', 'input:20', '[*n*]test']
    elist = cms_configurator.parse_cms_interactions(lines, ['10'])

    # verify
    assert 5 == len(elist)

    assert ssh.INTERACTION_TYPE_TEXT == elist[0].type
    assert "Enter choice" == elist[0].value
    assert not elist[0].optional
    assert not elist[0].sensitive

    assert ssh.INTERACTION_TYPE_INPUT == elist[1].type
    assert str(10) == elist[1].value
    assert elist[1].sensitive

    assert ssh.INTERACTION_TYPE_TEXT == elist[2].type
    assert "Enter choice" == elist[2].value
    assert not elist[2].optional
    assert not elist[2].sensitive

    assert ssh.INTERACTION_TYPE_INPUT == elist[3].type
    assert str(20) == elist[3].value
    assert not elist[3].sensitive

    assert ssh.INTERACTION_TYPE_TEXT == elist[4].type
    assert 'test' == elist[4].value
    assert elist[4].optional
    assert 10 == elist[4].timeout
    assert not elist[3].sensitive


@pytest.mark.cms
def test_load_cms_template_file():
    # varaible
    file_content = [" line1 ", " line2"]

    # prepare file
    file_name = "/tmp/test_load_cms_template_file"
    os.system('echo "{0}" > {1}'.format(file_content[0], file_name))
    os.system('echo "{0}" >> {1}'.format(file_content[1], file_name))

    try:
        # call method
        result = cms_configurator.load_cms_file(file_name)

        # verify
        assert 2 == len(result)
        assert "line1" == result[0]
        assert "line2" == result[1]
    finally:
        os.remove(file_name)


@pytest.mark.cms
def test_get_cm_instances(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    cm_instance_name = 'cm_instance_1'

    setup_data = {cmsC.CMS_TEMPLATE_SETUP_ACDS_KEY: [{cmsC.CMS_TEMPLATE_SETUP_CM_INSTANCE_KEY: cm_instance_name}]}

    # mocking
    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = setup_data

    # call method
    output = cms_configurator.get_cm_instances(customer_number, 'cms_instance_1')

    assert 1 == len(output)
    assert cm_instance_name == output[0]

    data_helper.get_vm_extra_parameters.assert_called_with(customer_number, cms_instance_name,
                                                           cmsC.CMS_TEMPLATE_SETUP_KEY)


@pytest.mark.cms
def test_authorize_cms(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    code = "abc"
    vm_ip = 'vm_ip'
    vm_name = 'vm_name_on_vmware'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    interactions = []
    port = 10

    authorization_data = {
        "authorization": {
            "forecasting_package": True,
            "vectoring_package": True,
            "graphics_feature": True,
            "external_call_history": True,
            "expert_agent_selection": True,
            "external_application": True,
            "global_dictionary_acd_groups": True,
            "maximum_simultaneous_supervisor_logins": 1600,
            "report_designer": True,
            "maximum_split_skill_members": 800000,
            "maximum_acds": 8,
            "authorized_agents": 100,
            "authorized_odbc_connection": 10
        },
    }

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = authorization_data

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    # call method
    rc = cms_configurator.authorize_cms(customer_object, cms_instance_name, code)

    # verify
    assert rc
    data_helper.get_vm_extra_parameters(customer_number, cms_instance_name,
                                        cmsC.CMS_TEMPLATE_AUTHORIZATION_KEY)
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_start_cms(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    # call method
    rc = cms_configurator.start_cms(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_setup_cms_weblm(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    weblm_ip = 'weblm_ip'
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_weblm_ip')
    data_helper.get_weblm_ip.return_value = weblm_ip

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, ''

    # call method
    rc = cms_configurator.setup_cms_weblm(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    data_helper.get_weblm_ip.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_start_cms_ids(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    # call method
    rc = cms_configurator.start_cms_ids(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_install_cms_packages(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []
    cmd = cmsC.CMS_COMMAND_CMSADM
    message = ''

    package_settings = \
        {
            "forecasting": True,
            "multi-tenancy": True,
            "dup-ip": True
        }

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = package_settings

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    # call method
    rc = cms_configurator.install_cms_packages(customer_object, cms_instance_name)

    # verify
    assert rc

    data_helper.get_vm_extra_parameters.assert_called_with(customer_number, cms_instance_name,
                                                           cmsC.CMS_TEMPLATE_PACKAGES_KEY)

    assert 3 == ssh.run_pexpect_command_on_remote_with_root.call_count
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd, cmd, message, logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_install_cms_packages_one_package(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []
    cmd = cmsC.CMS_COMMAND_CMSADM
    message = ''

    package_settings = \
        {
            "forecasting": True,
            "multi-tenancy": False,
            "dup-ip": False
        }

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = package_settings

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    # call method
    rc = cms_configurator.install_cms_packages(customer_object, cms_instance_name)

    # verify
    assert rc

    data_helper.get_vm_extra_parameters.assert_called_with(customer_number, cms_instance_name,
                                                           cmsC.CMS_TEMPLATE_PACKAGES_KEY)

    assert 1 == ssh.run_pexpect_command_on_remote_with_root.call_count
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd, cmd, message, logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_configure_dual_ip_happy_path(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    cm_hostname = 'cm_hostname'
    cm_ess_ip = 'cm_ess_ip'
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, ''

    # call method
    rc = cms_configurator.configure_dual_ip(customer_object, cms_instance_name, cm_hostname, cm_ess_ip)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_configure_dual_ip_error_path(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    cm_hostname = 'cm_hostname'
    cm_ess_ip = 'cm_ess_ip'
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = False, ''

    # call method
    rc = cms_configurator.configure_dual_ip(customer_object, cms_instance_name, cm_hostname, cm_ess_ip)

    # verify
    assert not rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_reboot_cms(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    dc = 'dc'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(db, 'get_default_datacenter')
    db.get_default_datacenter.return_value = dc, True

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(VmwareDeployHelper, 'reboot_vm')
    VmwareDeployHelper.reboot_vm.return_value = True

    mocker.patch.object(health_check, 'check_ssh')
    health_check.check_ssh.return_value = True

    # call method
    rc = cms_configurator.reboot_cms(customer_object, cms_instance_name)

    # verify
    assert rc
    db.get_default_datacenter.assert_called_with()
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    VmwareDeployHelper.reboot_vm.assert_called_with(dc, vm_name)
    health_check.check_ssh.assert_called_with(vm_ip, port, vm_u_name, vm_pwd, logger, 1000, 20)


@pytest.mark.cms
def test_reboot_cms_reboot_failed(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    dc = 'dc'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(db, 'get_default_datacenter')
    db.get_default_datacenter.return_value = dc, True

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(VmwareDeployHelper, 'reboot_vm')
    VmwareDeployHelper.reboot_vm.return_value = False

    mocker.patch.object(health_check, 'check_ssh')
    health_check.check_ssh.return_value = True

    # call method
    rc = cms_configurator.reboot_cms(customer_object, cms_instance_name)

    # verify
    assert not rc
    db.get_default_datacenter.assert_called_with()
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    VmwareDeployHelper.reboot_vm.assert_called_with(dc, vm_name)


@pytest.mark.cms
def test_reboot_cms_check_ssh_failed(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    dc = 'dc'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(db, 'get_default_datacenter')
    db.get_default_datacenter.return_value = dc, True

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(VmwareDeployHelper, 'reboot_vm')
    VmwareDeployHelper.reboot_vm.return_value = True

    mocker.patch.object(health_check, 'check_ssh')
    health_check.check_ssh.return_value = False

    # call method
    rc = cms_configurator.reboot_cms(customer_object, cms_instance_name)

    # verify
    assert not rc
    db.get_default_datacenter.assert_called_with()
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    VmwareDeployHelper.reboot_vm.assert_called_with(dc, vm_name)
    health_check.check_ssh.assert_called_with(vm_ip, port, vm_u_name, vm_pwd, logger, 1000, 20)


@pytest.mark.cms
def test_setup_cms_ntp(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    ntp = 'ntp'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_ntp')
    data_helper.get_ntp.return_value = ntp

    mocker.patch.object(CommonConfigurator, 'setup_ntp')
    CommonConfigurator.setup_ntp.return_value = True

    mocker.patch.object(cms_configurator, 'reboot_cms')
    cms_configurator.reboot_cms.return_value = True

    # call method
    rc = cms_configurator.setup_cms_ntp(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_ntp.assert_called_with(customer_number, cms_instance_name)
    CommonConfigurator.setup_ntp.assert_called_with(customer_number, cms_instance_name, ntp, logger,
                                                    user_prompt="$", root_prompt="#")
    cms_configurator.reboot_cms.assert_called_with(customer_object, cms_instance_name)


@pytest.mark.cms
def test_setup_cms_ntp_failed_path(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    ntp = 'ntp'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_ntp')
    data_helper.get_ntp.return_value = ntp

    mocker.patch.object(CommonConfigurator, 'setup_ntp')
    CommonConfigurator.setup_ntp.return_value = False

    mocker.patch.object(cms_configurator, 'reboot_cms')
    cms_configurator.reboot_cms.return_value = True

    # call method
    rc = cms_configurator.setup_cms_ntp(customer_object, cms_instance_name)

    # verify
    assert not rc
    data_helper.get_ntp.assert_called_with(customer_number, cms_instance_name)
    CommonConfigurator.setup_ntp.assert_called_with(customer_number, cms_instance_name, ntp, logger,
                                                    user_prompt="$", root_prompt="#")


@pytest.mark.cms
def test_setup_cms(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    cm_instance_name = "cm_instance_name"
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []
    data_center_name = 'data_center'
    cmd = 'tail -2 {0}'.format(cmsC.CMS_ADMIN_LOG)
    message = 'Setup completed successfully'
    vm_dir = '/tmp'

    settup_settings = \
        {
            "backup_option": 2,
            "backup_device": "/tmp",
            "acds": [
                {
                    "cm_instance": cm_instance_name,
                    "hostname": None,
                    "acd_version": 3,
                    "vectoring_enabled": True,
                    "expert_agent_selection_enabled": True,
                    "have_disconnect_supervion": True,
                    "phantom_abandon_call_timer": 0,
                    "local_port": 1,
                    "remote_port": 1,
                    "transport": 1,
                    "ip": None,
                    "port": 5001,
                    "maximum_splits_skills": 8000,
                    "total_split_skill_members": 360000,
                    "shifts": [
                        {
                            "start_time": "08:00AM",
                            "stop_time": "04:00PM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "04:00PM",
                            "stop_time": "12:00AM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "12:00AM",
                            "stop_time": "8:00AM",
                            "number_of_agents": 100
                        }
                    ],
                    "maximu_trunk_groups": 2000,
                    "maximum_trunks": 24000,
                    "maximum_unmeasured_trunks": 12000,
                    "minimum_work_codes": 1999,
                    "maximum_vectors": 8000,
                    "maximum_vdns": 30000
                }]
        }

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = settup_settings

    mocker.patch.object(data_helper, 'get_hostname')
    data_helper.get_hostname.return_value = 'hostname'

    mocker.patch.object(data_helper, 'get_virtual_ip_for_vm')
    data_helper.get_virtual_ip_for_vm.return_value = 'virt_ip'

    mocker.patch.object(data_helper, 'get_dc_type_from_vm_data')
    data_helper.get_dc_type_from_vm_data.return_value = 'Primary'

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(FileSystemHelper, 'get_customer_directory')
    FileSystemHelper.get_customer_directory.return_value = vm_dir

    mocker.patch.object(ssh, 'sftp_file_to_remote')

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, 'Successfully'

    mocker.patch.object(data_helper, 'get_instance_type')
    data_helper.get_instance_type.return_value = 'CMS'

    mocker.patch.object(data_helper, "get_fqdn")
    data_helper.get_fqdn.return_value = "host_name.acm.avaya.com"

    mocker.patch.object(cms_configurator, "add_node_name_for_cms")
    cms_configurator.add_node_name_for_cms.return_value = 0

    mocker.patch.object(cms_configurator, "add_communication_interface_process_for_cms")
    cms_configurator.add_communication_interface_process_for_cms.return_value = 0

    mocker.patch.object(cms_configurator, "save_translations_for_cms")
    cms_configurator.save_translations_for_cms.return_value = 0

    remote_helper = mocker.patch.object(data_helper, "RemoteDataAccess")
    remote_helper.get_keys_from_particular_machine_data.return_value = \
        {template_constants.VIRTUAL_IP_HOSTNAME: "virtual_ip_hostname",
         template_constants.VIRTUAL_IP_ADDRESS: "virtual_ip_addess"}

    # call method
    rc = cms_configurator.setup_cms(customer_object, data_center_name, cms_instance_name)

    # verify
    assert rc

    data_helper.get_instance_type.assert_called_with(customer_number, cms_instance_name)
    FileSystemHelper.get_customer_directory.assert_called_with(customer_number, data_center_name, 'CMS',
                                                               cms_instance_name)
    data_helper.get_hostname.assert_called_with(customer_number, cms_instance_name)
    data_helper.get_virtual_ip_for_vm.assert_called_with(customer_number, cm_instance_name)

    data_helper.get_vm_extra_parameters.assert_called_with(customer_number, cms_instance_name,
                                                           cmsC.CMS_TEMPLATE_SETUP_KEY)

    ssh.sftp_file_to_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name, vm_root_pwd, vm_dir,
                                               cmsC.CMS_INSTALL_DIR, logger, cmsC.CMS_INSTALL_FILE)

    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmd, message, logger,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_configure_dual_ips(mocker):
    # variables
    customer_number = 9
    cms_instance_name = "cms_instance_1"
    cm_instance_name = "cm_instance_name"
    cm_instance_name_standby = "cm_ess_name"
    cm_ip_standby = "cm_ip"

    settup_settings = \
        {
            "backup_option": 2,
            "backup_device": "/tmp",
            "acds": [
                {
                    "cm_instance": cm_instance_name,
                    "cm_instance_standby": cm_instance_name_standby,
                    "hostname": None,
                    "acd_version": 3,
                    "vectoring_enabled": True,
                    "expert_agent_selection_enabled": True,
                    "have_disconnect_supervion": True,
                    "phantom_abandon_call_timer": 0,
                    "local_port": 1,
                    "remote_port": 1,
                    "transport": 1,
                    "ip": None,
                    "port": 5001,
                    "maximum_splits_skills": 8000,
                    "total_split_skill_members": 360000,
                    "shifts": [
                        {
                            "start_time": "08:00AM",
                            "stop_time": "04:00PM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "04:00PM",
                            "stop_time": "12:00AM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "12:00AM",
                            "stop_time": "8:00AM",
                            "number_of_agents": 100
                        }
                    ],
                    "maximu_trunk_groups": 2000,
                    "maximum_trunks": 24000,
                    "maximum_unmeasured_trunks": 12000,
                    "minimum_work_codes": 1999,
                    "maximum_vectors": 8000,
                    "maximum_vdns": 30000
                }]
        }
    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_dc_type_from_vm_data')
    data_helper.get_dc_type_from_vm_data.return_value = template_constants.DATACENTER_TYPE_SECONDARY

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = settup_settings

    mocker.patch.object(data_helper, 'get_ip_address_1')
    data_helper.get_ip_address_1.return_value = cm_ip_standby

    mocker.patch.object(cms_configurator, 'stop_cms')
    mocker.patch.object(cms_configurator, 'start_cms')
    mocker.patch.object(cms_configurator, 'configure_dual_ip')
    cms_configurator.configure_dual_ip.return_value = True

    # call
    rc = cms_configurator.configure_dual_ips(customer_object, cms_instance_name)

    # validation
    assert rc
    data_helper.get_dc_type_from_vm_data.assert_called_with(customer_number, cms_instance_name)
    data_helper.get_vm_extra_parameters(customer_number, cms_instance_name, cmsC.CMS_TEMPLATE_SETUP_KEY)
    cms_configurator.stop_cms.assert_called_with(customer_object, cms_instance_name)
    data_helper.get_ip_address_1.assert_called_with(customer_number, cm_instance_name_standby)
    cms_configurator.configure_dual_ip.assert_called_with(customer_object, cms_instance_name, None, cm_ip_standby)
    cms_configurator.start_cms.assert_called_with(customer_object, cms_instance_name)


@pytest.mark.cms
def test_configure_dual_ips_failed_path(mocker):
    # variables
    customer_number = 9
    cms_instance_name = "cms_instance_1"
    cm_instance_name = "cm_instance_name"
    cm_instance_name_standby = "cm_ess_name"
    cm_ip_standby = "cm_ip"

    settup_settings = \
        {
            "backup_option": 2,
            "backup_device": "/tmp",
            "acds": [
                {
                    "cm_instance": cm_instance_name,
                    "cm_instance_standby": cm_instance_name_standby,
                    "hostname": None,
                    "acd_version": 3,
                    "vectoring_enabled": True,
                    "expert_agent_selection_enabled": True,
                    "have_disconnect_supervion": True,
                    "phantom_abandon_call_timer": 0,
                    "local_port": 1,
                    "remote_port": 1,
                    "transport": 1,
                    "ip": None,
                    "port": 5001,
                    "maximum_splits_skills": 8000,
                    "total_split_skill_members": 360000,
                    "shifts": [
                        {
                            "start_time": "08:00AM",
                            "stop_time": "04:00PM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "04:00PM",
                            "stop_time": "12:00AM",
                            "number_of_agents": 100
                        },
                        {
                            "start_time": "12:00AM",
                            "stop_time": "8:00AM",
                            "number_of_agents": 100
                        }
                    ],
                    "maximu_trunk_groups": 2000,
                    "maximum_trunks": 24000,
                    "maximum_unmeasured_trunks": 12000,
                    "minimum_work_codes": 1999,
                    "maximum_vectors": 8000,
                    "maximum_vdns": 30000
                }]
        }
    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_dc_type_from_vm_data')
    data_helper.get_dc_type_from_vm_data.return_value = template_constants.DATACENTER_TYPE_SECONDARY

    mocker.patch.object(data_helper, 'get_vm_extra_parameters')
    data_helper.get_vm_extra_parameters.return_value = settup_settings

    mocker.patch.object(data_helper, 'get_ip_address_1')
    data_helper.get_ip_address_1.return_value = cm_ip_standby

    mocker.patch.object(cms_configurator, 'stop_cms')
    mocker.patch.object(cms_configurator, 'start_cms')
    mocker.patch.object(cms_configurator, 'configure_dual_ip')
    cms_configurator.configure_dual_ip.return_value = False

    # call
    rc = cms_configurator.configure_dual_ips(customer_object, cms_instance_name)

    # validation
    assert not rc
    data_helper.get_dc_type_from_vm_data.assert_called_with(customer_number, cms_instance_name)
    data_helper.get_vm_extra_parameters(customer_number, cms_instance_name, cmsC.CMS_TEMPLATE_SETUP_KEY)
    cms_configurator.stop_cms.assert_called_with(customer_object, cms_instance_name)
    data_helper.get_ip_address_1.assert_called_with(customer_number, cm_instance_name_standby)
    cms_configurator.configure_dual_ip.assert_called_with(customer_object, cms_instance_name, None, cm_ip_standby)


@pytest.mark.cms
def test_configure_cms_firewall(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, ''

    # call method
    rc = cms_configurator.configure_cms_firewall(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_configure_cms_fips(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    interactions = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(cms_configurator, 'parse_cms_interactions')
    cms_configurator.parse_cms_interactions.return_value = interactions

    mocker.patch.object(ssh, 'run_pexpect_command_on_remote_with_root')
    ssh.run_pexpect_command_on_remote_with_root.return_value = True, ''

    # call method
    rc = cms_configurator.configure_cms_fips(customer_object, cms_instance_name)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd, vm_root_u_name,
                                                                   vm_root_pwd,
                                                                   cmsC.CMS_COMMAND_CMSSVC, '', logger, interactions,
                                                                   user_prompt='$', root_prompt='#')


@pytest.mark.cms
def test_setup_cms_ossi_scripts_primary(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    data_center_name = "dc"
    cm_instance_name = "cm_instance"
    cm_ip = "cm_ip"
    cm_cli_password = "cli_password"

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_dc_type_from_vm_data')
    data_helper.get_dc_type_from_vm_data.return_value = template_constants.DATACENTER_TYPE_PRIMARY

    mocker.patch.object(data_helper, 'get_ip_address_1')
    data_helper.get_ip_address_1.return_value = cm_ip

    mocker.patch.object(data_helper, 'get_cli_password')
    data_helper.get_cli_password.return_value = cm_cli_password

    mocker.patch.object(CommonConfigurator, 'setup_ossi_scripts')

    # call method
    rc = cms_configurator.update_translations(customer_object, data_center_name, cms_instance_name, cm_instance_name)

    # verify
    assert rc
    data_helper.get_dc_type_from_vm_data.assert_called_with(customer_number, cms_instance_name)
    data_helper.get_ip_address_1.assert_called_with(customer_number, cm_instance_name)
    data_helper.get_cli_password.assert_called_with(customer_number, cm_instance_name)
    CommonConfigurator.setup_ossi_scripts(customer_number, data_center_name, cms_instance_name, cm_ip, cm_cli_password)


@pytest.mark.cms
def test_setup_cms_ossi_scripts_secondary(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    data_center_name = "dc"
    cm_instance_name = "cm_instance"
    cm_ip = "cm_ip"
    cm_cli_password = "cli_password"

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_dc_type_from_vm_data')
    data_helper.get_dc_type_from_vm_data.return_value = template_constants.DATACENTER_TYPE_SECONDARY

    remote_helper = mocker.patch.object(data_helper, "RemoteDataAccess")
    remote_helper.get_keys_from_particular_machine_data.return_value = \
        {template_constants.VIRTUAL_IP_ADDRESS: cm_ip,
         template_constants.CLIPASSWORD: cm_cli_password}

    mocker.patch.object(CommonConfigurator, 'setup_ossi_scripts')

    # call method
    rc = cms_configurator.update_translations(customer_object, data_center_name, cms_instance_name, cm_instance_name)

    # verify
    assert rc
    data_helper.get_dc_type_from_vm_data.assert_called_with(customer_number, cms_instance_name)
    # remote_helper.get_keys_from_particular_machine_data.assert_called_with(cm_instance_name,
    #                                                                       template_constants.VIRTUAL_IP_ADDRESS,
    #                                                                       template_constants.CLIPASSWORD)
    CommonConfigurator.setup_ossi_scripts(customer_number, data_center_name, cms_instance_name, cm_ip, cm_cli_password)


@pytest.mark.cms
def test_start_cms_web(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(ssh, 'run_ssh_command_on_remote')
    ssh.run_ssh_command_on_remote.return_value = True, ''

    # call method
    cms_configurator.start_cms_web(customer_object, cms_instance_name)

    # verify
    data_helper.get_vm_details.assert_called_with(customer_number, cms_instance_name)
    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT,
                                                     vm_root_u_name, vm_root_pwd,
                                                     "cmsweb stop; cmsweb start",
                                                     logger)


@pytest.mark.cms
def test_do_cms_configurations_happy_path(mocker):
    # varaible
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    cm_instance_name = "cm_instance_1"
    data_center_name = 'data center'

    return_list = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(cms_configurator, 'get_cm_instances')
    cms_configurator.get_cm_instances.return_value = [cm_instance_name]

    mocker.patch.object(cms_configurator, 'setup_cms_ntp')
    cms_configurator.setup_cms_ntp.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms_ossi_scripts')
    cms_configurator.update_translations.return_value = True

    mocker.patch.object(cms_configurator, 'start_cms_ids')
    cms_configurator.start_cms_ids.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms_weblm')
    cms_configurator.setup_cms_weblm.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms')
    cms_configurator.setup_cms.return_value = True

    mocker.patch.object(cms_configurator, 'install_cms_packages')
    cms_configurator.install_cms_packages.return_value = True

    mocker.patch.object(cms_configurator, 'configure_dual_ips')
    cms_configurator.configure_dual_ips.return_value = True

    mocker.patch.object(cms_configurator, 'configure_cms_firewall')
    cms_configurator.configure_cms_firewall.return_value = True

    mocker.patch.object(cms_configurator, 'start_cms')
    cms_configurator.start_cms.return_value = True

    mocker.patch.object(cms_configurator, 'start_cms_web')
    cms_configurator.start_cms_web.return_value = True

    # call method
    rc = cms_configurator.do_cms_configurations(customer_object, cms_instance_name, data_center_name, return_list)

    # verify
    assert rc
    assert not (False in return_list)

    cms_configurator.get_cm_instances.assert_called_with(customer_number, cms_instance_name)

    cms_configurator.setup_cms_ntp.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.update_translations.assert_called_with(customer_object, data_center_name,
                                                            cms_instance_name, cm_instance_name)

    cms_configurator.start_cms_ids.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.setup_cms_weblm.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.setup_cms.assert_called_with(customer_object, data_center_name, cms_instance_name)

    cms_configurator.install_cms_packages.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.configure_dual_ips.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.configure_cms_firewall.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.start_cms.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.start_cms_web.assert_called_with(customer_object, cms_instance_name)


@pytest.mark.cms
def test_do_cms_configurations_failure_one_sub_task_failed(mocker):
    # varaible
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    cm_instance_name = "cm_instance_1"
    data_center_name = 'data center'

    return_list = []

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(cms_configurator, 'get_cm_instances')
    cms_configurator.get_cm_instances.return_value = [cm_instance_name]

    mocker.patch.object(cms_configurator, 'setup_cms_ntp')
    cms_configurator.setup_cms_ntp.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms_ossi_scripts')
    cms_configurator.update_translations.return_value = True

    mocker.patch.object(cms_configurator, 'start_cms_ids')
    cms_configurator.start_cms_ids.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms_weblm')
    cms_configurator.setup_cms_weblm.return_value = True

    mocker.patch.object(cms_configurator, 'setup_cms')
    cms_configurator.setup_cms.return_value = True

    mocker.patch.object(cms_configurator, 'install_cms_packages')
    cms_configurator.install_cms_packages.return_value = True

    mocker.patch.object(cms_configurator, 'configure_dual_ips')
    cms_configurator.configure_dual_ips.return_value = True

    mocker.patch.object(cms_configurator, 'configure_cms_firewall')
    cms_configurator.configure_cms_firewall.return_value = True

    mocker.patch.object(cms_configurator, 'start_cms')
    cms_configurator.start_cms.return_value = False

    mocker.patch.object(cms_configurator, 'start_cms_web')
    cms_configurator.start_cms_web.return_value = True

    # call method
    rc = cms_configurator.do_cms_configurations(customer_object, cms_instance_name, data_center_name, return_list)

    # verify
    assert not rc
    assert False in return_list

    cms_configurator.get_cm_instances.assert_called_with(customer_number, cms_instance_name)

    cms_configurator.setup_cms_ntp.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.update_translations.assert_called_with(customer_object, data_center_name,
                                                            cms_instance_name, cm_instance_name)

    cms_configurator.start_cms_ids.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.setup_cms_weblm.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.setup_cms.assert_called_with(customer_object, data_center_name, cms_instance_name)

    cms_configurator.install_cms_packages.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.configure_dual_ips.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.configure_cms_firewall.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.start_cms.assert_called_with(customer_object, cms_instance_name)

    cms_configurator.start_cms_web.assert_called_with(customer_object, cms_instance_name)


@pytest.mark.cms
def test_get_num_of_node_names(mocker):
    # variables
    customer_number = 100
    deployment_type = dbC.PRIMARY
    cm = 'CM2'
    cms = "CMS2"
    cms_swrepo = '/swrepo/a'
    ossi_cmd_prefix = '/swrepo/b'

    # mocking
    mocker.patch.object(cms_configurator, 'get_cms_common')
    cms_configurator.get_cms_common.return_value = cms_swrepo, ossi_cmd_prefix

    mocker.patch.object(subprocess, 'call')
    mocker.patch.object(subprocess, 'check_output')
    subprocess.check_output.side_effect = ["",  "4"]

    # invoke
    assert not cms_configurator.check_node_name(customer_number, deployment_type, cm, cms)

    # verification
    cmd = '{0} {1}/{2} {1}/{2}.o'.format(ossi_cmd_prefix, cms_swrepo, cmsC.CMS_RES_CM_RETRIEVE_NODE_NAMES)
    subprocess.call.assert_called_with(cmd, shell=True)

    cmd = "/bin/grep '6800ff00 = IP' {0}/{1}.o | /bin/wc -l".format(cms_swrepo, cmsC.CMS_RES_CM_RETRIEVE_NODE_NAMES)
    subprocess.check_output.assert_called_with(cmd, shell=True)


@pytest.mark.cms
def test_add_node_name_for_cms(mocker):
    # variables
    customer_number = 100
    deployment_type = dbC.PRIMARY
    cm = 'CM2'
    cms = "CMS2"
    node_name = 'txcms2'
    ip = 'ip'
    cms_swrepo = '/swrepo/a'
    ossi_cmd_prefix = '/swrepo/b'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(cms_configurator, 'get_cms_common')
    cms_configurator.get_cms_common.return_value = cms_swrepo, ossi_cmd_prefix

    mocker.patch.object(subprocess, 'call')
    subprocess.call.return_value = 0

    assert 0 == cms_configurator.add_node_name_for_cms(customer_number, deployment_type, cm, cms, node_name, ip, logger)
    cmd = '{0} {1}/{2} {1}/{2}.o'.format(ossi_cmd_prefix, cms_swrepo, cmsC.CMS_RES_CM_CHANGE_NODE_NAME_IP)
    subprocess.call.assert_called_with(cmd, shell=True)


@pytest.mark.cms
def test_add_communication_interface_process_for_cms(mocker):
    # variables
    customer_number = 100
    deployment_type = dbC.PRIMARY
    cm = 'CM2'
    cms = "CMS2"
    node_name = 'txcms2'
    cms_swrepo = '/swrepo/a'
    ossi_cmd_prefix = '/swrepo/b'
    acd = {
        "cm_instance": cms,
        "hostname": None,
        "acd_version": 3,
        "vectoring_enabled": True,
        "expert_agent_selection_enabled": True,
        "have_disconnect_supervion": True,
        "phantom_abandon_call_timer": 0,
        "local_port": 1,
        "remote_port": 1,
        "transport": 1,
        "ip": None,
        "port": 5001,
        "maximum_splits_skills": 8000,
        "total_split_skill_members": 360000,
        "shifts": [
            {
                "start_time": "08:00AM",
                "stop_time": "04:00PM",
                "number_of_agents": 100
            },
            {
                "start_time": "04:00PM",
                "stop_time": "12:00AM",
                "number_of_agents": 100
            },
            {
                "start_time": "12:00AM",
                "stop_time": "8:00AM",
                "number_of_agents": 100
            }
        ],
        "maximu_trunk_groups": 2000,
        "maximum_trunks": 24000,
        "maximum_unmeasured_trunks": 12000,
        "minimum_work_codes": 1999,
        "maximum_vectors": 8000,
        "maximum_vdns": 30000
    }
    seq = 1
    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(cms_configurator, 'get_cms_common')
    cms_configurator.get_cms_common.return_value = cms_swrepo, ossi_cmd_prefix

    mocker.patch.object(subprocess, 'call')
    subprocess.call.return_value = 0

    mocker.patch.object(cms_configurator, "write_file")

    # invoke
    assert 0 == cms_configurator.add_communication_interface_process_for_cms(customer_number, deployment_type,
                                                                             cm, cms,
                                                                             seq, node_name, acd, logger)

    cmd = '{0} {1}/{2} {1}/{2}.o'.format(ossi_cmd_prefix, cms_swrepo,
                                         cmsC.CMS_RES_CM_CHANGE_COMMUNICATOR_INTERFACE_PROCESS)
    subprocess.call.assert_called_with(cmd, shell=True)


@pytest.mark.cms
def test_save_translations_for_cms(mocker):
    # variables
    customer_number = 100
    deployment_type = dbC.PRIMARY
    cm = 'CM2'
    cms = "CMS2"
    cms_swrepo = '/swrepo/a'
    ossi_cmd_prefix = '/swrepo/b'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(cms_configurator, 'get_cms_common')
    cms_configurator.get_cms_common.return_value = cms_swrepo, ossi_cmd_prefix

    mocker.patch.object(subprocess, 'call')
    subprocess.call.return_value = 0

    # invoke
    assert 0 == cms_configurator.save_translations_for_cms(customer_number, deployment_type, cm, cms, logger)

    cmd = '{0} {1}/{2} {1}/{2}.o'.format(ossi_cmd_prefix, cms_swrepo,
                                         cmsC.CMS_RES_CM_SAVE_TRANSLATIONS)
    subprocess.call.assert_called_with(cmd, shell=True)


@pytest.mark.cms
def test_config_do_work(mocker):
    # variables
    customer_number = 3
    cms_instance_name = 'cms_instance_1'
    vm_name = 'vm_name_on_vmware'
    vm_ip = 'vm_ip'
    vm_u_name = 'cms'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'root'
    vm_root_pwd = 'vm_root_pwd'
    port = 10
    dc = "dc"
    return_list = []

    # mocking

    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(data_helper, 'get_dc_name_from_vm_data')
    data_helper.get_dc_name_from_vm_data.return_value = dc

    mocker.patch.object(generic_function_library, 'invoke_configure_software_tasks')

    mocker.patch.object(cms_configurator, "do_cms_configurations")

    # call
    config.do_work(customer_object, cms_instance_name, return_list)

    # validation
    cms_configurator.do_cms_configurations.assert_called_with(customer_object, cms_instance_name, dc, return_list)
