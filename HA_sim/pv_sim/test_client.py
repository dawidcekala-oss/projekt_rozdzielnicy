#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Szybki test symulatora SUN2000 bez Home Assistant (czysty stdlib).

Uzycie: python test_client.py [host] [port]
"""
import socket
import struct
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 502

_tid = 0


def regs(sock, addr, count):
    global _tid
    _tid += 1
    req = struct.pack(">HHHBBHH", _tid, 0, 6, 1, 3, addr, count)
    sock.sendall(req)
    hdr = b""
    while len(hdr) < 9:
        hdr += sock.recv(9 - len(hdr))
    tid, pid, length, uid, fc, bc = struct.unpack(">HHHBBB", hdr)
    if fc & 0x80:
        raise RuntimeError(f"wyjatek Modbus @{addr}: kod {bc}")
    body = b""
    while len(body) < bc:
        body += sock.recv(bc - len(body))
    return list(struct.unpack(f">{bc // 2}H", body))


def as_str(r):
    b = b"".join(bytes([x >> 8, x & 0xFF]) for x in r)
    return b.split(b"\x00")[0].decode("ascii", "ignore")


def as_u32(r):
    return (r[0] << 16) | r[1]


def as_i32(r):
    v = as_u32(r)
    return v - (1 << 32) if v >= 1 << 31 else v


s = socket.create_connection((HOST, PORT), timeout=5)

print("Model:         ", as_str(regs(s, 30000, 15)))
print("S/N:           ", as_str(regs(s, 30015, 10)))
print("Moc znam.:     ", as_u32(regs(s, 30073, 2)), "W")
print("Liczba stringow:", regs(s, 30071, 1)[0])
print("Moc DC:        ", as_i32(regs(s, 32064, 2)), "W")
print("Moc czynna:    ", as_i32(regs(s, 32080, 2)), "W")
print("PV1:           ", regs(s, 32016, 1)[0] / 10, "V /",
      regs(s, 32017, 1)[0] / 100, "A")
print("Napiecie L1:   ", regs(s, 32069, 1)[0] / 10, "V")
print("Czestotliwosc: ", regs(s, 32085, 1)[0] / 100, "Hz")
print("Sprawnosc:     ", regs(s, 32086, 1)[0] / 100, "%")
print("Temperatura:   ", regs(s, 32087, 1)[0] / 10, "C")
print("Status (32089):", regs(s, 32089, 1)[0], "(512=On-grid, 2=Standby)")
print("Energia dnia:  ", as_u32(regs(s, 32114, 2)) / 100, "kWh")
print("Energia calk.: ", as_u32(regs(s, 32106, 2)) / 100, "kWh")
print("Meter status:  ", regs(s, 37100, 1)[0], "| moc licznika:",
      as_i32(regs(s, 37113, 2)), "W (+eksport)")

# test odczytu blokowego jak w huawei_solar (duze paczki rejestrow)
batch = regs(s, 32000, 116)
assert len(batch) == 116
print("Odczyt blokowy 32000-32115: OK (116 rejestrow)")

s.close()
print("\nOK - symulator odpowiada poprawnie.")
