__author__ = 'Albert'
'''
Scenario:
A launched VM should get an ip address and routing table entries from DHCP. And
it should be able to metadata service.

Pre-requisites:
1 tenant
1 network
2 VMs

Steps:
1. create a network
2. launch 2 VMs
3. verify that 2 VMs can ping each other

Expected results:
ping works
'''


from tempest.test import services
from tempest import config
from tempest.openstack.common import log as logging
from tempest.scenario.midokura.midotools import scenario
import itertools
import time
from pprint import pprint

CONF = config.CONF
LOG = logging.getLogger(__name__)
CIDR1 = "10.10.1.0/24"


class TestNetworkBasicIntraVMConnectivity(scenario.TestScenario):

    @classmethod
    def setUpClass(cls):
        super(TestNetworkBasicIntraVMConnectivity, cls).setUpClass()
        cls.check_preconditions()

    def setUp(self):
        super(TestNetworkBasicIntraVMConnectivity, self).setUp()
        self.security_group = \
            self._create_security_group_neutron(tenant_id=self.tenant_id)
        self._scenario_conf()
        self.custom_scenario(self.scenario)

    def _scenario_conf(self):
        serverB = {
            'floating_ip': False,
        }
        subnetA = {
            "network_id": None,
            "ip_version": 4,
            "cidr": CIDR1,
            "allocation_pools": None
        }
        networkA = {
            'subnets': [subnetA],
            'servers': [serverB, serverB],
        }
        tenantA = {
            'networks': [networkA],
            'tenant_id': None,
            'type': 'default',
            'hasgateway': True
        }
        self.scenario = {
            'tenants': [tenantA],
        }

    # def _ssh_through_gateway(self, origin, destination):
    #     try:
    #         self.
    #         result = ssh_client.exec_command(
    #             'ssh -A -t -o UserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no cirros@%s' % destination[0])
    #         pprint(result)
    #     except Exception as inst:
    #         LOG.info(inst.args)
    #         raise

    @services('compute', 'network')
    def test_network_basic_inter_vmssh(self):
        ap_details = self.access_point.keys()[0]
        networks = ap_details.networks
        ip_pk = []
        for server in self.servers:
            #servers should only have 1 network
            name = server.networks.keys()[0]
            if any(i in networks.keys() for i in server.networks.keys()):
                remote_ip = server.networks[name][0]
                pk = self.servers[server].private_key
                ip_pk.append((remote_ip, pk))
            else:
                LOG.info("FAIL - No ip connectivity to the server ip: %s" % server.networks[name][0])
                raise Exception("FAIL - No ip for this network : %s"
                            % server.networks)
        for pair in itertools.permutations(ip_pk):
            LOG.info("Checking ssh between %s %s" % (pair[0][0], pair[1][0]))
            # self._ssh_through_gateway(pair[0],pair[1])
            try:
                remote_client = self.get_remote_client(pair[0][0],
                                                       gateway_ip=self.get_gateway_ip,
                                                       gateway_key=self.get_gateway_key)
                remote_client.exec_command('ls -la')
            except Exception:
                LOG.exception('ssh to server failed')
                self._log_console_output()
                raise