from flask import Flask, render_template, request, jsonify, redirect, url_for
from entities.user import User
from flask_login import LoginManager, login_user, login_required, logout_user
from dotenv import load_dotenv
from entities.account import Account
from entities.transactions import Transaction
from flask_login import current_user
import os
from entities.log import log
from enums.log_type import LogType

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/welcome')
@login_required
def welcome():
    user_account = Account.get_account_by_user(current_user.id)
    return render_template('welcome.html', account=user_account)

@app.route('/api/users', methods=["POST"])
def create_user():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.check_email_exists(email):
        return jsonify({"success": False, "message": "El correo electrónico ingresado ya se encuentra registrado."}), 409

    if User.save(name, email, password):
        return jsonify({"success": True, "message": "Su cuenta fue creada correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "Ocurrió un error al crear su cuenta. Intente de nuevo"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.check_login(email, password)
    if user:

        login_user(user)
        log.save_log(user, "Inicio de sesión exitoso", LogType.LOGIN)
        
        return jsonify({
            "success": True,
            "message": "Sesión iniciada correctamente"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Los datos de acceso ingresados no son correctos."
        }), 401

@app.route('/api/transactions', methods=['POST'])
@login_required
def create_transaction():
    data = request.get_json()

    description = data.get("description")
    amount = data.get("amount")
    transaction_type = data.get("transaction_type")

    if not description or not amount or not transaction_type:
        return jsonify({"success": False, "message": "Todos los campos son requeridos."}), 400

    if transaction_type not in ["INCOME", "EXPENSE"]:
        return jsonify({"success": False, "message": "Tipo de transacción inválido."}), 400

    account = Account.get_account_by_user(current_user.id)
    if not account:
        return jsonify({"success": False, "message": "No se encontró la cuenta del usuario."}), 404

    if Transaction.save(description, float(amount), transaction_type, account.id):
        return jsonify({"success": True, "message": "Movimiento registrado correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "Ocurrió un error al registrar el movimiento."}), 500

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run()