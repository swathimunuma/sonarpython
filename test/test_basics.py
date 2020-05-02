import pytest

from components.dbscripts import mongo_io as db
from components.lifecyclemgr.resources import api_solutions as api_s
# from components.scriptgenerator import AcpSolutionDeployer as acp_s
from components.scriptgenerator.vmwarehelper import VmwareDeployHelper as VmDH
from components.test.test_constants import test_api_solutions as tas
from components.web.webmodule import create_app


@pytest.fixture(scope="session", autouse=True)
def pre_test():
    VmDH.save_datacenter_details(tas.FACTORY, tas.HOSTNAME, tas.USERNAME, tas.PASSWORD, tas.IGNORE_SSL,
                                 tas.SITE_NAME, tas.SITE_FNAME,
                                 tas.DATACENTER, tas.DATASTORE, tas.CLUSTER, tas.DISK_PROVISIONING,
                                 tas.RESOURCE_POOL)


@pytest.fixture
def app():
    app = create_app()
    return app


def test_get_list_of_deployed_customers_blank_response(app):
    res = acp_s.get_list_of_deployed_customers()
    assert res == []


def test_get_customer_information_blank_response(app):
    res = acp_s.get_customer_information(5)
    assert res["customerName"] == "Not in parameters list"
    # assert res == {'numberOfUsers': None, 'remoteSupport': None, 'customerName': None, 'primaryDeploymentType': None,
    #                'primaryDeploymentState': None, 'primaryLocation': None, 'secondaryLocation': None,
    #                'secondaryDeploymentType': None, 'secondaryDeploymentState': None, 'numberOfRequests': None,
    #                'deploymentDate': None, 'requestType': None}


def test_get_all_solns_info_blank_response(app):
    res = api_s.get_all_solutions_info()
    assert res == []


def test_get_solution_info_blank_response(app):
    cust_id = 5
    res = api_s.get_solution_info(cust_id)
    assert res["customerName"] == "Not in parameters list"
    # assert res == {'numberOfUsers': -1, 'remoteSupport': -1, 'customerName': -1, 'primaryDeploymentType': -1,
    #                'primaryDeploymentState': -1, 'primaryLocation': -1, 'secondaryLocation': -1,
    #                'secondaryDeploymentType': -1, 'secondaryDeploymentState': -1, 'numberOfRequests': -1,
    #                'deploymentDate': -1, 'requestType': -1, 'customerId': 5}


def test_create_solution_new_solution(app):
    res = api_s.create_solution(5, 4000, 'FALSE', 'test')
    assert 'Success' in res


def test_create_solution_already_solution_exists(app):
    res = api_s.create_solution(5, 4000, 'FALSE', 'test')
    assert res == (None, 'Solution already exists, customer ID = 5')


def test_get_list_of_deployed_customers(app):
    res = acp_s.get_list_of_deployed_customers()
    assert res == [5]


def test_get_customer_information(app):
    cust_id = 5
    res = acp_s.get_customer_information(cust_id)
    assert res['customerName'] == 'test'


def test_get_all_solns_info(app):
    res = api_s.get_all_solutions_info()
    assert res[0]['customerName'] == 'test'


def test_get_solution_info(app):
    cust_id = 5
    res = api_s.get_solution_info(cust_id)
    assert res['customerName'] == 'test'


def test_delete_solution():
    res = db.remove_cust_number(5)
    database = db.create_client()
    table_cust = database['customer']
    table_cust.drop()
    assert res is None

