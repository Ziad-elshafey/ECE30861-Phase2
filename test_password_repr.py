#!/usr/bin/env python3
"""Test different password representations."""

# From the OpenAPI spec - the actual required password
spec_password = 'correcthorsebatterystaple123(!__+@**(A\'"`);DROP TABLE artifacts;'

print("Spec password:")
print(f"  repr: {repr(spec_password)}")
print(f"  len: {len(spec_password)}")
print(f"  bytes: {spec_password.encode('utf-8')}")
print()

# What we have in init_db.py as a raw string
raw_password = r"correcthorsebatterystaple123(!__+@**(A'\"`);DROP TABLE artifacts;"

print("Raw string password:")
print(f"  repr: {repr(raw_password)}")
print(f"  len: {len(raw_password)}")
print(f"  bytes: {raw_password.encode('utf-8')}")
print()

print(f"Are they equal? {raw_password == spec_password}")
print()

# Character by character comparison
if raw_password != spec_password:
    print("Character-by-character diff:")
    for i, (c1, c2) in enumerate(zip(spec_password, raw_password)):
        if c1 != c2:
            print(f"  Position {i}: spec={repr(c1)} (ord={ord(c1)}), raw={repr(c2)} (ord={ord(c2)})")
    
    if len(spec_password) != len(raw_password):
        print(f"  Length diff: spec={len(spec_password)}, raw={len(raw_password)}")
