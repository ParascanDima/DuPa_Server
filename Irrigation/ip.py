from netifaces import interfaces, ifaddresses, AF_INET

def Get_IP():
    public_ips = []
    for iface in interfaces():
        # list of ipv4 addrinfo dicts
        ipv4s = ifaddresses(iface).get(AF_INET, [])
        for entry in ipv4s:
            addr = entry.get('addr')
            if not addr:
                continue
            if not (iface.startswith('lo') or addr.startswith('127.')):
                public_ips.append(addr)
                
    return public_ips

