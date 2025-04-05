import qrcode
import time
from typing import Optional
from src.crypto.lwc import LightweightCrypto
from src.bank.bank import Bank

class UPIMachine:
    def __init__(self, bank: Bank):
        self.bank = bank
        self.lwc = LightweightCrypto()
        self.current_merchant: Optional[str] = None

    def login_merchant(self, mid: str, password: str) -> bool:
        """
        Login merchant to the UPI machine
        """
        if mid in self.bank.merchants and self.bank.merchants[mid]['password'] == password:
            self.current_merchant = mid
            return True
        return False

    def generate_qr_code(self) -> Optional[str]:
        """
        Generate QR code for the current merchant
        """
        if not self.current_merchant:
            return None

        # Encrypt merchant ID using LWC
        encrypted_mid = self.lwc.encrypt_merchant_id(self.current_merchant)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(encrypted_mid)
        qr.make(fit=True)
        
        # Save QR code to file
        filename = f"qr_{self.current_merchant}_{int(time.time())}.png"
        qr.make_image(fill_color="black", back_color="white").save(filename)
        
        return filename

    def process_payment(self, encrypted_mid: str, uid: str, amount: float, pin: str) -> bool:
        """
        Process payment from user to merchant
        """
        # Decrypt merchant ID
        mid = self.lwc.decrypt_merchant_id(encrypted_mid)
        
        # Verify merchant exists
        if mid not in self.bank.merchants:
            return False
            
        # Process transaction through bank
        return self.bank.process_transaction(uid, mid, amount, pin)

    def get_merchant_balance(self) -> Optional[float]:
        """
        Get current merchant's balance
        """
        if not self.current_merchant:
            return None
        return self.bank.get_merchant_balance(self.current_merchant) 