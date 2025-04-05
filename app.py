from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Get the absolute path to the src directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static',
    template_folder=os.path.join(BASE_DIR, 'templates')
)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///upi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize bank and UPI machine
from bank.bank import Bank
from upi_machine.upi_machine import UPIMachine
from crypto.lwc import LightweightCrypto
from crypto.quantum import QuantumCrypto

bank = Bank("HDFC", "HDFC0001234")
upi_machine = UPIMachine(bank)
lwc = LightweightCrypto()
quantum = QuantumCrypto()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    uid = db.Column(db.String(32), unique=True)
    mmid = db.Column(db.String(7), unique=True)
    balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    mid = db.Column(db.String(32), unique=True)
    balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        pin = request.form['pin']
        initial_balance = float(request.form['balance'])

        # Register with bank
        uid = bank.register_user(username, password, mobile, pin, initial_balance)
        
        # Create database user
        user = User(username=username, mobile=mobile, uid=uid)
        user.set_password(password)
        user.balance = initial_balance
        
        db.session.add(user)
        db.session.commit()
        
        flash('User registered successfully!')
        return redirect(url_for('login'))
    
    return render_template('register_user.html')

@app.route('/register/merchant', methods=['GET', 'POST'])
def register_merchant():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        initial_balance = float(request.form['balance'])

        # Register with bank
        mid = bank.register_merchant(name, password, initial_balance)
        
        # Create database merchant
        merchant = Merchant(name=name, mid=mid)
        merchant.set_password(password)
        merchant.balance = initial_balance
        
        db.session.add(merchant)
        db.session.commit()
        
        flash('Merchant registered successfully!')
        return redirect(url_for('login'))
    
    return render_template('register_merchant.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if user_type == 'user':
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('user_dashboard'))
        else:
            merchant = Merchant.query.filter_by(name=username).first()
            if merchant and merchant.check_password(password):
                session['merchant_id'] = merchant.mid
                return redirect(url_for('merchant_dashboard'))
        
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html', user=current_user)

@app.route('/merchant/dashboard')
def merchant_dashboard():
    if 'merchant_id' not in session:
        return redirect(url_for('login'))
    
    merchant = Merchant.query.filter_by(mid=session['merchant_id']).first()
    return render_template('merchant_dashboard.html', merchant=merchant)

@app.route('/merchant/generate_qr')
def generate_qr():
    if 'merchant_id' not in session:
        return redirect(url_for('login'))
    
    qr_filename = upi_machine.generate_qr_code()
    return render_template('qr_display.html', qr_filename=qr_filename)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        encrypted_mid = request.form['encrypted_mid']
        amount = float(request.form['amount'])
        pin = request.form['pin']
        
        success = upi_machine.process_payment(encrypted_mid, current_user.uid, amount, pin)
        if success:
            flash('Payment successful!')
        else:
            flash('Payment failed!')
        
        return redirect(url_for('user_dashboard'))
    
    return render_template('payment.html')

@app.route('/logout')
def logout():
    logout_user()
    session.pop('merchant_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 