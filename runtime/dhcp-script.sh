#!/bin/sh
# Optional BusyBox/GNS3 client script; automated run uses ISC dhclient instead.
case "$1" in
  deconfig) ip addr flush dev "$interface" ;;
  bound|renew)
    ip addr flush dev "$interface"
    ip addr add "$ip/24" dev "$interface"
    ip route replace default via "${router%% *}" dev "$interface"
    printf 'nameserver %s\n' "${dns%% *}" > /etc/resolv.conf
    ;;
esac
