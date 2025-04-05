# Centralized UPI Payment Gateway

A secure UPI payment gateway implementation using Blockchain, Lightweight Cryptography, and Quantum Cryptography.

## Features

- Secure merchant and user registration
- QR code generation for payments
- Lightweight Cryptography (SPECK) for merchant ID encryption
- Quantum Cryptography simulation using Shor's algorithm
- Blockchain-based transaction recording
- Secure PIN verification

## Project Structure

```
upi_payment_gateway/
├── src/
│   ├── bank/           # Bank-related functionality
│   ├── merchant/       # Merchant-related functionality
│   ├── user/          # User-related functionality
│   ├── upi_machine/   # UPI machine functionality
│   ├── crypto/        # Cryptographic implementations
│   └── utils/         # Utility functions
└── tests/             # Test cases
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Bank Registration

```python
from src.bank.bank import Bank

# Create a new bank
bank = Bank("HDFC", "HDFC0001234")

# Register a merchant
mid = bank.register_merchant("Merchant Name", "password", 1000.0)

# Register a user
uid = bank.register_user("User Name", "password", "9876543210", "1234", 5000.0)
```

### UPI Machine

```python
from src.upi_machine.upi_machine import UPIMachine

# Initialize UPI machine
upi_machine = UPIMachine(bank)

# Login merchant
upi_machine.login_merchant(mid, "password")

# Generate QR code
qr_filename = upi_machine.generate_qr_code()

# Process payment
success = upi_machine.process_payment(encrypted_mid, uid, 100.0, "1234")
```

## Security Features

1. **Lightweight Cryptography (LWC)**

   - Uses SPECK algorithm for merchant ID encryption
   - Fast and efficient encryption for resource-constrained environments

2. **Quantum Cryptography**

   - Simulates Shor's algorithm for PIN cracking
   - Demonstrates vulnerability of classical cryptography

3. **Blockchain**
   - Immutable transaction recording
   - Transparent and secure transaction history
   - Automatic balance calculation

## Testing

Run tests using:

```bash
pytest tests/
```

## Team Members

- [Team Member 1]
- [Team Member 2]
- [Team Member 3]

## License

This project is licensed under the MIT License.
