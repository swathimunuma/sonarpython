import pytest
import logging
import subprocess

from mock import ANY

from components.dbscripts import DbConstants as dbC
from components.networkmodule import AcpNetworkDataModule
from components.scriptgenerator import ScriptGeneratorConstants as sgConstants
from components.scriptgenerator.vmwarehelper import VmwareDeployHelper, data_helper


@pytest.mark.cms
def test_resize_cpu(mocker):
    site_name = dbC.TEXASDATACENTER
    vm_type = dbC.CMS
    vm_name = "hmtxcms2_10.3.1.181"
    profile = 'profile2'
    cpu_size = AcpNetworkDataModule.cms_cpumap.get(profile)
    cmd = '{0} vm.change -vm {1} -c={2} -e cpuid.coresPerSocket={3}' \
        .format(sgConstants.GOVCBIN, vm_name, cpu_size[0], cpu_size[1])

    # mock
    logger = mocker.patch.object(logging, 'Logger')
    p = mocker.patch.object(subprocess, 'Popen')
    subprocess.Popen.return_value = p
    p.communicate.return_value = ('', 0)

    mocker.patch.object(data_helper, 'get_vcenter_hostname')
    data_helper.get_vcenter_hostname.return_value = 'hostname'

    mocker.patch.object(data_helper, 'get_govc_secure_status')
    data_helper.get_govc_secure_status.return_value = 'secure_status'

    mocker.patch.object(data_helper, 'get_vcenter_username')
    data_helper.get_vcenter_username.return_value = 'vcenter_username'

    mocker.patch.object(data_helper, 'get_vcenter_password')
    data_helper.get_vcenter_password.return_value = 'username'

    mocker.patch.object(data_helper, 'get_vcenter_datacenter_name')
    data_helper.get_vcenter_datacenter_name.return_value = 'data_center_name'

    mocker.patch.object(data_helper, 'get_vcenter_datastore')
    data_helper.get_vcenter_datastore.return_value = 'store'

    # call method
    VmwareDeployHelper.change_cpu_size(site_name, vm_type, vm_name, profile, logger)

    # verify
    subprocess.Popen.assert_called_with(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                        env=ANY)


@pytest.mark.cms
def test_resize_memory(mocker):
    site_name = dbC.TEXASDATACENTER
    vm_type = dbC.CMS
    vm_name = "hmtxcms2_10.3.1.181"
    profile = 'profile2'
    memory_size = AcpNetworkDataModule.cms_memorymap.get(profile)
    cmd = '{0} vm.change -vm {1} -m={2}' \
        .format(sgConstants.GOVCBIN, vm_name, memory_size[0], memory_size[1])

    # mock
    logger = mocker.patch.object(logging, 'Logger')
    p = mocker.patch.object(subprocess, 'Popen')
    subprocess.Popen.return_value = p
    p.communicate.return_value = ('', 0)

    mocker.patch.object(data_helper, 'get_vcenter_hostname')
    data_helper.get_vcenter_hostname.return_value = 'hostname'

    mocker.patch.object(data_helper, 'get_govc_secure_status')
    data_helper.get_govc_secure_status.return_value = 'secure_status'

    mocker.patch.object(data_helper, 'get_vcenter_username')
    data_helper.get_vcenter_username.return_value = 'vcenter_username'

    mocker.patch.object(data_helper, 'get_vcenter_password')
    data_helper.get_vcenter_password.return_value = 'username'

    mocker.patch.object(data_helper, 'get_vcenter_datacenter_name')
    data_helper.get_vcenter_datacenter_name.return_value = 'data_center_name'

    mocker.patch.object(data_helper, 'get_vcenter_datastore')
    data_helper.get_vcenter_datastore.return_value = 'store'

    # call method
    VmwareDeployHelper.change_memory_size(site_name, vm_type, vm_name, profile, logger)

    # verify
    subprocess.Popen.assert_called_with(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                        env=ANY)
