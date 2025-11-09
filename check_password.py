#!/usr/bin/env python3
"""Check the exact password stored in the database."""

import sys
sys.path.insert(0, '/Users/ahmedelbehiry/Documents/Software Engineering/ECE30861-Phase2')

from src.database.connection import SessionLocal
from src.database.models import User
from src.auth.password_hash import verify_password

# The password from the spec
spec_password = 'correcthorsebatterystaple123(!__+@**(A\'"`);DROP TABLE artifacts;'

print("Password from spec:")
print(repr(spec_password))
print(f"Length: {len(spec_password)}")
print(f"Bytes: {spec_password.encode('utf-8')}")
print()

# Check what's in the database
db = SessionLocal()
try:
    user = db.query(User).filter(User.username == "ece30861defaultadminuser").first()
    if user:
        print(f"User found: {user.username}")
        print(f"User is_admin: {user.is_admin}")
        print(f"Password hash: {user.hashed_password[:50]}...")
        print()
        
        # Test if the spec password matches
        if verify_password(spec_password, user.hashed_password):
            print("✅ Spec password MATCHES the hash in database!")
        else:
            print("❌ Spec password DOES NOT match the hash in database!")
        
        # Try some variations
        variations = [
            'correcthorsebatterystaple123(!__+@**(A;DROP TABLE packages\'',  # Old version
            r'correcthorsebatterystaple123(!__+@**(A\'"\`;DROP TABLE artifacts;',  # No backtick at end - raw string
            'correcthorsebatterystaple123(!__+@**(A\'"`;DROP TABLE artifacts;',  # Different order
        ]
        
        print("\nTrying variations:")
        for var in variations:
            if verify_password(var, user.hashed_password):
                print(f"✅ MATCH: {repr(var)}")
            else:
                print(f"❌ No match: {repr(var)}")
    else:
        print("❌ User not found in database!")
finally:
    db.close()
