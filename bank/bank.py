import hashlib
from typing import Dict
from .blockchain import Blockchain, Transaction

class Bank:
    def __init__(self, name: str, ifsc_code: str):
        self.name = name
        self.ifsc_code = ifsc_code
        self.merchants: Dict[str, Dict] = {}  # MID -> merchant details
        self.users: Dict[str, Dict] = {}      # UID -> user details
        self.blockchain = Blockchain()

    def register_merchant(self, name: str, password: str, initial_balance: float) -> str:
        """
        Register a new merchant and generate their Merchant ID (MID)
        """
        # Generate MID using SHA-256
        data = f"{name}{password}{self.ifsc_code}"
        mid = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        # Store merchant details
        self.merchants[mid] = {
            'name': name,
            'password': password,
            'balance': initial_balance
        }
        
        return mid

    def register_user(self, name: str, password: str, mobile: str, pin: str, initial_balance: float) -> str:
        """
        Register a new user and generate their User ID (UID)
        """
        # Generate UID using SHA-256
        data = f"{name}{password}{self.ifsc_code}"
        uid = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        # Generate MMID
        mmid = hashlib.sha256(f"{uid}{mobile}".encode()).hexdigest()[:7]
        
        # Store user details
        self.users[uid] = {
            'name': name,
            'password': password,
            'mobile': mobile,
            'pin': pin,
            'mmid': mmid,
            'balance': initial_balance
        }
        
        return uid

    def process_transaction(self, uid: str, mid: str, amount: float, pin: str) -> bool:
        """
        Process a transaction between user and merchant
        """
        # Verify user exists and PIN is correct
        if uid not in self.users or self.users[uid]['pin'] != pin:
            return False
            
        # Verify merchant exists
        if mid not in self.merchants:
            return False
            
        # Check if user has sufficient balance
        if self.blockchain.get_balance(uid) < amount:
            return False
            
        # Create and add transaction to blockchain
        transaction = Transaction(uid, mid, amount, time.time())
        self.blockchain.add_transaction(transaction)
        
        return True

    def get_user_balance(self, uid: str) -> float:
        """
        Get current balance of a user
        """
        return self.blockchain.get_balance(uid)

    def get_merchant_balance(self, mid: str) -> float:
        """
        Get current balance of a merchant
        """
        return self.blockchain.get_balance(mid)

    def verify_credentials(self, uid: str, pin: str) -> bool:
        """
        Verify user credentials
        """
        return uid in self.users and self.users[uid]['pin'] == pin 