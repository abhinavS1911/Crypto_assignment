from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import time
import base64

class LightweightCrypto:
    def __init__(self):
        self.key = b'16bytekey1234567'  # 128-bit key for AES
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def generate_vmid(self, merchant_id: str, timestamp: int) -> str:
        """
        Generate Virtual Merchant ID (VMID) using AES encryption
        """
        # Combine merchant ID and timestamp
        data = f"{merchant_id}{timestamp}".encode()
        
        # Pad data to multiple of 16 bytes
        padded_data = pad(data, AES.block_size)
        
        # Encrypt using AES
        encrypted = self.cipher.encrypt(padded_data)
        
        # Convert to 16-digit hex
        vmid = encrypted.hex()[:16]
        return vmid

    def encrypt_merchant_id(self, merchant_id: str) -> str:
        """
        Encrypt merchant ID for QR code generation
        """
        timestamp = int(time.time())
        return self.generate_vmid(merchant_id, timestamp)

    def decrypt_merchant_id(self, encrypted_id: str) -> str:
        """
        Decrypt merchant ID from QR code
        Note: This is a simplified version. In real implementation,
        you would need to handle the timestamp and proper decryption
        """
        # In a real implementation, this would properly decrypt the VMID
        # For this example, we'll just return the first 16 characters
        return encrypted_id[:16] 