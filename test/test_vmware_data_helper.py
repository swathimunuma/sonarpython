from components.dbscripts import DbConstants as dbC
from components.scriptgenerator.vmwarehelper import data_helper


def test_set_cust_env():
    value = 1
    data_helper.set_cust_env(123, "name", value)
    assert str(value) == data_helper.get_cust_env(123, "name")

    cms_authorization = "abc$a"
    data_helper.set_cust_env(123, dbC.CMS_AUTHORIZATION, cms_authorization)
    assert cms_authorization == data_helper.get_cust_env(123, dbC.CMS_AUTHORIZATION)

    cms_authorization = None
    data_helper.set_cust_env(123, dbC.CMS_AUTHORIZATION, cms_authorization)
    assert "" == data_helper.get_cust_env(123, dbC.CMS_AUTHORIZATION)

    cms_authorization = ''
    data_helper.set_cust_env(123, dbC.CMS_AUTHORIZATION, cms_authorization)
    assert "" == data_helper.get_cust_env(123, dbC.CMS_AUTHORIZATION)

    assert data_helper.get_cust_env(123, "a_not_exist_key") is None
