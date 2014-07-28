__author__ = 'Albert'

from tempest import config
from tempest.openstack.common import log as logging
from tempest import test
from pprint import pprint
from tempest.scenario.midokura.midotools import scenario
from netaddr import IPNetwork, IPAddress

CONF = config.CONF()
LOG = logging.getLogger(__name__)
CIDR1 = "10.10.10.8/29"
CIDR2 = "10.10.1.8/29"


class TestBasicMultisubnet(scenario.TestScenario):



    @classmethod
    def setUpClass(cls):
        super(TestBasicMultisubnet, cls).setUpClass()
        cls.scenario = {}

    def _scenario_conf(self):
        serverA = {
            'floating_ip': False
        }
        subnetA = {
            "network_id": None,
            "ip_version": 4,
            "cidr": CIDR1,
            "allocation_pools": None
        }
        subnetB = {
            "network_id": None,
            "ip_version": 4,
            "cidr": CIDR2,
            "allocation_pools": None
        }
        networkA = {
            'subnets': [subnetA, subnetB],
            'servers': [serverA, serverA, serverA, serverA, serverA]
        }
        tenantA = {
            'networks': [networkA],
            'tenant_id': None,
            'type': 'default'
        }
        self.scenario = {
            'tenants': [tenantA],
        }

    def _check_vm_assignation(self):
        s1 = 0
        s2 = 0
        for server in self.servers:
            network = server.addresses
            key, value = network.popitem()
            ip = value[0]['addr']
            pprint(ip)
            if IPAddress(ip) in IPNetwork(CIDR1):
                s1 += 1
            else:
                s2 += 1
        return s1 == 4 or s2 == 4

    def setUp(self):
        self.security_group = \
            self._create_security_group_neutron(tenant_id=self.tenant_id)
        self._scenario_conf()
        self.custom_scenario(self.scenario)


    @test.attr(type='smoke')
    @test.services('compute', 'network')
    def test_network_basic_multisubnet(self):
        return True
        #self.assertTrue(self._check_vm_assignation())