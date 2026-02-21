#!/usr/bin/python3

__author__     = "Paolo Mantovani"
__copyright__  = "Copyright 2017, Columbia University, NY"
__credits__    = "Giuseppe Di Guglielmo"
__license__    = "DO NOT DISTRIBUTE!"
__maintainer__ = "Paolo Mantovani"
__email__      = "paolo@cs.columbia.edu"
__status__     = "Testing"

import sys

if len(sys.argv) != 2:
    print("Usage: ./srec2text.py <srec_file>")
    print("")
    print("  <srec_file> : Object in SREC format")
    print("")
    sys.exit(0)

try:
    fd = open(sys.argv[1], 'r')
except:
    print("Error: failed to open " + sys.argv[1])
    sys.exit(0)

# =====================================================
# Phase 1: Parse SREC records and store each byte
#          into byte_map indexed by absolute address.
# key = byte address (int), value = byte value (int)
# =====================================================
byte_map = {}

for line in fd:
    if not line.strip():
        continue

    entry = line.strip()
    s_type = int(entry[1])

    # Skip header, record count, and end records
    if s_type == 0 or s_type == 5 or s_type == 6:
        continue
    if s_type == 7 or s_type == 8 or s_type == 9:
        continue

    if s_type == 1:
        byte_cnt   = int(entry[2:4], 16) - 3   # 16-bit address: -2(addr) -1(cksum)
        data_start = 8
    elif s_type == 2:
        byte_cnt   = int(entry[2:4], 16) - 4   # 24-bit address
        data_start = 10
    elif s_type == 3:
        byte_cnt   = int(entry[2:4], 16) - 5   # 32-bit address
        data_start = 12
    else:
        print("Error: SREC decoding error -> \"" + entry + "\"")
        sys.exit(0)

    address = int(entry[4:data_start], 16)

    # Store each byte into byte_map at its absolute address
    for i in range(byte_cnt):
        byte_val = int(entry[data_start + i*2 : data_start + i*2 + 2], 16)
        byte_map[address + i] = byte_val

fd.close()

# =====================================================
# Phase 2: Read byte_map in address order.
#          Group every 4 bytes into a 32-bit word,
#          swap from little-endian to big-endian,
#          and print as text. Fill gaps with 0xFF.
# =====================================================
if not byte_map:
    print("Error: no data found in SREC file")
    sys.exit(0)

min_addr = min(byte_map.keys())
max_addr = max(byte_map.keys())

# Align start address to 4-byte boundary
start_addr = min_addr & ~0x3

for addr in range(start_addr, max_addr + 1, 4):
    # Fetch 4 bytes; fill missing addresses (gaps) with 0xFF
    b0 = byte_map.get(addr + 0, 0xFF)
    b1 = byte_map.get(addr + 1, 0xFF)
    b2 = byte_map.get(addr + 2, 0xFF)
    b3 = byte_map.get(addr + 3, 0xFF)

    # Byte swap: little-endian (b0..b3) -> big-endian (b3..b0)
    word = (b3 << 24) | (b2 << 16) | (b1 << 8) | b0
    print(f"{hex(addr)} 0x{word:08X}")

