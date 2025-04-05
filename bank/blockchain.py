import hashlib
import time
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Transaction:
    uid: str
    mid: str
    amount: float
    timestamp: float
    transaction_id: str = None

    def __post_init__(self):
        if self.transaction_id is None:
            # Generate transaction ID using SHA-256
            data = f"{self.uid}{self.mid}{self.timestamp}{self.amount}"
            self.transaction_id = hashlib.sha256(data.encode()).hexdigest()

class Block:
    def __init__(self, transactions: List[Transaction], previous_hash: str):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = f"{self.previous_hash}{self.timestamp}"
        for tx in self.transactions:
            block_data += tx.transaction_id
        return hashlib.sha256(block_data.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block([], "0" * 64)
        self.chain.append(genesis_block)

    def add_transaction(self, transaction: Transaction):
        self.pending_transactions.append(transaction)
        if len(self.pending_transactions) >= 5:  # Create new block every 5 transactions
            self.mine_pending_transactions()

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            return

        new_block = Block(
            transactions=self.pending_transactions.copy(),
            previous_hash=self.chain[-1].hash
        )
        self.chain.append(new_block)
        self.pending_transactions = []

    def get_balance(self, account_id: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.uid == account_id:
                    balance -= tx.amount
                if tx.mid == account_id:
                    balance += tx.amount
        return balance

    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True 