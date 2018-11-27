# Copyright 2018 ARICENT HOLDINGS LUXEMBOURG SARL and Cable Television
# Laboratories, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os

from snaps_k8s.common.consts import consts


"""
Utilities for parsing the k8s deployment configuration
"""

logger = logging.getLogger('config_utils')


def get_k8s_dict(k8s_conf):
    """
    Returns a dict of proxy settings
    :param k8s_conf: the config dict
    :return: a dict containing all of the proxy settings
    :raises: Exception if not exists
    """
    return k8s_conf[consts.K8S_KEY]


def get_proxy_dict(k8s_conf):
    """
    Returns a dict of proxy settings
    :param k8s_conf: the config dict
    :return: a dict containing all of the proxy settings
    :raises: Exception if not exists
    """
    return get_k8s_dict(k8s_conf)[consts.PROXIES_KEY]


def get_networks(k8s_conf):
    """
    Returns a list of all configured networks
    :param k8s_conf: the config dict
    :return: a list containing all of the network settings
    :raises: Exception if not exists
    """
    return get_k8s_dict(k8s_conf)[consts.NETWORKS_KEY]


def get_multus_network(k8s_conf):
    networks = get_networks(k8s_conf)
    for network in networks:
        if consts.MULTUS_NET_KEY in network:
            return network[consts.MULTUS_NET_KEY]


def get_multus_elems(k8s_conf, key):
    multus_cfgs = get_multus_network(k8s_conf)
    for multus_cfg in multus_cfgs:
        if key in multus_cfg:
            return multus_cfg.get(key)


def get_multus_net_elems(k8s_conf):
    return get_multus_elems(k8s_conf, consts.MULTUS_CNI_KEY)


def get_multus_cni_cfgs(k8s_conf):
    return get_multus_elems(k8s_conf, consts.MULTUS_CNI_CONFIG_KEY)


def get_multus_cni_flannel_cfgs(k8s_conf):
    cni_elems = get_multus_elems(k8s_conf, consts.MULTUS_CNI_CONFIG_KEY)
    for cni_elem in cni_elems:
        if consts.FLANNEL_NET_TYPE in cni_elem:
            return cni_elem[consts.FLANNEL_NET_TYPE]
    return list()


def get_multus_cni_macvlan_cfgs(k8s_conf):
    cni_elems = get_multus_elems(k8s_conf, consts.MULTUS_CNI_CONFIG_KEY)
    for cni_elem in cni_elems:
        if consts.MACVLAN_NET_TYPE in cni_elem:
            return cni_elem[consts.MACVLAN_NET_TYPE]
    return list()


def get_multus_cni_sriov_cfgs(k8s_conf):
    cni_elems = get_multus_elems(k8s_conf, consts.MULTUS_CNI_CONFIG_KEY)
    for cni_elem in cni_elems:
        if consts.SRIOV_NET_TYPE in cni_elem:
            return cni_elem[consts.SRIOV_NET_TYPE]
    return list()


def get_multus_cni_weave_cfgs(k8s_conf):
    cni_elems = get_multus_elems(k8s_conf, consts.MULTUS_CNI_CONFIG_KEY)
    for cni_elem in cni_elems:
        if consts.WEAVE_NET_TYPE in cni_elem:
            return cni_elem[consts.WEAVE_NET_TYPE]
    return list()


def is_multus_cni_enabled(k8s_conf):
    """
    This function is used to get multus cni value
    """
    sriov_cni = False
    flannel_cni = False
    weave_cni = False
    macvlan_cni = False
    multus_cni = get_multus_net_elems(k8s_conf)
    for cni in multus_cni:
        if consts.SRIOV_TYPE == cni:
            sriov_cni = True
        elif consts.FLANNEL_TYPE == cni:
            flannel_cni = True
        elif consts.WEAVE_TYPE == cni:
            weave_cni = True
        elif consts.MACVLAN_TYPE == cni:
            macvlan_cni = True
    return sriov_cni or flannel_cni or weave_cni or macvlan_cni


def get_default_network(k8s_conf):
    networks = get_networks(k8s_conf)
    for network in networks:
        if consts.DFLT_NET_KEY in network:
                return network[consts.DFLT_NET_KEY]


def get_service_subnet(k8s_conf):
    default_network = get_default_network(k8s_conf)
    if default_network:
        return default_network[consts.SRVC_SUB_KEY]


def get_networking_plugin(k8s_conf):
    default_network = get_default_network(k8s_conf)
    if default_network:
        return default_network[consts.NET_PLUGIN_KEY]


def get_pod_subnet(k8s_conf):
    default_network = get_default_network(k8s_conf)
    if default_network:
        return default_network[consts.POD_SUB_KEY]


def get_version(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.K8_VER_KEY]


def get_ha_config(k8s_conf):
    return get_k8s_dict(k8s_conf).get(consts.HA_CONFIG_KEY)


def get_ha_lb_ips(k8s_conf):
    out = list()
    ha_configs = get_ha_config(k8s_conf)
    if ha_configs:
        for ha_config in ha_configs:
            out.append(ha_config[consts.HA_API_EXT_LB_KEY][consts.IP_KEY])
    return out


def get_node_configs(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.NODE_CONF_KEY]


def get_hostname_ips_dict(k8s_conf):
    out = dict()
    node_confs = get_node_configs(k8s_conf)
    for node_conf in node_confs:
        host_conf = node_conf[consts.HOST_KEY]
        out[host_conf[consts.HOSTNAME_KEY]] = host_conf[consts.IP_KEY]
    return out


def get_host_reg_port_dict(k8s_conf):
    """
    Returns a dict object where the key contains the node hostname and the
    value contains the registry port value
    :param k8s_conf: the configuration dict
    :return: a dict
    """
    out = {}
    for node_conf in get_node_configs(k8s_conf):
        host_conf = node_conf[consts.HOST_KEY]
        out[host_conf[consts.HOSTNAME_KEY]] = host_conf[consts.REG_PORT_KEY]
    return out


def get_host_ips(k8s_conf):
    out = list()
    node_confs = get_k8s_dict(k8s_conf)[consts.NODE_CONF_KEY]
    for node_conf in node_confs:
        host_conf = node_conf[consts.HOST_KEY]
        out.append(host_conf[consts.IP_KEY])
    return out


def get_hosts(k8s_conf):
    out = list()
    node_confs = get_k8s_dict(k8s_conf)[consts.NODE_CONF_KEY]
    for node_conf in node_confs:
        host_conf = node_conf[consts.HOST_KEY]
        out.append(host_conf[consts.HOSTNAME_KEY])
    return out


def get_basic_auth(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.BASIC_AUTH_KEY]


def get_project_name(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.PROJECT_NAME_KEY]


def get_artifact_dir(k8s_conf):
    directory = get_k8s_dict(k8s_conf).get(consts.ARTIFACT_DIR_KEY, '/tmp')
    return os.path.expanduser(directory)


def get_project_artifact_dir(k8s_conf):
    directory = get_artifact_dir(k8s_conf)
    project_name = get_project_name(k8s_conf)
    return "{}/{}/{}".format(directory, consts.PROJ_DIR_NAME, project_name)


def get_kubespray_dir(k8s_conf):
    directory = get_artifact_dir(k8s_conf)
    return "{}/{}".format(directory, consts.KUBESPRAY_FOLDER_NAME)


def get_docker_repo(k8s_conf):
    return get_k8s_dict(k8s_conf).get(consts.DOCKER_REPO_KEY)


def get_git_branch(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.GIT_BRANCH_KEY]


def get_persis_vol(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.PERSIS_VOL_KEY]


def get_ceph_vol(k8s_conf):
    persist_vol = get_k8s_dict(k8s_conf)[consts.PERSIS_VOL_KEY]
    return persist_vol.get(consts.CEPH_VOLUME_KEY)


def get_ceph_hosts(k8s_conf):
    persist_vol = get_k8s_dict(k8s_conf)[consts.PERSIS_VOL_KEY]
    ceph_vol = persist_vol.get(consts.CEPH_VOLUME_KEY)

    out = list()
    if ceph_vol:
        for ceph_host in ceph_vol:
            if consts.HOST_KEY in ceph_host:
                out.append(ceph_host[consts.HOST_KEY])
    return out


def get_ceph_hosts_info(k8s_conf):
    """
    Returns a list of tuple 3 of configured Ceph control hosts where
    index 0 is the hostname, 1 is the IP, and 2 is the type value
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_hosts(k8s_conf)
    for ceph_host in ceph_hosts:
        out.append((ceph_host[consts.HOSTNAME_KEY],
                    ceph_host[consts.IP_KEY],
                    ceph_host[consts.NODE_TYPE_KEY]))
    return out


def get_ceph_ctrls(k8s_conf):
    """
    Returns a list of the configured Ceph control hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_hosts(k8s_conf)
    for ceph_host in ceph_hosts:
        if ceph_host[consts.NODE_TYPE_KEY] == consts.CEPH_CTRL_TYPE:
            out.append(ceph_host)
    return out


def get_ceph_ctrls_info(k8s_conf):
    """
    Returns a list of tuple 3 of configured Ceph control hosts where
    index 0 is the hostname, 1 is the IP, and 2 is the type value
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_ctrls(k8s_conf)
    for ceph_host in ceph_hosts:
        out.append((ceph_host[consts.HOSTNAME_KEY],
                    ceph_host[consts.IP_KEY],
                    ceph_host[consts.NODE_TYPE_KEY]))
    return out


def get_ceph_osds(k8s_conf):
    """
    Returns a list of the configured Ceph control hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_hosts(k8s_conf)
    for ceph_host in ceph_hosts:
        if ceph_host[consts.NODE_TYPE_KEY] == consts.CEPH_OSD_TYPE:
            out.append(ceph_host)
    return out


def get_ceph_osds_info(k8s_conf):
    """
    Returns a list of tuple 3 of configured Ceph OSD hosts where
    index 0 is the hostname, 1 is the IP, and 2 is the type value
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_osds(k8s_conf)
    for ceph_host in ceph_hosts:
        out.append((ceph_host[consts.HOSTNAME_KEY],
                    ceph_host[consts.IP_KEY],
                    ceph_host[consts.NODE_TYPE_KEY]))
    return out


def get_ceph_osd_ips(k8s_conf):
    """
    Returns a list of IPs of configured Ceph OSD hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3s
    """
    out = list()
    ceph_hosts = get_ceph_osds(k8s_conf)
    for ceph_host in ceph_hosts:
        out.append((ceph_host[consts.HOSTNAME_KEY],
                    ceph_host[consts.IP_KEY],
                    ceph_host[consts.NODE_TYPE_KEY]))
    return out


def get_host_vol(k8s_conf):
    persist_vol = get_k8s_dict(k8s_conf)[consts.PERSIS_VOL_KEY]
    return persist_vol.get(consts.HOST_VOL_KEY)


def get_persist_vol_claims(k8s_conf):
    out = list()
    persist_vols = get_host_vol(k8s_conf)
    for persist_vol in persist_vols:
        if consts.CLAIM_PARAMS_KEY in persist_vol:
            out.append(persist_vol[consts.CLAIM_PARAMS_KEY])
    return out


def get_first_master_host(k8s_conf):
    """
    Returns a tuple 2 where 0 is the hostname and 1 is the IP of the first
    master host found in the config
    # TODO/FIXME - This will probably need to be updated for getting HA working
    :param k8s_conf: the configuration dict
    :return: a tuple 2 hostname, ip of the first master host
    """
    node_confs = get_node_configs(k8s_conf)
    for node_conf in node_confs:
        node = node_conf[consts.HOST_KEY]
        if node[consts.NODE_TYPE_KEY] == 'master':
            return node[consts.HOSTNAME_KEY], node[consts.IP_KEY]


def get_nodes_ip_name_type(k8s_conf):
    """
    Returns a list of tuple 3 where 0 is the hostname and 1 is the IP and 2 is
    the type of all configured hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3 - hostname, ip, type
    """
    out = list()
    node_confs = get_node_configs(k8s_conf)
    for node_conf in node_confs:
        node = node_conf[consts.HOST_KEY]
        out.append((node[consts.HOSTNAME_KEY], node[consts.IP_KEY],
                    node[consts.NODE_TYPE_KEY]))
    return out


def get_master_nodes_ip_name_type(k8s_conf):
    """
    Returns a list of tuple 3 where 0 is the hostname and 1 is the IP and 2 is
    the type of all configured master hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3 - hostname, ip, type
    """
    out = list()
    node_tuple_3 = get_nodes_ip_name_type(k8s_conf)
    for hostname, ip, node_type in node_tuple_3:
        if node_type == consts.NODE_TYPE_MASTER:
            out.append((hostname, ip, node_type))
    return out


def get_master_node_ips(k8s_conf):
    """
    Returns a list IP addresses to all configured master hosts
    :param k8s_conf: the configuration dict
    :return: a list IPs
    """
    out = list()
    node_tuple_3 = get_master_nodes_ip_name_type(k8s_conf)
    for hostname, ip, node_type in node_tuple_3:
        out.append(ip)
    return out


def get_minion_nodes_ip_name_type(k8s_conf):
    """
    Returns a list of tuple 3 where 0 is the hostname and 1 is the IP and 2 is
    the type of all configured minion hosts
    :param k8s_conf: the configuration dict
    :return: a list of tuple 3 - hostname, ip, type
    """
    out = list()
    node_tuple_3 = get_nodes_ip_name_type(k8s_conf)
    for hostname, ip, node_type in node_tuple_3:
        if node_type == consts.NODE_TYPE_MINION:
            out.append((hostname, ip, node_type))
    return out


def get_minion_node_ips(k8s_conf):
    """
    Returns a list IP addresses to all configured minion hosts
    :param k8s_conf: the configuration dict
    :return: a list IPs
    """
    out = list()
    node_tuple_3 = get_minion_nodes_ip_name_type(k8s_conf)
    for hostname, ip, node_type in node_tuple_3:
        out.append(ip)
    return out


def is_logging_enabled(k8s_conf):
    """
    Returns T/F based on the kubernetes.enable_logging value
    :param k8s_conf: the configuration dict
    :return: T/F
    """
    value = get_k8s_dict(k8s_conf).get(consts.ENABLE_LOG_KEY, False)
    return bool_val(value)


def get_log_level(k8s_conf):
    return get_k8s_dict(k8s_conf)[consts.LOG_LEVEL_KEY]


def get_logging_port(k8s_conf):
    return str(get_k8s_dict(k8s_conf)[consts.LOG_PORT_KEY])


def is_cpu_alloc(k8s_conf):
    """
    Returns T/F based on the kubernetes.enable_logging value
    :param k8s_conf: the configuration dict
    :return: T/F
    """
    value = get_k8s_dict(k8s_conf).get(consts.CPU_ALLOC_KEY, False)
    return bool_val(value)


def is_metrics_server_enabled(k8s_conf):
    """
    Returns T/F based on the kubernetes.enable_logging value
    :param k8s_conf: the configuration dict
    :return: T/F
    """
    value = get_k8s_dict(k8s_conf).get(consts.METRICS_SERVER_KEY, False)
    return bool_val(value)


def bool_val(value):
    if not value:
        return False
    elif isinstance(value, str):
        if value.upper() == 'false'.upper() or value.upper() == 'no'.upper():
            return False
        if value.upper() == 'true'.upper() or value.upper() == 'yes'.upper():
            return True
    elif isinstance(value, bool):
        return value
    else:
        return False