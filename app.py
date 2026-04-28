from flask import Flask, request, jsonify
from flask_cors import CORS

app= Flask(__name__)
CORS(app)

@app.route("/")
def home():
  return("Server ok")

@app.route("/products", methods=["POST"])
def add_product():
  data=request.json
  print("Produit: ", data)

  return jsonify({"message": "ok"})

if __name__=="__main__":
  app.run(debug=True)

@app.route("/products", methods=["GET"])
def get_products():
  produits=[
    {"nom": "yaourt", "date_peremption": "2026-04-30"},
    {"nom": "lait", "date_peremption": "2026-04-25"},
  ]
  return jsonify(produits)
