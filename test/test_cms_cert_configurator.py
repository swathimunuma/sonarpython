import logging
import os.path as ospath

import pytest
from mock import ANY

from components.dbscripts import mongo_io as db, DbConstants as dbC
from components.scriptgenerator import CustomerDetails
from components.scriptgenerator import ScriptGeneratorConstants as SGConstants
from components.scriptgenerator.configurationlibrary.certs_config import cert_configurator_util as certUtil, certainty
from components.scriptgenerator.configurationlibrary.certs_config import cms_cert_configurator
from components.scriptgenerator.fileutils import FileSystemHelper
from components.scriptgenerator.sshutils import SshUtilHelper as ssh
from components.scriptgenerator.vmwarehelper import data_helper


@pytest.mark.cms
def test_install_cms_certificates(mocker):
    # variables
    customer_number = 3
    vm_instance_name = "CMS1"
    data_center_name = 'data_center'
    vm_type = "CMS"

    vm_name = 'vm_name'
    vm_ip = 'vm_ip'
    vm_u_name = 'vm_u_name'
    vm_pwd = 'vm_pwd'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_pwd = 'vm_root_pwd'

    windows_ip = 'win_ip'
    windows_username = 'username'
    windows_password = 'password'
    windows_instance_name = 'win_instance_name'
    port = 'port'
    request_file = 'request+file'
    swrepo_path = 'swrepo_path'
    output_signed_file = swrepo_path + "/" + vm_instance_name + '_cmsweb_signed.pem'
    ca_cert_file = swrepo_path + '/' + windows_instance_name + ".ca.crt"

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    mocker.patch.object(FileSystemHelper, 'get_customer_directory')
    FileSystemHelper.get_customer_directory.return_value = swrepo_path

    mocker.patch.object(data_helper, 'get_vm_details')
    data_helper.get_vm_details.return_value = vm_name, vm_ip, vm_u_name, vm_pwd, vm_root_u_name, vm_root_pwd, port

    mocker.patch.object(certainty, 'get_ca')
    certainty.get_ca.return_value = windows_ip, windows_username, windows_password, windows_instance_name

    mocker.patch.object(data_helper, 'get_dc_name_from_vm_data')
    data_helper.get_dc_name_from_vm_data.return_value = data_center_name

    mocker.patch.object(certUtil, 'get_latest_ca_cert_from_windows')
    mocker.patch.object(cms_cert_configurator, 'generate_private_key_for_cms')

    mocker.patch.object(cms_cert_configurator, 'generate_cert_req_for_cms')
    cms_cert_configurator.generate_cert_req_for_cms.return_value = request_file

    mocker.patch.object(cms_cert_configurator, 'sign_cert_request_for_cms')
    cms_cert_configurator.sign_cert_request_for_cms.return_value = output_signed_file

    mocker.patch.object(cms_cert_configurator, 'install_ca_certs_for_cms')
    mocker.patch.object(cms_cert_configurator, 'install_signed_cert_for_cms')
    mocker.patch.object(cms_cert_configurator, 'apply_new_certs_for_cms')

    mocker.patch.object(ssh, 'run_ssh_command_on_remote')

    mocker.patch.object(db, 'get_machine_data')

    db.get_machine_data.return_value = vm_type

    # call the method
    return_list = []
    cms_cert_configurator.install_cms_certificates(customer_object, vm_instance_name, return_list)

    # validation
    cms_cert_configurator.generate_private_key_for_cms.assert_called_with(customer_number, data_center_name,
                                                                          vm_instance_name, vm_ip, vm_root_u_name,
                                                                          vm_root_pwd, logger)

    cms_cert_configurator.generate_cert_req_for_cms.assert_called_with(vm_instance_name, vm_ip, vm_root_u_name,
                                                                       vm_root_pwd,
                                                                       swrepo_path, logger)

    certUtil.get_latest_ca_cert_from_windows.assert_called_with(
        windows_ip, windows_instance_name + ".ca.crt", windows_username, windows_password, swrepo_path)

    cms_cert_configurator.sign_cert_request_for_cms.assert_called_with(customer_number,
                                                                       vm_instance_name, request_file,
                                                                       output_signed_file, logger)
    cms_cert_configurator.install_ca_certs_for_cms.assert_called_with(vm_ip, vm_root_u_name, vm_root_pwd,
                                                                      ca_cert_file, logger)
    cms_cert_configurator.install_signed_cert_for_cms.assert_called_with(vm_ip, vm_root_u_name, vm_root_pwd,
                                                                         output_signed_file, logger)

    cms_cert_configurator.apply_new_certs_for_cms.assert_called_with(vm_ip, vm_root_u_name, vm_root_pwd, logger)

    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name, vm_root_pwd,
                                                     "rm -rf {0}".format(cms_cert_configurator.CMS_CERT_CUSTOM_DIR),
                                                     logger)


@pytest.mark.cms
def test_generate_private_key_for_cms(mocker):
    # variables
    customer_number = 3
    vm = "CMS1"
    deployment_type = dbC.PRIMARY
    vm_ip = 'vm_ip'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_u_pwd = 'vm_root_pwd'
    hostname = 'hostname'
    domain = 'domain'
    ou_name = 'ou_name'
    org_name = 'org_name'
    city_name = 'city_name'
    state_name = 'state_name'
    country_name = 'country_name'
    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(data_helper, 'get_hostname')
    data_helper.get_hostname.return_value = hostname

    mocker.patch.object(data_helper, 'get_domain')
    data_helper.get_domain.return_value = domain

    mocker.patch.object(data_helper, 'get_general_certificate_details')
    data_helper.get_general_certificate_details.return_value = ou_name, org_name, city_name, state_name, country_name

    mocker.patch.object(ssh, 'run_ssh_command_on_remote')

    # call function
    cms_cert_configurator.generate_private_key_for_cms(customer_number, deployment_type, vm, vm_ip, vm_root_u_name,
                                                       vm_root_u_pwd, logger)

    # verify
    data_helper.get_hostname.assert_called_with(customer_number, vm)
    data_helper.get_domain.assert_called_with(customer_number, vm)
    data_helper.get_general_certificate_details.assert_called_with(customer_number, deployment_type)
    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                                     vm_root_u_pwd, ANY, logger)


@pytest.mark.cms
def test_generate_cert_req_for_cms(mocker):
    # variables
    vm = "CMS1"
    vm_ip = 'vm_ip'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_u_pwd = 'vm_root_pwd'
    swrepo_path = 'swrepo_path'
    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(ssh, 'run_ssh_command_on_remote')
    mocker.patch.object(ssh, 'scp_get_file_from_remote')

    # call function
    cms_cert_configurator.generate_cert_req_for_cms(vm, vm_ip, vm_root_u_name, vm_root_u_pwd, swrepo_path, logger)

    # verify
    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                                     vm_root_u_pwd, ANY, logger)
    ssh.scp_get_file_from_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                                    vm_root_u_pwd, ANY, ANY, logger)


@pytest.mark.cms
def test_sign_cert_request_for_cms(mocker):
    # variables
    customer_number = 9
    data_center_name = 'data center'
    vm_instance_name = 'CMS1'

    windows_ip = 'windows_ip'
    windows_username = 'windows_username'
    windows_password = 'windows_password'
    windows_instance_name = 'windows_instance'
    signed_file = 'signed_file'
    cert_request_file = 'cert_request_file'

    logger = mocker.patch.object(logging, 'Logger')

    # mocking
    mocker.patch.object(data_helper, 'get_ip_address_1')
    data_helper.get_ip_address_1.return_value = windows_ip
    mocker.patch.object(data_helper, 'get_cli_username')
    data_helper.get_cli_username.return_value = windows_username
    mocker.patch.object(data_helper, 'get_cli_password')
    data_helper.get_cli_password.return_value = windows_password
    mocker.patch.object(ospath, 'isfile')
    ospath.isfile.return_value = True
    mocker.patch.object(certUtil, 'send_cert_request_for_signing')

    mocker.patch.object(certainty, 'get_ca')
    certainty.get_ca.return_value = windows_ip, windows_username, windows_password, windows_instance_name

    mocker.patch.object(data_helper, 'get_dc_name_from_vm_data')
    data_helper.get_dc_name_from_vm_data.return_value = data_center_name

    mocker.patch.object(certUtil, 'get_latest_ca_cert_from_windows')
    mocker.patch.object(cms_cert_configurator, 'generate_private_key_for_cms')

    # call method
    signed_file = cms_cert_configurator.sign_cert_request_for_cms(customer_number, vm_instance_name,
                                                                  cert_request_file, signed_file, logger)

    # verification
    windows_ip = data_helper.get_ip_address_1(customer_number, dbC.WINDOWS_DOMAIN_CONTROLLER)
    windows_username = data_helper.get_cli_username(customer_number, dbC.WINDOWS_DOMAIN_CONTROLLER)
    windows_password = data_helper.get_cli_password(customer_number, dbC.WINDOWS_DOMAIN_CONTROLLER)
    certUtil.send_cert_request_for_signing.assert_called_with(windows_ip, cert_request_file, signed_file,
                                                              windows_username, windows_password)


@pytest.mark.cms
def test_install_signed_cert_for_cms(mocker):
    # variables
    vm_ip = 'vp_ip'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_u_pwd = 'vm_root_u_pwd'
    path = "/signed_dir"
    file_name = "signed_file"
    signed_file = path + '/' + file_name

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(ssh, 'sftp_file_to_remote')
    mocker.patch.object(ssh, 'run_ssh_command_on_remote')

    # call method
    cms_cert_configurator.install_signed_cert_for_cms(vm_ip, vm_root_u_name, vm_root_u_pwd, signed_file, logger)

    # verification
    ssh.sftp_file_to_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                               vm_root_u_pwd, path, cms_cert_configurator.CMS_CERT_CUSTOM_DIR,
                                               logger, file_name)
    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                                     vm_root_u_pwd, ANY, logger)


@pytest.mark.cms
def test_install_ca_certs_for_cms(mocker):
    # variables
    vm_ip = 'vp_ip'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_u_pwd = 'vm_root_u_pwd'
    path = "/signed_dir"
    file_name = "ca_cert_file"
    ca_cert_file = path + '/' + file_name

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(ssh, 'sftp_file_to_remote')
    mocker.patch.object(ssh, 'run_ssh_command_on_remote')
    mocker.patch.object(ospath, 'isfile')
    ospath.isfile.return_value = True

    # call method
    cms_cert_configurator.install_ca_certs_for_cms(vm_ip, vm_root_u_name, vm_root_u_pwd, ca_cert_file, logger)

    # verification
    ssh.sftp_file_to_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name, vm_root_u_pwd, path,
                                               cms_cert_configurator.CMS_CERT_CUSTOM_DIR, logger, file_name)
    ssh.run_ssh_command_on_remote(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name, vm_root_u_pwd, ANY, logger)


@pytest.mark.cms
def test_apply_new_certs_for_cms(mocker):
    # variables
    vm_ip = 'vp_ip'
    vm_root_u_name = 'vm_root_u_name'
    vm_root_u_pwd = 'vm_root_u_pwd'

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(ssh, 'run_ssh_command_on_remote')

    # call method
    cms_cert_configurator.apply_new_certs_for_cms(vm_ip, vm_root_u_name, vm_root_u_pwd, logger)

    # verification
    ssh.run_ssh_command_on_remote.assert_called_with(vm_ip, SGConstants.DEFAULT_VM_PORT, vm_root_u_name,
                                                     vm_root_u_pwd, ANY, logger)
