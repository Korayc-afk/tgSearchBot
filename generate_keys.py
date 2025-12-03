"""
Güvenlik anahtarları oluşturma scripti
"""

import secrets
from cryptography.fernet import Fernet

# SECRET_KEY oluştur (Flask session için)
secret_key = secrets.token_hex(32)
print("=" * 60)
print("SECRET_KEY:")
print(secret_key)
print("=" * 60)

# ENCRYPTION_KEY oluştur (API hash şifreleme için)
encryption_key = Fernet.generate_key().decode()
print("\nENCRYPTION_KEY:")
print(encryption_key)
print("=" * 60)

print("\n✅ Bu değerleri environment variables olarak ekleyin!")
print("⚠️  Bu değerleri güvenli tutun ve kimseyle paylaşmayın!")

