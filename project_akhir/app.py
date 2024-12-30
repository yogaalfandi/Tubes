from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Inisialisasi Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/project_akhir'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi Database & Login Manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class KonsultasiUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route Halaman Utama
@app.route('/')
def home():
    return render_template('home.html')

# Route Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('index_user'))
        else:
            flash('Login gagal. Periksa kembali username dan password Anda.', 'error')
    return render_template('login.html')

# Route Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan. Pilih username lain.', 'error')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Route Halaman User (Setelah Login)
@app.route('/index_user')
@login_required
def index_user():
    users = KonsultasiUser.query.all()
    return render_template('index_user.html', username=current_user.username, users=users)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Anda berhasil logout.', 'info')
    return redirect(url_for('home'))


# Route CRUD for KonsultasiUser
@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    age = request.form['age']
    email = request.form['email']
    new_user = KonsultasiUser(name=name, age=age, email=email)
    db.session.add(new_user)
    db.session.commit()
    flash('Data berhasil ditambahkan!', 'success')
    return redirect(url_for('index_user'))

# Route untuk halaman edit data pengguna
@app.route('/edit/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    user = KonsultasiUser.query.get_or_404(user_id)  # Ambil pengguna berdasarkan ID
    return render_template('edit.html', user=user)

# Route untuk memperbarui data pengguna
@app.route('/update/<int:user_id>', methods=['POST'])
def update_user(user_id):
    user = KonsultasiUser.query.get_or_404(user_id)  # Ambil pengguna berdasarkan ID
    user.name = request.form['name']
    user.age = request.form['age']
    user.email = request.form['email']

    db.session.commit()  # Simpan perubahan ke database
    return redirect(url_for('index_user'))

@app.route('/delete/<int:id>')
def delete_user(id):
    user = KonsultasiUser.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Data berhasil dihapus!', 'success')
    return redirect(url_for('index_user'))

# Route About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Route Services
@app.route('/services')
def services():
    return render_template('services.html')

# Menjalankan Aplikasi
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
