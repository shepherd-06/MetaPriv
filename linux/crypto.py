 # pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import hashlib


def Hash(text):
	return hashlib.sha256(text.encode()).digest()

def aes_encrypt(plaintext, key):
	padded_text = pad(plaintext.encode(), 16)
	cipher = AES.new(key, AES.MODE_ECB)
	ciphertext = cipher.encrypt(padded_text)
	return b64encode(ciphertext).decode('utf-8')

def aes_decrypt(ciphertext, key):
	cipher = AES.new(key, AES.MODE_ECB)
	padded_text = cipher.decrypt(b64decode(ciphertext.encode('utf-8')))
	plaintext = unpad(padded_text, 16)
	return plaintext.decode()