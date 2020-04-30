import sys
import pytest
import logging
from components.scriptgenerator import CustomerDetails
from unittest.mock import Mock
breeze_ssh_util = Mock()
sys.modules['components.scriptgenerator.sshutils.BreezeSshUtil'] = breeze_ssh_util
connection_class_instance = Mock()
breeze_ssh_util.BreezeSshConnection.return_value = connection_class_instance
from components.scriptgenerator.configurationlibrary.brz_config import config_accept_new_service


@pytest.mark.ps
def test_config_accept_new_service_successful(mocker):
    print(str(connection_class_instance))
    connection_class_instance.get_output.return_value="OKAY"

    vm_instance_name = "brz_instance_1"
    logger = mocker.patch.object(logging, 'Logger')
    customer_number = 3
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    return_list = []
    print(config_accept_new_service.do_work(customer_object, vm_instance_name, return_list))
    print(return_list)
    assert 1 == len(return_list)
    assert True == return_list[0]


@pytest.mark.ps
def test_config_accept_new_service_fails(mocker):
    print(str(connection_class_instance))
    connection_class_instance.get_output.return_value="FAILED"

    vm_instance_name = "brz_instance_1"
    logger = mocker.patch.object(logging, 'Logger')
    customer_number = 3
    customer_object = mocker.patch.object(CustomerDetails, 'GenericSolutionDeployment')
    customer_object.customer_number = customer_number
    customer_object.debug_logger = logger

    return_list = []
    print(config_accept_new_service.do_work(customer_object, vm_instance_name, return_list))
    print(return_list)
    assert 1 == len(return_list)
    assert False == return_list[0]
