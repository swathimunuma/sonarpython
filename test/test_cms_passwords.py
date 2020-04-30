import pytest

from components.scriptgenerator.configurationlibrary.pwd_config import pwd_funct_matrix
from components.scriptgenerator.configurationlibrary.pwd_config import pwd_changer
from components.scriptgenerator.generic_solution.template_handler.template_constants import CLIPASSWORD, ROOTPASSWORD, \
    ADMINPASSWORD


@pytest.mark.cms
@pytest.mark.password_change
def test_cms_password_basic():
    vm_name = "cms_instance_1"
    assert pwd_funct_matrix.get_password_change_function(vm_name, "cms") == pwd_changer.change_cli_password
    assert pwd_funct_matrix.get_password_change_function(vm_name, "cmssvc") == pwd_changer.change_admin_password
    assert pwd_funct_matrix.get_password_change_function(vm_name, "root") == pwd_changer.change_root_password

    assert pwd_funct_matrix.get_db_key(vm_name, "cms") == CLIPASSWORD
    assert pwd_funct_matrix.get_db_key(vm_name, "cmssvc") == ADMINPASSWORD
    assert pwd_funct_matrix.get_db_key(vm_name, "root") == ROOTPASSWORD


