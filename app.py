from datetime import timedelta
from flask import Flask, render_template, session, redirect, url_for
from modules.auth import auth_bp
from modules.dashboard import dashboard_bp, get_dashboard_context
from modules.books import books_bp
from modules.students import students_bp
from modules.report import report_bp
from extensions import mail

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.permanent_session_lifetime = timedelta(days=7)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mulayam99.ak@gmail.com'
app.config['MAIL_PASSWORD'] = 'eefd kkme uezy uhtw'
app.config['MAIL_DEFAULT_SENDER'] = 'mulayam99.ak@gmail.com'
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(books_bp)
app.register_blueprint(students_bp)
app.register_blueprint(report_bp)

@app.route('/')
def home():
    if 'email' in session:
        return redirect(url_for('home_page'))
    return redirect(url_for('auth.login'))


@app.route('/home')
def home_page():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    context = get_dashboard_context()
    context['email'] = session['email']
    return render_template('home.html', **context)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
