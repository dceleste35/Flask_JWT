from flask import Flask
from flask import render_template
from flask import json
from flask import jsonify
from flask import request
from datetime import timedelta
from flask import redirect, make_response

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies


app = Flask(__name__)

# Configuration du module JWT
app.config["JWT_SECRET_KEY"] = "Ma_clé_secrete"  # Ma clée privée
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

jwt = JWTManager(app)

@app.route('/')
def hello_world():
    return render_template('accueil.html')

# Création d'une route qui vérifie l'utilisateur et retour un Jeton JWT si ok.
# La fonction create_access_token() est utilisée pour générer un jeton JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username != "test" or password != "test":
        return jsonify({"msg": "Mauvais utilisateur ou mot de passe"}), 401

    access_token = create_access_token(
        identity=username,
        expires_delta=timedelta(hours=1),
        additional_claims={"role": "admin"}
    )

    response = make_response(redirect('/protected'))
    set_access_cookies(response, access_token)

    return response


# Route protégée par un jeton valide
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()

    if current_user != "test":
        return "Vous n'avez pas accès à cette ressource"

    return "Bienvenue dans la zone protégée, accès autorisé uniquement avec un jeton valide !"

# Route pour vérifier si c'est un admin
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin_protected():
    jwt = get_jwt()
    if jwt.get("role") != "admin":
        return jsonify({"msg": "Accès réservé aux administrateurs"}), 403

    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == "__main__":
  app.run(debug=True)
