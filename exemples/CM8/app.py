"""Squelette Flask de l'API de gestion de dépenses (openapi.yaml, v0.1.0).

Toutes les fonctions sont des placeholders : elles renvoient des données
d'exemple avec le code HTTP prévu par la spécification. Chaque `TODO`
indique ce qu'il reste à implémenter.

Lancer :
    pip install -r requirements.txt
    flask --app app run --debug
"""
from functools import wraps
from uuid import UUID

from flask import Blueprint, Flask, jsonify, request
from werkzeug.exceptions import HTTPException

api = Blueprint("api", __name__, url_prefix="/v1")

# --------------------------------------------------------------------------
# Données d'exemple (placeholders)
# --------------------------------------------------------------------------

SAMPLE_USER_ID = "11111111-1111-4111-8111-111111111111"
SAMPLE_ACCOUNT_ID = "22222222-2222-4222-8222-222222222222"
SAMPLE_STATEMENT_ID = "33333333-3333-4333-8333-333333333333"
SAMPLE_TRANSACTION_ID = "44444444-4444-4444-8444-444444444444"
SAMPLE_CATEGORY_ID = "55555555-5555-4555-8555-555555555555"
NOW = "2026-11-21T16:00:00Z"

SAMPLE_USER = {
    "id": SAMPLE_USER_ID,
    "email": "alice@example.com",
    "displayName": "Alice",
    "createdAt": NOW,
}

SAMPLE_TOKENS = {
    "accessToken": "placeholder.access.token",
    "refreshToken": "placeholder-refresh-token",
    "tokenType": "Bearer",
    "expiresIn": 900,
}

SAMPLE_ACCOUNT = {
    "id": SAMPLE_ACCOUNT_ID,
    "ownerId": SAMPLE_USER_ID,
    "name": "Compte courant",
    "iban": "FR7630006000011234567890189",
    "currency": "EUR",
    "role": "OWNER",
    "createdAt": NOW,
}

SAMPLE_STATEMENT = {
    "id": SAMPLE_STATEMENT_ID,
    "accountId": SAMPLE_ACCOUNT_ID,
    "fileName": "releve-2026-10.csv",
    "format": "csv",
    "importedAt": NOW,
    "importedBy": SAMPLE_USER_ID,
    "periodStart": "2026-10-01",
    "periodEnd": "2026-10-31",
    "transactionsImported": 42,
    "duplicatesSkipped": 0,
}

SAMPLE_CATEGORY = {"id": SAMPLE_CATEGORY_ID, "label": "Alimentation"}

SAMPLE_TRANSACTION = {
    "id": SAMPLE_TRANSACTION_ID,
    "accountId": SAMPLE_ACCOUNT_ID,
    "statementId": SAMPLE_STATEMENT_ID,
    "date": "2026-10-12",
    "amount": "-42.50",
    "description": "CARTE 12/10 SUPERMARCHE",
    "counterparty": "Supermarché",
    "category": SAMPLE_CATEGORY,
}

SAMPLE_ACCESS = {
    "userId": "66666666-6666-4666-8666-666666666666",
    "email": "bob@example.com",
    "permission": "READ",
    "grantedAt": NOW,
}


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------


def problem(status, title, detail=None, errors=None):
    """Réponse d'erreur au format RFC 9457 (application/problem+json)."""
    body = {"title": title, "status": status}
    if detail:
        body["detail"] = detail
    if errors:
        body["errors"] = errors
    response = jsonify(body)
    response.status_code = status
    response.content_type = "application/problem+json"
    return response


def require_auth(view):
    """Placeholder d'authentification.

    TODO: vérifier la signature et l'expiration du JWT, puis charger
    l'utilisateur courant (par exemple dans `flask.g`).
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer ") or len(header) <= len("Bearer "):
            return problem(401, "Unauthorized", "Jeton d'accès absent ou invalide.")
        return view(*args, **kwargs)

    return wrapper


def json_body(*required):
    """Retourne (corps JSON, None) ou (None, réponse d'erreur 400).

    TODO: remplacer par une vraie validation de schéma (pydantic, marshmallow…).
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None, problem(400, "Bad Request", "Corps JSON attendu.")
    missing = [f for f in required if f not in body]
    if missing:
        errors = [{"field": f, "message": "Champ obligatoire."} for f in missing]
        return None, problem(400, "Bad Request", "Champs manquants.", errors)
    return body, None


def page_of(items):
    """Enveloppe de pagination (paramètres `page` et `pageSize`)."""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 50, type=int)
    return {
        "page": page,
        "pageSize": page_size,
        "totalItems": len(items),
        "items": items,
    }


def no_content():
    return "", 204


# --------------------------------------------------------------------------
# Utilisateurs et authentification (sans jeton requis)
# --------------------------------------------------------------------------


@api.post("/users")
def register_user():
    # TODO: valider l'e-mail et le mot de passe (8 à 128 caractères), hacher le
    # mot de passe, renvoyer 409 si l'e-mail existe déjà, limiter le débit (429).
    body, error = json_body("email", "password")
    if error:
        return error
    return jsonify({**SAMPLE_USER, "email": body["email"]}), 201


@api.post("/auth/token")
def create_token():
    # TODO: vérifier les identifiants (401 sinon), limiter les tentatives (429),
    # émettre un vrai JWT et un jeton de rafraîchissement.
    _, error = json_body("email", "password")
    if error:
        return error
    return jsonify(SAMPLE_TOKENS), 200


@api.post("/auth/refresh")
def refresh_token():
    # TODO: vérifier le jeton de rafraîchissement (401 sinon) et l'invalider
    # après usage.
    _, error = json_body("refreshToken")
    if error:
        return error
    return jsonify(SAMPLE_TOKENS), 200


# --------------------------------------------------------------------------
# Comptes
# --------------------------------------------------------------------------


@api.get("/accounts")
@require_auth
def list_accounts():
    # TODO: comptes dont l'utilisateur est propriétaire ou bénéficiaire d'un accès.
    return jsonify([SAMPLE_ACCOUNT]), 200


@api.post("/accounts")
@require_auth
def create_account():
    # TODO: persister le compte, l'utilisateur courant en devient propriétaire.
    body, error = json_body("name", "currency")
    if error:
        return error
    return jsonify({**SAMPLE_ACCOUNT, "name": body["name"], "currency": body["currency"]}), 201


@api.get("/accounts/<uuid:account_id>")
@require_auth
def get_account(account_id: UUID):
    # TODO: 403 si pas d'accès, 404 si introuvable.
    return jsonify({**SAMPLE_ACCOUNT, "id": str(account_id)}), 200


@api.delete("/accounts/<uuid:account_id>")
@require_auth
def delete_account(account_id: UUID):
    # TODO: réservé au propriétaire ; suppression en cascade (extraits,
    # transactions, accès).
    return no_content()


# --------------------------------------------------------------------------
# États (dépenses / revenus)
# --------------------------------------------------------------------------


@api.get("/accounts/<uuid:account_id>/summary")
@require_auth
def get_account_summary(account_id: UUID):
    # TODO: agréger les transactions sur la période [from, to], filtrer par
    # `categoryId`, ventiler selon `groupBy` (none | category | month).
    group_by = request.args.get("groupBy", "none")
    summary = {
        "accountId": str(account_id),
        "from": request.args.get("from", "2026-10-01"),
        "to": request.args.get("to", "2026-10-31"),
        "currency": "EUR",
        "totalIncome": "2500.00",
        "totalExpenses": "-1830.40",
        "net": "669.60",
        "breakdown": [],
    }
    if request.args.get("categoryId"):
        summary["categoryId"] = request.args["categoryId"]
    if group_by == "category":
        summary["breakdown"] = [
            {
                "key": SAMPLE_CATEGORY_ID,
                "label": "Alimentation",
                "income": "0.00",
                "expenses": "-420.10",
            }
        ]
    elif group_by == "month":
        summary["breakdown"] = [{"key": "2026-10", "income": "2500.00", "expenses": "-1830.40"}]
    return jsonify(summary), 200


# --------------------------------------------------------------------------
# Extraits de compte
# --------------------------------------------------------------------------


@api.get("/accounts/<uuid:account_id>/statements")
@require_auth
def list_statements(account_id: UUID):
    return jsonify(page_of([{**SAMPLE_STATEMENT, "accountId": str(account_id)}])), 200


@api.post("/accounts/<uuid:account_id>/statements")
@require_auth
def upload_statement(account_id: UUID):
    # TODO: droit WRITE requis ; lire le CSV / xlsx, créer les transactions,
    # ignorer les doublons ; 413 (trop gros), 415 (format), 422 (contenu invalide).
    uploaded = request.files.get("file")
    if uploaded is None:
        return problem(400, "Bad Request", "Champ de fichier `file` manquant.")
    name = uploaded.filename or "extrait"
    extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if extension not in ("csv", "xlsx"):
        return problem(415, "Unsupported Media Type", "Formats acceptés : csv, xlsx.")
    return jsonify({**SAMPLE_STATEMENT, "accountId": str(account_id),
                    "fileName": name, "format": extension}), 201


@api.get("/accounts/<uuid:account_id>/statements/<uuid:statement_id>")
@require_auth
def get_statement(account_id: UUID, statement_id: UUID):
    return jsonify({**SAMPLE_STATEMENT, "id": str(statement_id),
                    "accountId": str(account_id)}), 200


@api.delete("/accounts/<uuid:account_id>/statements/<uuid:statement_id>")
@require_auth
def delete_statement(account_id: UUID, statement_id: UUID):
    # TODO: droit WRITE requis ; supprimer aussi les transactions de l'extrait.
    return no_content()


# --------------------------------------------------------------------------
# Transactions
# --------------------------------------------------------------------------


@api.get("/accounts/<uuid:account_id>/transactions")
@require_auth
def list_transactions(account_id: UUID):
    # TODO: filtres from, to, categoryId, uncategorized, statementId, type.
    return jsonify(page_of([{**SAMPLE_TRANSACTION, "accountId": str(account_id)}])), 200


@api.get("/accounts/<uuid:account_id>/transactions/<uuid:transaction_id>")
@require_auth
def get_transaction(account_id: UUID, transaction_id: UUID):
    return jsonify({**SAMPLE_TRANSACTION, "id": str(transaction_id),
                    "accountId": str(account_id)}), 200


@api.get("/accounts/<uuid:account_id>/transactions/<uuid:transaction_id>/category")
@require_auth
def get_transaction_category(account_id: UUID, transaction_id: UUID):
    # TODO: 404 si la transaction n'a pas de catégorie.
    return jsonify(SAMPLE_CATEGORY), 200


@api.put("/accounts/<uuid:account_id>/transactions/<uuid:transaction_id>/category")
@require_auth
def set_transaction_category(account_id: UUID, transaction_id: UUID):
    # TODO: droit WRITE requis ; vérifier que la catégorie existe.
    body, error = json_body("categoryId")
    if error:
        return error
    category = {**SAMPLE_CATEGORY, "id": body["categoryId"]}
    return jsonify({**SAMPLE_TRANSACTION, "id": str(transaction_id),
                    "accountId": str(account_id), "category": category}), 200


@api.delete("/accounts/<uuid:account_id>/transactions/<uuid:transaction_id>/category")
@require_auth
def clear_transaction_category(account_id: UUID, transaction_id: UUID):
    # TODO: droit WRITE requis.
    return no_content()


# --------------------------------------------------------------------------
# Catégories
# --------------------------------------------------------------------------


@api.get("/categories")
@require_auth
def list_categories():
    return jsonify([SAMPLE_CATEGORY]), 200


@api.post("/categories")
@require_auth
def create_category():
    # TODO: 409 si le libellé existe déjà pour cet utilisateur.
    body, error = json_body("label")
    if error:
        return error
    return jsonify({**SAMPLE_CATEGORY, "label": body["label"]}), 201


@api.patch("/categories/<uuid:category_id>")
@require_auth
def update_category(category_id: UUID):
    # TODO: 404 si introuvable, 409 si le libellé existe déjà.
    body, error = json_body("label")
    if error:
        return error
    return jsonify({"id": str(category_id), "label": body["label"]}), 200


@api.delete("/categories/<uuid:category_id>")
@require_auth
def delete_category(category_id: UUID):
    # TODO: les transactions concernées deviennent « non catégorisées ».
    return no_content()


# --------------------------------------------------------------------------
# Accès aux comptes
# --------------------------------------------------------------------------


@api.get("/accounts/<uuid:account_id>/access")
@require_auth
def list_account_access(account_id: UUID):
    # TODO: réservé au propriétaire.
    return jsonify([SAMPLE_ACCESS]), 200


@api.post("/accounts/<uuid:account_id>/access")
@require_auth
def grant_account_access(account_id: UUID):
    # TODO: réservé au propriétaire ; retrouver l'utilisateur par e-mail ;
    # remplacer l'accès existant le cas échéant.
    body, error = json_body("email", "permission")
    if error:
        return error
    if body["permission"] not in ("READ", "WRITE"):
        return problem(400, "Bad Request", "`permission` doit valoir READ ou WRITE.")
    return jsonify({**SAMPLE_ACCESS, "email": body["email"],
                    "permission": body["permission"]}), 201


@api.delete("/accounts/<uuid:account_id>/access/<uuid:user_id>")
@require_auth
def revoke_account_access(account_id: UUID, user_id: UUID):
    # TODO: réservé au propriétaire.
    return no_content()


# --------------------------------------------------------------------------
# Application
# --------------------------------------------------------------------------


def create_app() -> Flask:
    app = Flask(__name__)
    # Limite de taille des fichiers importés (réponse 413 au-delà).
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return problem(error.code or 500, error.name, error.description)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
