import logging

import pytest

from components.scriptgenerator.healthcheck import basicvmhealthcheck as health_check
from components.scriptgenerator.sshutils import SshUtilHelper as ssh


@pytest.mark.ssh_util_helper
def test_run_command_on_remote_ext_when_no_ssh_connection_to_host(mocker):

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(health_check, 'check_if_ssh_port_open')
    health_check.check_if_ssh_port_open.return_value = False

    # invoke
    exit_code, stdout, stderr = ssh.run_command_on_remote_ext("ip", "port", "vm_uname", "vm_pwd", "cmd", logger)

    assert exit_code == -1
    assert stdout is None
    assert stderr is None


@pytest.mark.ssh_util_helper
def test_run_command_on_remote_ext_when_exception_thrown(mocker):

    # mocking
    logger = mocker.patch.object(logging, 'Logger')
    mocker.patch.object(health_check, 'check_if_ssh_port_open')
    health_check.check_if_ssh_port_open.side_effect = Exception

    # invoke
    exit_code, stdout, stderr = ssh.run_command_on_remote_ext("ip", "port", "vm_uname", "vm_pwd", "cmd", logger)

    assert exit_code == -1
    assert stdout is None
    assert stderr is None
