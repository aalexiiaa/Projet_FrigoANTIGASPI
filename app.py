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
  