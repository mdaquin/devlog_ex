
DROP TABLE IF EXISTS operation;
DROP TABLE IF EXISTS releve;
DROP TABLE IF EXISTS categorie;
DROP TABLE IF EXISTS partage;
DROP TABLE IF EXISTS detient;
DROP TABLE IF EXISTS compte;
DROP TABLE IF EXISTS personne;

CREATE TABLE personne (
    id_personne    INT AUTO_INCREMENT PRIMARY KEY,
    nom            VARCHAR(100)  NOT NULL,
    prenom         VARCHAR(100)  NOT NULL,
    courriel       VARCHAR(255)  NOT NULL UNIQUE
);

CREATE TABLE compte (
    iban           VARCHAR(34)   PRIMARY KEY,
    bic            VARCHAR(11),
    intitule       VARCHAR(100)  NOT NULL,
    banque         VARCHAR(100)
);

CREATE TABLE detient (
    id_personne    INT           NOT NULL,
    iban           VARCHAR(34)   NOT NULL,
    PRIMARY KEY (id_personne, iban),
    CONSTRAINT fk_detient_personne FOREIGN KEY (id_personne)
        REFERENCES personne (id_personne),
    CONSTRAINT fk_detient_compte   FOREIGN KEY (iban)
        REFERENCES compte (iban)
);

CREATE TABLE partage (
    id_personne    INT           NOT NULL,
    iban           VARCHAR(34)   NOT NULL,
    droit          VARCHAR(20)   NOT NULL
                   CHECK (droit IN ('lecture', 'ecriture')),
    PRIMARY KEY (id_personne, iban),
    CONSTRAINT fk_partage_personne FOREIGN KEY (id_personne)
        REFERENCES personne (id_personne),
    CONSTRAINT fk_partage_compte   FOREIGN KEY (iban)
        REFERENCES compte (iban)
);

CREATE TABLE categorie (
    id_categorie   INT AUTO_INCREMENT PRIMARY KEY,
    nom            VARCHAR(100)  NOT NULL,
    id_personne    INT           NOT NULL,
    UNIQUE (id_personne, nom),
    CONSTRAINT fk_categorie_personne FOREIGN KEY (id_personne)
        REFERENCES personne (id_personne)
);

CREATE TABLE releve (
    iban           VARCHAR(34)   NOT NULL,
    periode_debut  DATE          NOT NULL,
    periode_fin    DATE          NOT NULL,
    date_import    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (iban, periode_debut, periode_fin),
    CHECK (periode_fin >= periode_debut),
    CONSTRAINT fk_releve_compte FOREIGN KEY (iban)
        REFERENCES compte (iban)
);

CREATE TABLE operation (
    id_operation   INT AUTO_INCREMENT PRIMARY KEY,
    date_operation DATE          NOT NULL,
    libelle        VARCHAR(255)  NOT NULL,
    montant        DECIMAL(12,2) NOT NULL,
    iban           VARCHAR(34)   NOT NULL,
    periode_debut  DATE          NOT NULL,
    periode_fin    DATE          NOT NULL,
    id_categorie   INT           NULL,
    CONSTRAINT fk_operation_releve FOREIGN KEY (iban, periode_debut, periode_fin)
        REFERENCES releve (iban, periode_debut, periode_fin),
    CONSTRAINT fk_operation_categorie FOREIGN KEY (id_categorie)
        REFERENCES categorie (id_categorie)
);