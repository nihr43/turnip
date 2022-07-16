# turnip

A (eventually) consistent, partition-tolerant layer-3 keepalived alternative.  Backed by etcd.

## motivation

This project exists to address two qualities that keepalived, CARP, and similar tools lack:

- consistency in the event of a network partition
- inter-network failover capability

Unlike keepalived and CARP, turnip operates at the IP layer, so participants can exist on seperate L3 networks.

An example of where this may be useful is to provide fault-tolerant access to kubernetes API servers running on /32 addresses in a pure-L3 network.  Such an implementation would allow us to keep our kubernetes masters in seperate L2 failure domains, while avoiding the shortcomings of naive DNS round-robin.

Another use-case is to provide a highly available unicast default gateway to vxlan networks.  For example, if we have vxlan vni 100 bridged to br100 on a number of linux hypervisors, the guests attached to that distributed bridge 'br100' likely need a route out to the internet.  turnip allows us to ensure a default gateway ip exists on at least one of those hypervisors' instances of 'br100' at all times.  If we happen to power off the hypervisor operating the current default gateway, turnip will ensure the IP gets brought back up somewhere else.

In both examples, an active routing protocol like bgp is required to propogate routes for the 'floating' IPs.

## implementation

In pursuit of simplicity, turnip simply uses a short control loop to 'watch' which etcd node is currently the cluster leader.  It is expected that etcd is running on localhost of each turnip node.  As a result, there is a short period (~10 seconds) after leader elections where an IP may exist in two places at once.  At this time, this is considered acceptable for the author's use-case.

## configuration

Provided is a systemd unit file.  Land this at `/lib/systemd/system/turnip.service`.  It references `/etc/default/turnip`.  Create this and populate the env vars:

```
TURNIP_IP=		# the IP to be failed over
TURNIP_NETMASK=		# the network mask
TURNIP_DEV=		# the network device
TURNIP_ID=		# the local node's etcd peering IP
```

If successful, systemd will show a node pick up the address:

```
~# systemctl status turnip
● turnip.service - Partition tolerant layer-3 IP failover
     Loaded: loaded (/lib/systemd/system/turnip.service; disabled; vendor preset: enabled)
     Active: active (running) since Fri 2022-07-15 22:08:16 CDT; 29s ago
   Main PID: 4041 (turnip)
      Tasks: 5 (limit: 9291)
     Memory: 27.0M
        CPU: 352ms
     CGroup: /system.slice/turnip.service
             └─4041 /usr/bin/python3 /usr/bin/turnip

Jul 15 22:08:16 apollolake-6e10 systemd[1]: Started Partition tolerant layer-3 IP failover.
Jul 15 22:08:27 apollolake-6e10 turnip[4041]: INFO:root:assuming address
```

## future work

Ideally (n) configured IP addresses would be hash-mapped accross all living nodes.

Its called 'turnip' because it 'turns over' IPs (sorta).
