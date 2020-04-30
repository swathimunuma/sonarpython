import pytest
import logging

import time

import json

from mock import ANY, call

from components.dbscripts import DbConstants as dbC
from components.scriptgenerator.configurationlibrary.cms_config import VmwareCMSDeployHelper
from components.scriptgenerator.sshutils import SshUtilHelper
from components.scriptgenerator.vmwarehelper import data_helper, VmwareDeployHelper


@pytest.mark.cms
def test_setup_cms_root_user(mocker):
    # variables
    site_name = dbC.TEXASDATACENTER
    root_password = "root_password"
    vm_instance_name = "abc"
    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_user')
    mocker.patch.object(time, "sleep")

    # call method
    VmwareCMSDeployHelper.setup_cms_root_user(site_name, vm_instance_name, root_password, logger)

    # verify
    VmwareCMSDeployHelper.setup_cms_user.assert_called_with(site_name, vm_instance_name, 'root', '', 'root',
                                                            root_password, logger, wait=False)
    time.sleep.assert_called_with(10)


@pytest.mark.cms
def test_setup_cms_user(mocker):
    # variables
    site_name = dbC.TEXASDATACENTER
    root_user = 'root'
    root_password = "root_password"
    user_account = "cms"
    user_password = "cms_password"
    vm_instance_name = "abc"
    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(VmwareDeployHelper, 'run_vm_commands')

    # call method
    VmwareCMSDeployHelper.setup_cms_user(site_name, vm_instance_name, root_user, root_password, user_account,
                                         user_password, logger)

    # verify
    VmwareDeployHelper.run_vm_commands.assert_called_with(site_name, vm_instance_name, ANY, logger, wait_for_done=True)
    params = VmwareDeployHelper.run_vm_commands.call_args[0]
    assert params[0] == site_name
    assert params[1] == vm_instance_name
    assert params[2]['cmds'][0][0] == "/bin/sh"
    assert params[2]['cmds'][0][1] == "-c 'echo " + user_account + ":" + user_password + " | /usr/sbin/chpasswd'"


@pytest.mark.cms
def test_setup_cms_timezone(mocker):
    # variables
    site_name = dbC.TEXASDATACENTER
    root_user = 'root'
    root_password = "root_password"
    vm_instance_name = "abc"
    timezone = "American/Denver"
    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(VmwareDeployHelper, 'run_vm_commands')

    # call method
    VmwareCMSDeployHelper.setup_cms_timezone(site_name, vm_instance_name, root_user, root_password, timezone, logger)

    # verify
    VmwareDeployHelper.run_vm_commands.assert_called_with(site_name, vm_instance_name, ANY, logger, wait_for_done=True)
    params = VmwareDeployHelper.run_vm_commands.call_args[0]
    assert params[0] == site_name
    assert params[1] == vm_instance_name
    assert params[2]['cmds'][1][0] == "/bin/ln"
    assert params[2]['cmds'][1][1] == "-s /usr/share/zoneinfo/{0} /etc/localtime".format(timezone)


@pytest.mark.cms
def test_setup_cms_network(mocker):
    # variables
    site_name = dbC.TEXASDATACENTER
    root_user = 'root'
    root_password = "root_password"
    vm_instance_name = "cms_instance_1"
    hostname = "hostname"
    ip_address_1 = "ip_address_1"
    domain = "domain"
    netmask = "netmask"
    gateway = "gateway"
    dns1 = "dns1"
    search_list = "search_list"
    logger = mocker.patch.object(logging, 'Logger')

    network_parameters = {
        'INTERFACE': 'eth0',
        'HOSTNAME': hostname,
        'IPADDR': ip_address_1,
        'DOMAIN': domain,
        'NETMASK': netmask,
        'GATEWAY': gateway,
        'DNS1': dns1,
        'SEARCH': search_list,
    }

    args = {
        "desc": "cmssvc-setup cms network",
        "cmds": [["/bin/sh", "-c \"echo INTERFACE=eth0 >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo HOSTNAME=hostname >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo IPADDR=ip_address_1 >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo DOMAIN=domain >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo NETMASK=netmask >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo GATEWAY=gateway >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo DNS1=dns1 >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/bin/sh", "-c \"echo SEARCH=search_list >> /tmp/cms_network.cfg\"", "root", "root_password"],
                 ["/cms/toolsbin/netconfig", "/tmp/cms_network.cfg", "root", "root_password"]]}

    # mocking
    mocker.patch.object(VmwareDeployHelper, 'run_vm_commands')

    # call method
    VmwareCMSDeployHelper.setup_cms_network(site_name, vm_instance_name, root_user, root_password,
                                            network_parameters, logger)

    print(json.dumps(json.dumps(VmwareDeployHelper.run_vm_commands.call_args_list[0][0][2])))
    # verify
    VmwareDeployHelper.run_vm_commands.assert_called_with(site_name, vm_instance_name, args, logger, wait_for_done=True)


@pytest.mark.cms
def test_get_cms_network_parameters(mocker):
    customer_number = 9
    vm_instance_name = "cms_instance_1"
    hostname = "hostname"
    ip_address_1 = "ip_address_1"
    domain = "domain"
    netmask = "netmask"
    gateway = "gateway"
    dns1 = "dns1"
    search_list = "search_list"

    mocker.patch.object(data_helper, 'get_hostname')
    data_helper.get_hostname.return_value = hostname

    mocker.patch.object(data_helper, 'get_ip_address_1')
    data_helper.get_ip_address_1.return_value = ip_address_1

    mocker.patch.object(data_helper, 'get_domain')
    data_helper.get_domain.return_value = domain

    mocker.patch.object(data_helper, 'get_netmask')
    data_helper.get_netmask.return_value = netmask

    mocker.patch.object(data_helper, 'get_gateway')
    data_helper.get_gateway.return_value = gateway

    mocker.patch.object(data_helper, 'get_dns')
    data_helper.get_dns.return_value = dns1

    mocker.patch.object(data_helper, 'get_search_list')
    data_helper.get_search_list.return_value = search_list

    network_parameters = {
        'INTERFACE': 'eth0',
        'HOSTNAME': hostname,
        'IPADDR': ip_address_1,
        'DOMAIN': domain,
        'NETMASK': netmask,
        'GATEWAY': gateway,
        'DNS1': dns1,
        'SEARCH': search_list,
    }

    # invoke
    ret = VmwareCMSDeployHelper.get_cms_network_parameters(customer_number, vm_instance_name)
    assert ret == network_parameters


@pytest.mark.cms
def test_setup_cms_easg(mocker):
    # variables
    customer_number = 9
    vm_instance_name = "CMS1"
    easg_enable_flag = 1
    vm_name = "CMS1Primary"
    vm_ip = "vm_ip"
    vm_u_name = "cms"
    vm_pwd = "vm_pwd"
    vm_root_u_name = "root"
    vm_root_pwd = "root_password"
    port = 20
    logger = mocker.patch.object(logging, 'Logger')
    easg_cmd = "EASGManage -f --enableEASG"

    # mocking
    mocker.patch.object(SshUtilHelper, 'run_pexpect_command_on_remote_with_root')
    SshUtilHelper.run_pexpect_command_on_remote_with_root.return_value = True, ""
    mocker.patch.object(data_helper, "get_vm_details")
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    # call method
    rc = VmwareCMSDeployHelper.setup_cms_easg(customer_number, vm_instance_name, easg_enable_flag, logger)

    # verify
    assert rc
    data_helper.get_vm_details.assert_called_with(customer_number, vm_instance_name)
    SshUtilHelper.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd,
                                                                             vm_root_u_name, vm_root_pwd,
                                                                             easg_cmd, '', logger,
                                                                             user_prompt="$", root_prompt="#")



@pytest.mark.cms
def test_setup_cms_easg_failure_path(mocker):
    # variables
    customer_number = 9
    vm_instance_name = "CMS1"
    easg_enable_flag = 1
    vm_name = "CMS1Primary"
    vm_ip = "vm_ip"
    vm_u_name = "cms"
    vm_pwd = "vm_pwd"
    vm_root_u_name = "root"
    vm_root_pwd = "root_password"
    port = 20
    logger = mocker.patch.object(logging, 'Logger')
    easg_cmd = "EASGManage -f --enableEASG"

    # mocking
    mocker.patch.object(SshUtilHelper, 'run_pexpect_command_on_remote_with_root')
    SshUtilHelper.run_pexpect_command_on_remote_with_root.return_value = False, ""
    mocker.patch.object(data_helper, "get_vm_details")
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    # call method
    rc = VmwareCMSDeployHelper.setup_cms_easg(customer_number, vm_instance_name, easg_enable_flag, logger)

    # verify
    assert not rc
    data_helper.get_vm_details.assert_called_with(customer_number, vm_instance_name)
    SshUtilHelper.run_pexpect_command_on_remote_with_root.assert_called_with(vm_ip, vm_u_name, vm_pwd,
                                                                             vm_root_u_name, vm_root_pwd,
                                                                             easg_cmd, '', logger,
                                                                             user_prompt="$", root_prompt="#")


@pytest.mark.cms
def test_setup_cms(mocker):
    # variables
    site_name = dbC.TEXASDATACENTER
    customer_number = 9
    vm_instance_name = "CMS1"
    vm_name = "CMS1Primary"
    logger = mocker.patch.object(logging, 'Logger')

    root_user = "root"
    root_password = "root_password"
    cms_user = "cms"
    cms_password = "cms_password"
    cmssvc_user = "cmssvc"
    cmssvc_password = "cmssvc_password"
    timezone = "American/Denver"
    network_parameters = {}

    easg_flag = "1"

    # mocking
    mocker.patch.object(data_helper, 'get_root_username')
    mocker.patch.object(data_helper, 'get_root_password')
    mocker.patch.object(data_helper, 'get_cli_username')
    mocker.patch.object(data_helper, 'get_cli_password')
    mocker.patch.object(data_helper, 'get_admin_username')
    mocker.patch.object(data_helper, 'get_admin_password')
    mocker.patch.object(data_helper, 'get_time_zone')
    mocker.patch.object(data_helper, 'get_ntp')
    mocker.patch.object(VmwareCMSDeployHelper, 'get_cms_network_parameters')
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_root_user')
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_user')
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_network')
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_timezone')
    mocker.patch.object(VmwareCMSDeployHelper, 'setup_cms_easg')

    data_helper.get_root_username.return_value = root_user
    data_helper.get_root_password.return_value = root_password
    data_helper.get_cli_username.return_value = cms_user
    data_helper.get_cli_password.return_value = cms_password
    data_helper.get_admin_username.return_value = cmssvc_user
    data_helper.get_admin_password.return_value = cmssvc_password
    data_helper.get_time_zone.return_value = timezone
    data_helper.get_easg_enable_flag.return_value = easg_flag

    setup_cms_user_calls =\
        [call(site_name, vm_name, root_user, root_password, cms_user, cms_password, logger),
         call(site_name, vm_name, root_user, root_password, cmssvc_user, cmssvc_password, logger)
         ]
    VmwareCMSDeployHelper.get_cms_network_parameters.return_value = network_parameters

    # call setup_cms
    VmwareCMSDeployHelper.setup_cms(site_name, vm_name, vm_instance_name, customer_number, logger)

    # validation
    VmwareCMSDeployHelper.setup_cms_root_user.assert_called_with(site_name, vm_name, root_password, logger)

    VmwareCMSDeployHelper.setup_cms_user.assert_has_calls(setup_cms_user_calls)

    VmwareCMSDeployHelper.setup_cms_timezone.assert_called_with(site_name, vm_name, root_user, root_password, timezone,
                                                                logger)

    VmwareCMSDeployHelper.setup_cms_network.assert_called_with(site_name, vm_name, root_user, root_password,
                                                               network_parameters, logger)

    VmwareCMSDeployHelper.setup_cms_easg.assert_called_with(customer_number, vm_instance_name, easg_flag, logger)
