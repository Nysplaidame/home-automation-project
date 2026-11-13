#!/bin/sh
# Scoped GL-MT6000 Zen/Openreach repair. Requires existing working PPPoE on eth1.
# Back up network/firewall/dhcp and arm a rollback before running this script.
set -eu
[ "$(uci -q get network.wan.proto)" = pppoe ]
[ "$(uci -q get network.wan.device)" = eth1 ]
mgmt_vlan=''
for section in $(uci show network | sed -n 's/^network\.\([^=]*\)=bridge-vlan$/\1/p'); do
    [ "$(uci -q get network.$section.vlan)" != 10 ] || mgmt_vlan="$section"
done
[ -n "$mgmt_vlan" ]

# One explicit DHCPv6 client over the PPPoE logical interface.
uci set network.wan.ipv6='1'
uci set network.wan6.device='@wan'
uci set network.wan6.proto='dhcpv6'
uci set network.wan6.reqaddress='try'
uci set network.wan6.reqprefix='auto'

# Cloud devices have internet, but no access to internal zones or router admin.
uci -q del_list "network.$mgmt_vlan.ports=lan2:u*" || true
uci set network.cloud_iot_vlan='bridge-vlan'
uci set network.cloud_iot_vlan.device='br-lan'
uci set network.cloud_iot_vlan.vlan='55'
uci set network.cloud_iot_vlan.local='1'
uci -q delete network.cloud_iot_vlan.ports || true
uci add_list network.cloud_iot_vlan.ports='lan2:u*'
uci set network.cloud_iot='interface'
uci set network.cloud_iot.proto='static'
uci set network.cloud_iot.device='br-lan.55'
uci set network.cloud_iot.ipaddr='192.168.55.1'
uci set network.cloud_iot.netmask='255.255.255.0'

uci set dhcp.cloud_iot='dhcp'
uci set dhcp.cloud_iot.interface='cloud_iot'
uci set dhcp.cloud_iot.start='100'
uci set dhcp.cloud_iot.limit='50'
uci set dhcp.cloud_iot.leasetime='12h'
uci set dhcp.cloud_iot.dhcpv4='server'
uci -q delete dhcp.cloud_iot.dhcp_option || true
uci add_list dhcp.cloud_iot.dhcp_option='6,192.168.55.1'
uci add_list dhcp.cloud_iot.dhcp_option='42,192.168.55.1'
uci set dhcp.hive_hub='host'
uci set dhcp.hive_hub.name='hive-hub'
uci set dhcp.hive_hub.mac='00:1c:2b:b1:02:20'
uci set dhcp.hive_hub.ip='192.168.55.10'

uci set firewall.cloud_iot='zone'
uci set firewall.cloud_iot.name='cloud_iot'
uci set firewall.cloud_iot.network='cloud_iot'
uci set firewall.cloud_iot.input='REJECT'
uci set firewall.cloud_iot.output='ACCEPT'
uci set firewall.cloud_iot.forward='REJECT'
for spec in 'dhcp:67:udp' 'dns:53:tcp udp' 'ntp:123:udp'; do
    name=${spec%%:*}; rest=${spec#*:}; port=${rest%%:*}; proto=${rest#*:}
    uci set "firewall.cloud_iot_$name=rule"
    label="Cloud-IoT-Router-$name"
    [ "$name" != dhcp ] || label="Allow DHCP input cloud_iot"
    [ "$name" != dns ] || label="Allow DNS input cloud_iot"
    uci set "firewall.cloud_iot_$name.name=$label"
    uci set "firewall.cloud_iot_$name.src=cloud_iot"
    uci set "firewall.cloud_iot_$name.dest_port=$port"
    uci set "firewall.cloud_iot_$name.proto=$proto"
    uci set "firewall.cloud_iot_$name.family=ipv4"
    uci set "firewall.cloud_iot_$name.target=ACCEPT"
done
# Keep the project's router-DNS policy, before the broad internet forwarding.
uci set firewall.cloud_iot_dns_bypass='rule'
uci set firewall.cloud_iot_dns_bypass.name='Cloud-IoT-Block-External-DNS'
uci set firewall.cloud_iot_dns_bypass.src='cloud_iot'
uci set firewall.cloud_iot_dns_bypass.dest='wan'
uci set firewall.cloud_iot_dns_bypass.dest_port='53 853'
uci set firewall.cloud_iot_dns_bypass.proto='tcp udp'
uci set firewall.cloud_iot_dns_bypass.target='REJECT'
uci set firewall.cloud_iot_wan='forwarding'
uci set firewall.cloud_iot_wan.src='cloud_iot'
uci set firewall.cloud_iot_wan.dest='wan'

uci set firewall.zen_dhcpv6='rule'
uci set firewall.zen_dhcpv6.name='Allow-DHCPv6-WAN'
uci set firewall.zen_dhcpv6.src='wan'
uci set firewall.zen_dhcpv6.src_port='547'
uci set firewall.zen_dhcpv6.dest_port='546'
uci set firewall.zen_dhcpv6.proto='udp'
uci set firewall.zen_dhcpv6.family='ipv6'
uci set firewall.zen_dhcpv6.target='ACCEPT'
uci set firewall.zen_icmpv6_input='rule'
uci set firewall.zen_icmpv6_input.name='Allow-ICMPv6-WAN-Input'
uci set firewall.zen_icmpv6_input.src='wan'
uci set firewall.zen_icmpv6_input.proto='icmp'
uci set firewall.zen_icmpv6_input.family='ipv6'
uci set firewall.zen_icmpv6_input.icmp_type='echo-request echo-reply destination-unreachable packet-too-big time-exceeded bad-header unknown-header-type router-solicitation router-advertisement neighbour-solicitation neighbour-advertisement'
uci set firewall.zen_icmpv6_input.limit='1000/sec'
uci set firewall.zen_icmpv6_input.target='ACCEPT'
uci set firewall.zen_icmpv6_forward='rule'
uci set firewall.zen_icmpv6_forward.name='Allow-ICMPv6-WAN-Forward'
uci set firewall.zen_icmpv6_forward.src='wan'
uci set firewall.zen_icmpv6_forward.dest='*'
uci set firewall.zen_icmpv6_forward.proto='icmp'
uci set firewall.zen_icmpv6_forward.family='ipv6'
uci set firewall.zen_icmpv6_forward.icmp_type='destination-unreachable packet-too-big time-exceeded bad-header unknown-header-type'
uci set firewall.zen_icmpv6_forward.limit='1000/sec'
uci set firewall.zen_icmpv6_forward.target='ACCEPT'

fw4 check
uci commit network
uci commit dhcp
uci commit firewall
/etc/init.d/network reload
/etc/init.d/firewall reload
/etc/init.d/dnsmasq restart
