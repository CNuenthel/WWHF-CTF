import os
from flask import render_template, send_from_directory, url_for, flash, redirect, request, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, ContractForm, SignContractForm
from app.models import User, Contract, UserContractStatus
from flask_login import login_user, current_user, logout_user, login_required
import hashlib
import time
from markupsafe import Markup

main = Blueprint('main', __name__)

def generate_secure_token(email):
    return hashlib.pbkdf2_hmac('sha256', email.encode(), int(time.time()).to_bytes(4, 'big'), 100000).hex()

@main.route("/")
@main.route("/home")
def home():
    return render_template('index.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        recovery_token = generate_secure_token(form.email.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, reset_token=recovery_token)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! Your recovery token is {recovery_token}. Please keep it safe as it will allow you to recover access to your account.', 'success')
        print(f"Registration successful: {form.username.data}, {form.email.data}, {form.password.data}")
        return redirect(url_for('main.login'))
    else:
        if form.errors:
            print(f"Registration failed: {form.username.data}, {form.email.data}, {form.password.data}, Errors: {form.errors}")
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and (bcrypt.check_password_hash(user.password, form.password.data) or user.reset_token == form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            print(f"Login successful: {form.email.data}, {form.password.data}")
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email, password, or recovery token', 'danger')
            print(f"Login failed: {form.email.data}, {form.password.data}")
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/create_contract", methods=['GET', 'POST'])
@login_required
def create_contract():
    form = ContractForm()
    if form.validate_on_submit():
        contract = Contract(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(contract)
        db.session.commit()
        flash(Markup(f'Your contract has been created! View it <a href="{url_for("main.contract", contract_id=contract.id)}">here</a>.'), 'success')
        return redirect(url_for('main.home'))
    return render_template('create_contract.html', title='New Contract', form=form)

@main.route("/contracts")
@login_required
def contracts():
    user_contracts = Contract.query.filter_by(author=current_user).all()
    signed_contracts = UserContractStatus.query.filter_by(user_id=current_user.id).all()
    return render_template('view_contracts.html', title='Your Contracts', user_contracts=user_contracts, signed_contracts=signed_contracts)

@main.route("/contract/<int:contract_id>")
@login_required
def contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    user_statuses = UserContractStatus.query.filter_by(contract_id=contract.id).all()
    return render_template('contract.html', title=contract.title, contract=contract, user_statuses=user_statuses)

@main.route("/sign_contract/<int:contract_id>", methods=['GET', 'POST'])
@login_required
def sign_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    user_status = UserContractStatus.query.filter_by(user_id=current_user.id, contract_id=contract.id).first()
    form = SignContractForm()
    if form.validate_on_submit():
        if form.submit.data:
            user_status.status = 'signed'
            flash('You have signed the contract!', 'success')
        elif form.refuse.data:
            user_status.status = 'refused'
            flash('You have refused to sign the contract.', 'danger')
        db.session.commit()
        return redirect(url_for('main.contract', contract_id=contract.id))
    return render_template('sign_contract.html', title='Sign Contract', contract=contract, user_status=user_status, form=form)

@main.route("/send_contract/<int:contract_id>", methods=['GET', 'POST'])
@login_required
def send_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            user_status = UserContractStatus(user_id=user.id, contract_id=contract.id)
            db.session.add(user_status)
            db.session.commit()
            flash('Contract sent successfully!', 'success')
        else:
            flash('User not found.', 'danger')
        return redirect(url_for('main.contract', contract_id=contract.id))
    return render_template('send_contract.html', title='Send Contract', contract=contract)

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'danger')
    return render_template('reset_request.html')

@main.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.query.filter_by(reset_token=token).first()
    if user is None:
        flash('That is an invalid token', 'warning')
        return redirect(url_for('main.reset_request'))
    if request.method == 'POST':
        password = request.form.get('password')
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html')
