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

    @services('compute', 'network')
    def test_ssh_hormiga_ardilla(self):
        ardilla_ip = "83.49.3.137"
        hormiga_ip = "192.34.62.132"
        private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2WAjPP9bnYAPMSVeus5MXrEa8Ejzfek5mw9Tm5nBvdBRKnGn
Qibt19zzqkgU8a5bepaJ12RGNrWHk9CNvuBiKGcm3SMReDJRyvicJcfNAK2a56fY
sDg/PhovT5eUBH5F8/HUGu4YAIgBc4zsoAn/xVpKzEHl85lTPiWEw2uyQze5N8qp
R622OitwRX1XDBvaqA5Q3i6tZ0jMGLIbkaXb4Bz5/RBz3Tx6XTZbrurJyxMffZDz
2D/Qlxbmt/C1F/HhMt0N97sFAC6ibh7/uxOdCDMm73rkohWplTVtsqrBvvhftBX+
g3kDc+3zLdISA0JSEV0iVJth/V+T3ZPhj2XduQIDAQABAoIBAQCfQgcvNmtZzivT
Nuzbci+TpK/24Yu7cPbqeuUneBPwzEHbFd+T4M+aul+vHxZxJuwQuWAN9YJXrNHC
4yYmdWCU91YK6BlxdXRlf5VvPJ4eZBK8rEVeficfibGl34jrbdQ0cLWUcWIWaY6e
qN3oNss0PP3V/mXJ/kh1nKlTP4EgKsWDzv81e1HqRUhL6kODbgw2IMO9kinMLLQV
Ali527ZCb9P/azvEII17v86MZFy+XfR5M3Cw2pvPlar6lcL+9+maw1+2GLM3/mg6
hfZVVw2RauLc0Jeldfrc31otJcniN2dAPkPzrxSKHUTyU5lHmHMkHAiWzcEwlON0
8E+13mNNAoGBAP9IBci//uQLC7q/WlaFcZmIz0qCM6PQqJ02bwunLJqGp5/N1U3S
5JyMdOxZyFd454NNpVIgD3YvK/4Oxzptd5cb4GPmpgt9FzlFzkXXqjW1P6hR3EvG
n6VeZFox6vIzqyM/yqkqndDC3XJ9VTTaF5IbAMc52yNRrvghGXL7LT73AoGBANn8
zALAXcnJ9FU7pn1FzsMg5NBQ08ikPBs7m5XTMXlyzf/lj+pw7Dz5MzjEaCxjDq5r
sFrVWfwOQ1j3NrQ065WTx7PMwn9Wq4SZlekdV/QcCbMR+xEr4A0J8Fy1mi39QP9a
8dyUa+SXpONT0KyrExLFVG9Dr4eyW//6U6rSDqzPAoGAU0WpLV0DxlucDeTRkRui
fNTV2ZYzRiKQfgf9nS2BLT7zevtnsyUyEab3lQmMgowb6QbxAKMYqBKnJQ6pCnQe
6JndTnk0fNbnNnWA3eOF0FM5WqypUcaO2SC7V3ilDTCxiKQMdbZDGJAYMHqVytHB
kpVgYZyL0S+aBbK2XH12uu0CgYAk2qCDNpKkswgkANm9BDhYtQ76STAFE/81e3Zq
djI/HjHFucIDGORXyqnmRw51sqmgw4QlVzzHaIHqYKFXBjtuJnX06AFaFgUZff3i
U5uzIapiJAAWfxx6F9wTUIColdCPW4jYih9Tnm+6H0mAZ8vpuIL17LOYdYcoV+Id
VzYz8QKBgQDIIjNMt3MB1yod4rO1r1WCClsX1/miRnSdZTV3wubI/oIFrpQPgLOV
ynr92ZufXZ/AYrzoMrh1xnpjfYPnw0Qf5Q9otlIylXk6y+jd3URzIK/iRXKLqxPl
R2JgNXyB4mdphhb7F8++MaSoezyv4/sRQZ8BpWO/nEP+nEl5Hf0pSg==
-----END RSA PRIVATE KEY-----"""

        try:
            remote_client = self.get_remote_client(ardilla_ip,
                                                   private_key=private_key,
                                                   gateway_ip=hormiga_ip,
                                                   gateway_key=private_key)
            remote_client.exec_command('ls -la')
        except Exception:
            LOG.exception('ssh to server failed')
            self._log_console_output()
            raise
