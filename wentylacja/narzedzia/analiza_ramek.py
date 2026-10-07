import re, sys
from collections import Counter, OrderedDict
p = r"C:\Users\Lenovo\Desktop\AMPERE_POINT\wentylacja\test_com_manual\log_sondy.txt"
h = open(p, encoding='utf-8', errors='replace').read()
start = int(sys.argv[1]) if len(sys.argv) > 1 else h.rfind('=== SONDA COM-MANUAL v2')
ses = h[start:] if start >= 0 else h
raw = []
for m in re.finditer(r'\[RX\]\s*((?:[0-9A-F]{2}\s+)+)', ses):
    raw += m.group(1).split()
b = [int(x, 16) for x in raw]
ramki, i = [], 0
while i < len(b) - 6:
    if b[i] == 0x7E and b[i+1] == 0x7E:
        dl = b[i+5]; total = 6 + dl
        if total <= 64 and i + total <= len(b):
            fr = b[i:i+total]
            x = 0
            for v in fr[:-1]: x ^= v
            ok = (x == fr[-1])
            ramki.append((' '.join(f'{v:02X}' for v in fr), ok))
            i += total; continue
    i += 1
cnt = Counter(r for r, ok in ramki)
uniq = list(OrderedDict.fromkeys(r for r, ok in ramki))
sumy = {r: ok for r, ok in ramki}
print(f"pelnych ramek: {len(ramki)}, wzorcow: {len(uniq)}")
for u in uniq:
    print(f"[x{cnt[u]}][suma {'OK' if sumy[u] else 'ZLA'}] {u}")
if ramki:
    print("OFFSET_KONCA:", len(h))
    print("OSTATNIA:", ramki[-1][0])
