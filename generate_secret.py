#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Flask production deployment
Run this script to generate a cryptographically secure secret key
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == '__main__':
    secret_key = generate_secret_key()
    print("🔐 Generated SECRET_KEY for Render deployment:")
    print("=" * 50)
    print(secret_key)
    print("=" * 50)
    print("\n📋 Copy this key and add it to your Render environment variables:")
    print("SECRET_KEY=" + secret_key)
    print("\n⚠️  Keep this key secure and never commit it to version control!")