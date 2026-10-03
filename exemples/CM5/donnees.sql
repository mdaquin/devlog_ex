-- Les identifiants auto-incrémentés suivent l'ordre d'insertion :
-- personne 1 = Sonia, 2 = Karim, 3 = Léa.

INSERT INTO personne (nom, prenom, courriel) VALUES
  ('Berthier', 'Sonia', 's.berthier@example.com'),
  ('Vasseur',  'Karim', 'k.vasseur@example.com'),
  ('Nguyen',   'Léa',   'l.nguyen@example.org');

INSERT INTO compte (iban, bic, intitule, banque) VALUES
  ('FR7630001007941234567890185', 'BNPAFRPP', 'Compte courant Sonia',     'BNP Paribas'),
  ('FR1420041010050500013M02606', 'PSSTFRPP', 'Compte joint Sonia-Karim', 'La Banque Postale'),
  ('FR7610107001011234567890129', 'BREDFRPP', 'Livret Léa',               'BRED');

-- détention : le deuxième compte est un compte joint
INSERT INTO detient (id_personne, iban) VALUES
  (1, 'FR7630001007941234567890185'),
  (1, 'FR1420041010050500013M02606'),
  (2, 'FR1420041010050500013M02606'),
  (3, 'FR7610107001011234567890129');

-- partages : Karim voit le courant de Sonia ; Sonia gère le livret de Léa
INSERT INTO partage (id_personne, iban, droit) VALUES
  (2, 'FR7630001007941234567890185', 'lecture'),
  (1, 'FR7610107001011234567890129', 'ecriture');

-- catégories, propres à chaque personne (1-4 Sonia, 5-6 Karim, 7 Léa)
INSERT INTO categorie (nom, id_personne) VALUES
  ('Courses', 1), ('Logement', 1), ('Transport', 1), ('Loisirs', 1),
  ('Courses', 2), ('Abonnements', 2),
  ('Études',  3);

INSERT INTO releve (iban, periode_debut, periode_fin, date_import) VALUES
  ('FR7630001007941234567890185', '2026-01-01', '2026-01-31', '2026-02-02 09:14'),
  ('FR7630001007941234567890185', '2026-02-01', '2026-02-28', '2026-03-02 08:51'),
  ('FR1420041010050500013M02606', '2026-01-01', '2026-01-31', '2026-02-03 19:40'),
  ('FR7610107001011234567890129', '2026-01-01', '2026-01-31', '2026-02-05 12:07');

INSERT INTO operation
  (date_operation, libelle, montant, iban, periode_debut, periode_fin, id_categorie) VALUES
  ('2026-01-03','LOYER JANVIER',      -700.00,'FR7630001007941234567890185','2026-01-01','2026-01-31',    2),
  ('2026-01-07','CARREFOUR MARKET',    -42.50,'FR7630001007941234567890185','2026-01-01','2026-01-31',    1),
  ('2026-01-12','SNCF CONNECT',        -38.90,'FR7630001007941234567890185','2026-01-01','2026-01-31',    3),
  ('2026-01-15','VIREMENT SALAIRE',   2150.00,'FR7630001007941234567890185','2026-01-01','2026-01-31', NULL),
  ('2026-01-22','CINEMA PATHE',        -11.50,'FR7630001007941234567890185','2026-01-01','2026-01-31',    4),
  ('2026-02-03','LOYER FEVRIER',      -700.00,'FR7630001007941234567890185','2026-02-01','2026-02-28',    2),
  ('2026-02-05','REMB MUTUELLE',        35.00,'FR7630001007941234567890185','2026-02-01','2026-02-28', NULL),
  ('2026-02-14','CARREFOUR MARKET',    -61.20,'FR7630001007941234567890185','2026-02-01','2026-02-28',    1),
  ('2026-01-05','EDF ELECTRICITE',     -89.00,'FR1420041010050500013M02606','2026-01-01','2026-01-31', NULL),
  ('2026-01-10','NETFLIX',             -13.49,'FR1420041010050500013M02606','2026-01-01','2026-01-31',    6),
  ('2026-01-18','INTERMARCHE',         -78.30,'FR1420041010050500013M02606','2026-01-01','2026-01-31',    5),
  ('2026-01-20','CROUS RESTAURATION',   -3.30,'FR7610107001011234567890129','2026-01-01','2026-01-31',    7),
  ('2026-01-25','FNAC',                -24.90,'FR7610107001011234567890129','2026-01-01','2026-01-31', NULL);


  INSERT INTO operation
  (date_operation, libelle, montant, iban, periode_debut, periode_fin, id_categorie) VALUES
  ('2026-01-19', 'PHARMACIE DU PARC', -18.40, 'FR7630001007941234567890185',
   '2026-01-01', '2026-01-31', NULL);