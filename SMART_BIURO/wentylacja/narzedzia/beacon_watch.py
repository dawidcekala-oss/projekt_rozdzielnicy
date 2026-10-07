import socket, time, sys
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 4210))
s.settimeout(2)
seen = set()
while True:
    try:
        data, addr = s.recvfrom(256)
        msg = data.decode('utf-8', 'replace').strip()
        if addr[0] not in seen:
            seen.add(addr[0])
            print(f"SONDA ONLINE: {addr[0]} ({msg})", flush=True)
    except socket.timeout:
        pass
