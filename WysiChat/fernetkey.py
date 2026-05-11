from cryptography.fernet import Fernet

# Generate the key
key = Fernet.generate_key()

# Print it out so you can copy it
print(key)
