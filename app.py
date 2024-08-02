from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelbooking.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    package = db.relationship('Package', backref='bookings')

db.create_all()

@app.route('/')
def home():
    packages = Package.query.all()
    return render_template('index.html', packages=packages)

@app.route('/package/<int:package_id>')
def package_detail(package_id):
    package = Package.query.get_or_404(package_id)
    return render_template('package_detail.html', package=package)

@app.route('/book/<int:package_id>')
def book_package(package_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    new_booking = Booking(user_id=user_id, package_id=package_id)
    db.session.add(new_booking)
    db.session.commit()
    return redirect(url_for('bookings'))

@app.route('/bookings')
def bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    return render_template('bookings.html', bookings=user.bookings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
