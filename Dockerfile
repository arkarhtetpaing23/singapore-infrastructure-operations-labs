FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
ENV DEBIAN_FRONTEND=noninteractive
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d && chmod +x /usr/sbin/policy-rc.d \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3 iproute2 iputils-ping \
       curl dnsutils dnsmasq isc-dhcp-client tcpdump nftables frr nginx \
       openssh-server prometheus prometheus-alertmanager ca-certificates procps \
    && find /etc/ssh -name 'ssh_host_*' -delete \
    && rm -rf /var/lib/apt/lists/*
COPY runtime/ /lab/
CMD ["sleep", "infinity"]
