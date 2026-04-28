from datetime import date, datetime


def calculer_jours_restants(date_peremption):
    """Retourne le nombre de jours avant la péremption. Négatif = déjà expiré."""
    date_exp = datetime.strptime(date_peremption, "%Y-%m-%d").date()
    return (date_exp - date.today()).days


def definir_statut(jours):
    """Retourne 'rouge', 'jaune' ou 'vert' selon les jours restants."""
    if jours <= 0:
        return "rouge"   # expiré
    elif jours <= 3:
        return "jaune"   # expire bientôt
    else:
        return "vert"    # ok


def analyser_produit(produit):
    """
    Prend un produit et lui ajoute ses jours restants et son statut.

    Entrée :  {"nom": "Yaourt", "date_peremption": "2026-04-24"}
    Sortie :  {"nom": "Yaourt", "date_peremption": "2026-04-24",
               "jours_restants": 3, "statut": "jaune"}
    """
    jours = calculer_jours_restants(produit["date_peremption"])
    produit["jours_restants"] = jours
    produit["statut"] = definir_statut(jours)
    return produit


def trier_par_priorite(produits):
    """Trie la liste du plus urgent (rouge) au moins urgent (vert)."""
    for p in produits:
        analyser_produit(p)
    return sorted(produits, key=lambda p: p["jours_restants"])


def a_consommer_aujourd_hui(produits):
    """Retourne uniquement les produits rouges et jaunes (les urgents)."""
    resultats = []
    for p in produits:
        analyser_produit(p)
        if p["statut"] in ("rouge", "jaune"):
            resultats.append(p)
    return sorted(resultats, key=lambda p: p["jours_restants"])