CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	nom VARCHAR(100),
	email VARCHAR(100) UNIQUE,
	mot_de_passe VARCHAR(50),
	role VARCHAR(15)
);
CREATE TABLE produits(
	id SERIAL PRIMARY KEY,
	nom VARCHAR(100),
	quantite INTEGER,
	date_expiration DATE
);
CREATE TABLE historique_produits(
	id SERIAL PRIMARY KEY,
	produit_id INTEGER REFERENCES produits(id) ON DELETE SET NULL,
	nom VARCHAR(100),
	quantite INTEGER,
	date_expiration DATE,
	consomme_le DATE DEFAULT CURRENT_DATE,
	co2_economise_kg FLOAT
);



