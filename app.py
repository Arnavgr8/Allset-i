from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = "secret" # Generates a random key of 32 hex characters

# Configure SQLAlchemy with multiple databases
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///database/users.db',   # Users database
    'contacts': 'sqlite:///database/contacts.db'  # Contacts database
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model (for 'users' database)
class User(db.Model):
    __bind_key__ = 'users'  # Binds this model to the 'users' database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    firstname = db.Column(db.String(100))  # Ensure this column exists
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)

# Define the Contact model (for 'contacts' database)
class Contact(db.Model):
    __bind_key__ = 'contacts'  # Binds this model to the 'contacts' database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)

# Dummy credentials for login (replace this with a database in a real app)
USERNAME = "admin"
PASSWORD = "admin123"

# Route for the home page
@app.route('/')
def home():
    # Check if user is logged in
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
        elif existing_email:
            flash('Email is already in use. Please use a different one.', 'danger')
        else:
            # Hash the password before storing it
            password_hash = generate_password_hash(password)
            # Create a new user record
            new_user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password_hash)

            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error! Account not created. Please try again. {str(e)}", 'danger')

    return render_template('signup.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):
            # Store username in session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

# Route to display and handle the contact form (both GET and POST requests)
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # Create a new contact record
        new_contact = Contact(name=name, email=email, phone=phone, message=message)

        try:
            db.session.add(new_contact)
            db.session.commit()
            return redirect('/sent')
        except Exception as e:
            db.session.rollback()
            flash(f"Error! Message not saved, please try again. {str(e)}")

    return render_template('contact.html')

# Route to display the "Message Sent" page
@app.route('/sent')
def sent():
    return render_template('sent.html')

# Logout route to clear the session
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Create the database tables (if not already created)
with app.app_context():
    db.create_all(bind='users')  # Create tables for users database
    db.create_all(bind='contacts')  # Create tables for contacts database

# Run the app
if __name__ == '__main__':
    app.run(debug=True)