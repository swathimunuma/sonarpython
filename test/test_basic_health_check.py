import logging
import unittest.mock

import mock

from components.scriptgenerator.healthcheck import basicvmhealthcheck as bhc

logger = logging.getLogger('MyLogger')


@unittest.mock.patch('os.system')
def test_check_ping(os_system):
    os_system("ping -c 1 " + "10.5.8.242")
    bhc.check_ping.return_value = False
    assert bhc.check_ping("10.5.8.242", logger, 10, 1, 10) is False


# @requests_mock.mock()
# def test_check_https_request_via_curl():
#     # m.get("HTTPS://10.5.1.231//network-login")
#     # self.assertEqual(bhc.check_curl("HTTPS://10.5.1.231//network-login", True, logger), 200)
#     # mocker.patch.object(bhc, 'check_curl')
#     bhc.check_curl.return_value = 200
#     assert bhc.check_curl("HTTPS://10.5.1.231//network-login", True, logger) is 200
#     bhc.check_https_request_via_curl.return_value = True
#     assert bhc.check_https_request_via_curl("HTTPS://10.5.1.231//network-login", 3, 1, logger) is True

@mock.patch('components.scriptgenerator.healthcheck.basicvmhealthcheck.paramiko')
def test_check_ssh(paramiko):
    paramiko.SSHClient().return_value = False
    bhc.check_ssh.return_value = True
    assert bhc.check_ssh("testtxcm2a", "22", "cust", "14WdszLC", logger, 2, 30) is True


@mock.patch('components.scriptgenerator.healthcheck.basicvmhealthcheck.paramiko')
def test_is_ssh(paramiko):
    paramiko.SSHClient().return_value = False
    bhc.is_ssh.return_value = True
    assert bhc.is_ssh("testtxcm2a", "22", "cust", "14WdszLC", logger, 1, 2, 30) is True

#
# def test_get_vm_power_on_off_status(mocker):
#     mocker.patch.object(VDH, 'govc_sub_process_calls_output')
#     cmd = ScriptGeneratorConstants.GOVCBIN + " vm.info " + "testtxcm2a_10.5.8.242"
#     VDH.govc_sub_process_calls_output(cmd, "tx")
#     bhc.get_vm_power_on_off_status.return_value = "poweredOn"
#     assert "poweredOn" in bhc.get_vm_power_on_off_status("tx", "testtxcm2a_10.5.8.242", logger)
#
#
# def test_get_success_status_from_logfile(mocker):
#     mocker.patch.object(bhc, 'is_ssh')
#     bhc.is_ssh.return_value = True
#     assert bhc.is_ssh("testtxsm2", "22", "cust", "T9Eje4Ec", logger, 1, 2, 30) is True
#     bhc.get_success_status_from_logfile.return_value = False
#     assert bhc.get_success_status_from_logfile("testtxsm2", "22", "cust", "T9Eje4Ec", 2, 2,
#                                                "/var/log/Avaya/PostDeployLogs/post_install_sp.log",
#                                                "Lock removal successful for SMGR_Deployment", logger) is True
#
#
# def test_is_string_present(mocker):
#     mocker.patch.object(bhc, 'is_ssh')
#     bhc.is_ssh.return_value = True
#     assert bhc.is_ssh("testtxsm2", "22", "cust", "T9Eje4Ec", logger, 1, 2, 30) is True
#     bhc.is_string_present.return_value = True
#     assert bhc.is_string_present("testtxsm2", "22", "cust", "T9Eje4Ec", 2, 2, 1,
#                                  "/var/log/Avaya/PostDeployLogs/post_install_sp.log",
#                                  "Lock removal successful for SMGR_Deployment", logger) is True
#
#
# def test_check_if_maintanance_lock(mocker):
#     mocker.patch.object(SshUH, 'run_command_on_remote')
#     bhc.check_maintenance_lock.return_value = True
#     assert bhc.check_maintenance_lock("testtxsm2", "22", "cust", "T9Eje4Ec", 2, 2,
#                                       "/var/log/Avaya/PostDeployLogs/post_install_sp.log",
#                                       "Lock removal successful for SMGR_Deployment", logger) is True
