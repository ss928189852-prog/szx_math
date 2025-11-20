import hashlib

# Hash a plain text password

plain_password = input("Please input a password: ")
hashed_password = hashlib.sha256(plain_password.encode()).hexdigest()

# Use 'hashed_password' for database operations
print(f"Hashed Password: {hashed_password}")
