import os
import pytest
import tempfile
import tarfile
import shutil

from components.scriptgenerator.generic_solution.generic_configurator import generic_configurator_reader as gen_config

from components.scriptgenerator.generic_solution.generic_deployer import generic_constants
from components.scriptgenerator.generic_solution.template_handler import template_constants
from components.dbscripts import mongo_io as db

from components.maintenance import template_manager


@pytest.fixture
def test_template_id():

    template_root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates")
    for dir_name in os.listdir(template_root_dir):
        template_file = os.path.join(template_root_dir, dir_name, dir_name + ".tmpl")
        if os.path.exists(template_file):
            return dir_name


@pytest.fixture
def override_template_store_dir(monkeypatch):
    template_store_root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates")
    monkeypatch.setattr(template_constants, 'TEMPLATE_STORE_LOCATION', template_store_root_dir)
    return template_store_root_dir


@pytest.mark.templatemanager
def test_convert_application_instance_type_list_to_template_variables():

    product_list = [generic_constants.APP_TYPE_CM_DUPLEX,
                    generic_constants.APP_TYPE_CM_ESS,
                    generic_constants.APP_TYPE_WDC]
    template_variables = template_manager.convert_application_instance_type_list_to_template_variables(product_list)
    assert template_constants.TEMPLATE_VARIABLE_PRODUCT_CM in template_variables
    assert template_constants.TEMPLATE_VARIABLE_PRODUCT_WIN in template_variables

    product_list = [generic_constants.APP_TYPE_CM_DUPLEX]
    template_variables = template_manager.convert_application_instance_type_list_to_template_variables(product_list)
    assert template_constants.TEMPLATE_VARIABLE_PRODUCT_CM in template_variables

    product_list = [generic_constants.APP_TYPE_CM_ESS]
    template_variables = template_manager.convert_application_instance_type_list_to_template_variables(product_list)
    assert template_constants.TEMPLATE_VARIABLE_PRODUCT_CM in template_variables

    product_list = [generic_constants.APP_TYPE_WDC]
    template_variables = template_manager.convert_application_instance_type_list_to_template_variables(product_list)
    assert template_constants.TEMPLATE_VARIABLE_PRODUCT_WIN in template_variables

@pytest.mark.templatemanager
def test_convert_list_to_dic():

    input_list = ['a', 'b']
    output_dict = template_manager.convert_list_to_dic(input_list)
    assert 1 in output_dict
    assert output_dict[1] == 'a'
    assert 2 in output_dict
    assert output_dict[2] == 'b'


@pytest.mark.templatemanager
def test_convert_to_kvp():

    input_dict = {1:'a', 2:'b'}
    output_kvp = template_manager.convert_to_kvp(input_dict)
    assert len(output_kvp) == 2
    assert 1 == output_kvp[0]['key']
    assert 'a' == output_kvp[0]['value']
    assert 2 == output_kvp[1]['key']
    assert 'b' == output_kvp[1]['value']


@pytest.mark.templatemanager
def test_get_template_root_dir():

    template_root_dir = template_manager.get_template_root_dir('template_id')
    assert template_root_dir == os.path.join(template_constants.TEMPLATE_STORE_LOCATION, 'template_id')


@pytest.mark.templatemanager
def test_get_master_template_file_name():
    template_master_file_name = template_manager.get_master_template_file_name('template_id')
    assert template_master_file_name == 'template_id.tmpl'


@pytest.mark.templatemanager
def test_get_master_template_file_at():

    template_master_file = template_manager.get_master_template_file_at('/tmp', 'template_id')
    assert template_master_file ==  '/tmp/template_id.tmpl'


def test_get_template_meta_file():

    template_meta_file_name = template_manager.get_template_meta_file('template_id')
    assert template_meta_file_name == os.path.join(template_constants.TEMPLATE_STORE_LOCATION,
                                                   'template_id', 'template_id.tmpl')

@pytest.mark.templatemanager
def test_render_template_details(override_template_store_dir, test_template_id):

    template_id = test_template_id
    template_store_root_dir = override_template_store_dir
    template_dir = os.path.join(template_store_root_dir, template_id)

    template_master_file = template_manager.get_master_template_file_at(template_dir, template_id)
    template_details = template_manager.render_template_details(template_master_file)

    assert template_details is not None
    template_details = template_details[template_constants.TEMPLATE_SPECS_OBJ_KEY]

    assert template_constants.TEMPLATE_METADATA_ID in template_details
    assert template_constants.TEMPLATE_METADATA_NAME in template_details
    assert template_constants.TEMPLATE_METADATA_VERSION in template_details
    assert template_constants.TEMPLATE_METADATA_AUTHOR in template_details
    assert template_constants.TEMPLATE_METADATA_DESCRIPTION in template_details


@pytest.mark.templatemanager
def test_parse_meta_data(override_template_store_dir, test_template_id):

    template_id = test_template_id
    template_store_root_dir = override_template_store_dir
    template_dir = os.path.join(template_store_root_dir, template_id)

    template_master_file = template_manager.get_master_template_file_at(template_dir, template_id)
    template_details = template_manager.parse_meta_data(template_master_file)

    assert template_details is not None

    assert template_constants.TEMPLATE_METADATA_ID in template_details
    assert template_constants.TEMPLATE_METADATA_NAME in template_details
    assert template_constants.TEMPLATE_METADATA_VERSION in template_details
    assert template_constants.TEMPLATE_METADATA_AUTHOR in template_details
    assert template_constants.TEMPLATE_METADATA_DESCRIPTION in template_details


@pytest.mark.templatemanager
def test_template_exists(override_template_store_dir, test_template_id):

    template_id = test_template_id
    assert template_manager.template_exists(template_id)

    template_id = template_id + "_abcd1234"
    assert not template_manager.template_exists(template_id)


@pytest.mark.templatemanager
def test_get_template_solutions(mocker):
    template_id = 'abc'
    customers = [1, 2]
    # mock db
    mocker.patch.object(db, 'get_customers_by_template_id')
    db.get_customers_by_template_id.return_value = customers

    ret_customers = template_manager.get_template_solutions(template_id)
    assert customers == ret_customers


@pytest.mark.templatemanager
def test_get_basic_template_variables(mocker):

    mocker.patch.object(gen_config, "get_datacenter_configured_for_the_agent")
    gen_config.get_datacenter_configured_for_the_agent.return_value = [0]
    template_variables = template_manager.get_basic_template_variables()
    assert 0 == template_variables['cust_num']
    assert 'abc' == template_variables['cust_name']
    assert 4000 == template_variables['num_users']
    assert '0' == template_variables['datacenter_id']


@pytest.mark.templatemanager
def test_render_template(test_template_id):

    template_id = test_template_id
    template_variables = {
        'cust_num': 10,
        'cust_name': 'abc',
        'num_users': 4000,
        'datacenter_id': 'NAR1'
    }

    json_data, error_list = template_manager.render_template(template_id, template_variables)

    assert json_data is not None
    assert len(json_data[template_constants.VM_INSTANCE_SPEC_OBJ_KEY]) > 0


@pytest.mark.templatemanager
def test_get_product_parameters(override_template_store_dir, test_template_id):

    template_id = test_template_id
    product_parameters = template_manager.get_product_parameters(template_id)
    assert "CM" in product_parameters


@pytest.mark.templatemanager
def test_check_template_errors(override_template_store_dir, test_template_id):

    template_errors = template_manager.check_template_errors(test_template_id)
    if template_errors is not None and len(template_errors) > 0:
        assert isinstance(template_errors, list)
        assert isinstance(template_errors[0], str)


@pytest.mark.templatemanager
def test_get_template_errors(override_template_store_dir, test_template_id):

    template_errors = template_manager.get_template_errors(test_template_id, kvp=True)
    if template_errors is not None and len(template_errors) > 0:
        assert isinstance(template_errors, list)
        assert 1 == template_errors[0]['key']


@pytest.mark.templatemanager
def test_get_template(override_template_store_dir, test_template_id):

    template = template_manager.get_template(test_template_id)
    assert template is not None
    assert template[template_constants.TEMPLATE_METADATA_ID] is not None

    template = template_manager.get_template(test_template_id, show_inuse=True, kvp=True)
    assert template is not None
    assert len(template) > 0
    assert template[0]['key'] is not None


@pytest.mark.templatemanager
def test_get_templates(override_template_store_dir):
    templates = template_manager.get_templates()
    assert isinstance(templates, list)
    assert len(templates) > 0
    assert isinstance(templates[0], dict)


@pytest.mark.templatemanager
def test_get_templates_as_choices(override_template_store_dir):
    templates = template_manager.get_templates_as_choices()
    assert isinstance(templates, list)
    assert len(templates) > 0
    assert isinstance(templates[0], tuple)


@pytest.mark.templatemanager
def test_delete_template(mocker):

    template_id = 'abc'
    dir = tempfile.mkdtemp()

    mocker.patch.object(template_manager, "get_template_root_dir")
    template_manager.get_template_root_dir.return_value = dir
    template_manager.delete_template(template_id)

    assert not os.path.exists(dir)


@pytest.mark.templatemanager
def create_tar_file(output_filename, source_dir):
    with tarfile.open(output_filename, "w") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))


@pytest.mark.templatemanager
def test_extract_template(override_template_store_dir, test_template_id):

    tar_file = tempfile.mktemp()
    src_dir = os.path.join(override_template_store_dir, test_template_id, "")
    create_tar_file(tar_file, src_dir)

    work_dir = tempfile.mkdtemp()

    try:
        rc, message = template_manager.extract_template(work_dir, tar_file)
        assert rc == template_manager.UPLOAD_ERROR_SUCESS
        template_master_file = os.path.join(work_dir, template_manager.get_master_template_file_name(test_template_id))
        assert os.path.exists(template_master_file)
    finally:
        shutil.rmtree(work_dir)
        os.remove(tar_file)


@pytest.mark.templatemanager
def test_extract_template_tar_error(override_template_store_dir, test_template_id):

    tar_file = tempfile.mktemp()
    open(tar_file, 'a').close()

    work_dir = tempfile.mkdtemp()

    try:
        rc, message = template_manager.extract_template(work_dir, tar_file)
        assert rc == template_manager.UPLOAD_ERROR_BAD_TAR_FILE
    finally:
        shutil.rmtree(work_dir)
        if os.path.exists(tar_file):
            os.remove(tar_file)


class FileStorage:
    def save(self, target_dir):
        pass


@pytest.mark.templatemanager
def test_save_uploaded_template(override_template_store_dir, test_template_id, monkeypatch, mocker):

    template_id = test_template_id
    tar_file = "/tmp/{}".format(template_id)
    file_name = os.path.basename(tar_file)
    src_dir = os.path.join(override_template_store_dir, test_template_id, "")
    create_tar_file(tar_file, src_dir)

    # reset TEMPLATE_STORE_LOCATION to a new directory
    template_store_dir = tempfile.mkdtemp()
    monkeypatch.setattr(template_constants, 'TEMPLATE_STORE_LOCATION', template_store_dir)

    work_dir = tempfile.mkdtemp()
    try:
        mocker.patch.object(tempfile, "mkdtemp")
        tempfile.mkdtemp.return_value = work_dir

        shutil.copyfile(tar_file, os.path.join(work_dir, file_name))

        file_storage = FileStorage()

        template_manager.save_uploaded_template(file_name, file_storage)

        master_template_file = template_manager.get_master_template_file(template_id)
        assert (os.path.exists(master_template_file))
    finally:
        os.remove(tar_file)
        shutil.rmtree(template_store_dir)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)


@pytest.mark.templatemanager
def test_get_supported_products(override_template_store_dir, test_template_id):

    supported_products = template_manager.get_supported_products(test_template_id)
    assert supported_products is not None
    assert len(supported_products) > 0
    assert isinstance(supported_products[0], dict)

    supported_products = template_manager.get_supported_products(test_template_id, 0)
    assert supported_products is not None
    assert len(supported_products) > 0
    assert isinstance(supported_products[0], dict)


@pytest.mark.templatemanager
def test_get_supported_products_as_product_type_list(override_template_store_dir, test_template_id):

    supported_products = template_manager.get_supported_products_as_product_type_list(test_template_id)
    assert supported_products is not None
    assert len(supported_products) > 0
    assert isinstance(supported_products[0], str)


@pytest.mark.templatemanager
def test_override_template(monkeypatch):

    template_id = "abc"
    work_dir = tempfile.mkdtemp()

    template_store_dir = tempfile.mkdtemp()
    monkeypatch.setattr(template_constants, 'TEMPLATE_STORE_LOCATION', template_store_dir)
    target_dir = os.path.join(template_store_dir, template_id)
    os.mkdir(target_dir)

    try:
        assert template_manager.override_template(template_id, work_dir)
        assert os.path.exists(target_dir)
        assert not os.path.exists(work_dir)
    finally:
        shutil.rmtree(template_store_dir)


@pytest.mark.templatemanager
def test_cleanup_uploaded_template():

    work_dir = tempfile.mkdtemp()
    assert template_manager.cleanup_uploaded_template(work_dir)
    assert not os.path.exists(work_dir)
