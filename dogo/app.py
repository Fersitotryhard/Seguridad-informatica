from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from entities.permission import Permissions
from entities.user import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from entities.account import Account
from entities.transactions import Transaction
from entities.log import log
from enums.log_type import LogType
from enums.value_permissions import ValuePermissions
import os

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
    
        if user.is_active:
            return jsonify({
                "success": True,
                "message": "Inicio de sesión exitoso."
            }), 200

        login_user(user)
        log.save_log(user, "Inicio de sesión exitoso", LogType.LOGIN)
        return jsonify({"success": True, "message": "Sesión iniciada correctamente"}), 200
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

#Administradores

@app.route('/usuarios')
@login_required
def usuarios():
    if not current_user.is_admin():
        abort(403)
    users = User.get_all()
    all_permissions = [p.name for p in ValuePermissions]
    return render_template('usuarios.html', users=users, all_permissions=all_permissions)

@app.route('/api/usuarios/<int:user_id>/permisos', methods=['POST'])
@login_required
def agregar_permiso(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso denegado."}), 403

    data = request.get_json()
    permission_value = data.get("permission")

    if not permission_value or permission_value not in [p.name for p in ValuePermissions]:
        return jsonify({"success": False, "message": "Permiso inválido."}), 400

    if User.add_permission(user_id, permission_value):
        return jsonify({"success": True, "message": "Permiso agregado correctamente."}), 201
    else:
        return jsonify({"success": False, "message": "El permiso ya existe o hubo un error."}), 409

@app.route('/api/usuarios/<int:user_id>/permisos', methods=['DELETE'])
@login_required
def eliminar_permiso(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso denegado."}), 403

    data = request.get_json()
    permission_value = data.get("permission")

    if User.remove_permission(user_id, permission_value):
        return jsonify({"success": True, "message": "Permiso eliminado."}), 200
    else:
        return jsonify({"success": False, "message": "Error al eliminar permiso."}), 500
    
@app.route('/api/usuarios/<int:user_id>/permisos-lista', methods=['GET'])
@login_required
def listar_permisos(user_id):
    if not current_user.is_admin():
        return jsonify({"success": False, "message": "Acceso denegado."}), 403
    perms = Permissions.get_permissions_by_user_id(user_id)
    return jsonify({"permissions": [p.value.name for p in perms]})

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run()