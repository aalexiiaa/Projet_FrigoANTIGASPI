from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from datetime import datetime, date
from co2_stats import calculer_co2_economise, construire_stats_depuis_historique, generer_rapport_mensuel
from priorite import analyser_produit, trier_par_priorite, a_consommer_aujourd_hui

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+pg8000://neondb_owner:npg_BVJg5YLyet1o@ep-raspy-sea-ab7gmqpt.eu-west-2.aws.neon.tech/neondb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "cle-secrete-frigo"

db  = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    __tablename__ = "users"
    id           = db.Column(db.Integer, primary_key=True)
    nom          = db.Column(db.String(100))
    email        = db.Column(db.String(100), unique=True)
    mot_de_passe = db.Column(db.String(255))
    role         = db.Column(db.String(15))


class Produit(db.Model):
    __tablename__ = "produits"
    id              = db.Column(db.Integer, primary_key=True)
    nom             = db.Column(db.String(100))
    quantite        = db.Column(db.Integer)
    date_expiration = db.Column(db.Date)

class HistoriqueProduit(db.Model):
    __tablename__ = "historique_produits"
    id                 = db.Column(db.Integer, primary_key=True)
    produit_id         = db.Column(db.Integer, db.ForeignKey("produits.id", ondelete="SET NULL"))
    nom                = db.Column(db.String(100))
    quantite           = db.Column(db.Integer)
    date_expiration    = db.Column(db.Date)
    consomme_le        = db.Column(db.Date, default=date.today)
    co2_economise_kg   = db.Column(db.Float)


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if user and user.mot_de_passe == data["mot_de_passe"]:
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token, "nom": user.nom, "role": user.role}), 200
    else:
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401


@app.route("/api/produits", methods=["GET"])
def get_products():
    produits = Produit.query.all()
    resultat = []
    for p in produits:
        produit_dict = {
            "id":              p.id,
            "nom":             p.nom,
            "quantite":        p.quantite,
            "date_peremption": p.date_expiration.strftime("%Y-%m-%d")
        }
        analyser_produit(produit_dict)
        resultat.append(produit_dict)
    resultat = trier_par_priorite(resultat)
    return jsonify(resultat), 200


@app.route("/api/produits", methods=["POST"])
def add_product():
    data = request.json
    exp_date = datetime.strptime(data["date_peremption"], "%Y-%m-%d").date()
    nouveau_produit = Produit(
        nom=data["nom"],
        quantite=data.get("quantite", 1),
        date_expiration=exp_date
    )
    db.session.add(nouveau_produit)
    db.session.commit()
    return jsonify({"message": "Produit ajouté !"}), 201


@app.route("/api/produits/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    produit = Produit.query.get(id)
    if not produit:
        return jsonify({"error": "Produit introuvable"}), 404
    historique = HistoriqueProduit(
        produit_id=produit.id,
        nom=produit.nom,
        quantite=produit.quantite,
        date_expiration=produit.date_expiration,
        co2_economise_kg=calculer_co2_economise(produit.nom, produit.quantite)
    )
    db.session.add(historique)
    db.session.delete(produit)
    db.session.commit()
    return jsonify({"message": "Produit consommé !"}), 200


@app.route("/api/co2/stats", methods=["GET"])
def co2_stats():
    historique = HistoriqueProduit.query.order_by(HistoriqueProduit.consomme_le.asc()).all()
    stats = construire_stats_depuis_historique(historique)
    return jsonify(stats), 200


@app.route("/api/co2/historique", methods=["GET"])
def co2_historique():
    historique = HistoriqueProduit.query.order_by(HistoriqueProduit.consomme_le.desc()).all()
    resultat = []
    for h in historique:
        resultat.append({
            "id": h.id,
            "nom": h.nom,
            "quantite": h.quantite,
            "date_expiration": h.date_expiration.strftime("%Y-%m-%d") if h.date_expiration else None,
            "consomme_le": h.consomme_le.strftime("%Y-%m-%d") if h.consomme_le else None,
            "co2_economise_kg": h.co2_economise_kg
        })
    return jsonify(resultat), 200


@app.route("/api/co2/rapport-mensuel", methods=["GET"])
def co2_rapport_mensuel():
    mois = request.args.get("mois")
    historique = HistoriqueProduit.query.all()
    rapport = generer_rapport_mensuel(historique, mois)
    return jsonify({"mois": mois, "rapport": rapport}), 200


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    user_existant = User.query.filter_by(email=data["email"]).first()
    if user_existant:
        return jsonify({"error": "Ce user existe déja"}), 400
    user = User(
        nom=data["nom"],
        email=data["email"],
        mot_de_passe=data["mot_de_passe"],
        role="admin"
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Le compte a été crée"}), 201


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
