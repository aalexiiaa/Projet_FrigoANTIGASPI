INSERT INTO users(nom, email, mot_de_passe, role)
VALUES ('Test2', 'admin1@test.fr', '123456', 'admin');

INSERT INTO produits(nom, quantite, date_expiration)
VALUES 
('Lait', 2, '2027-04-01'),
('Pain', 1, '2026-03-30');

SELECT * FROM users;
SELECT * FROM produits;
SELECT * FROM historique_produits;