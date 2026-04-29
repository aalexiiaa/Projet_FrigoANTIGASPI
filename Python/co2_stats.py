from datetime import date
from collections import defaultdict

# Facteurs d'emission moyens par produit alimentaire, en kg CO2e par unite.
# Ces valeurs sont volontairement simples pour rester compatibles avec le projet et faciles a justifier en presentation.
FACTEURS_CO2_KG = {
    "boeuf": 25.0,
    "bœuf": 25.0,
    "viande": 15.0,
    "poulet": 6.0,
    "poisson": 5.0,
    "fromage": 8.0,
    "lait": 1.2,
    "yaourt": 1.0,
    "oeuf": 0.5,
    "œuf": 0.5,
    "pain": 0.8,
    "riz": 2.7,
    "pates": 1.6,
    "pâtes": 1.6,
    "legume": 0.5,
    "légume": 0.5,
    "fruit": 0.4,
    "salade": 0.3,
}

FACTEUR_CO2_PAR_DEFAUT_KG = 2.5


def normaliser_nom(nom_produit):
    """Nettoie un nom de produit pour faciliter la recherche du facteur CO2."""
    return (nom_produit or "").strip().lower()


def trouver_facteur_co2(nom_produit):
    """
    Retourne le facteur CO2 le plus pertinent pour un produit.
    Si aucun mot-cle n'est reconnu, on utilise un facteur moyen par defaut.
    """
    nom = normaliser_nom(nom_produit)

    for mot_cle, facteur in FACTEURS_CO2_KG.items():
        if mot_cle in nom:
            return facteur

    return FACTEUR_CO2_PAR_DEFAUT_KG


def calculer_co2_economise(nom_produit, quantite=1):
    """Calcule le CO2 economise lorsqu'un produit est consomme au lieu d'etre jete."""
    quantite = quantite or 1
    facteur = trouver_facteur_co2(nom_produit)
    return round(float(quantite) * facteur, 2)


def mois_fr(date_valeur=None):
    """Retourne une cle AAAA-MM pour les statistiques mensuelles."""
    date_valeur = date_valeur or date.today()
    return date_valeur.strftime("%Y-%m")


def construire_stats_depuis_historique(historique):
    """
    Agrege une liste d'objets HistoriqueProduit.
    Sortie prevue pour alimenter des cartes statistiques, graphiques et rapports.
    """
    total_produits = 0
    total_co2 = 0.0
    par_mois = defaultdict(lambda: {"produits_sauves": 0, "co2_economise_kg": 0.0})
    par_produit = defaultdict(lambda: {"produits_sauves": 0, "co2_economise_kg": 0.0})

    for ligne in historique:
        quantite = getattr(ligne, "quantite", 1) or 1
        co2 = getattr(ligne, "co2_economise_kg", None)
        if co2 is None:
            co2 = calculer_co2_economise(getattr(ligne, "nom", ""), quantite)

        nom = getattr(ligne, "nom", "Produit") or "Produit"
        date_conso = getattr(ligne, "consomme_le", None) or date.today()
        mois = mois_fr(date_conso)

        total_produits += quantite
        total_co2 += float(co2)

        par_mois[mois]["produits_sauves"] += quantite
        par_mois[mois]["co2_economise_kg"] += float(co2)

        par_produit[nom]["produits_sauves"] += quantite
        par_produit[nom]["co2_economise_kg"] += float(co2)

    return {
        "produits_sauves": total_produits,
        "co2_economise_kg": round(total_co2, 2),
        "par_mois": [
            {
                "mois": mois,
                "produits_sauves": valeurs["produits_sauves"],
                "co2_economise_kg": round(valeurs["co2_economise_kg"], 2),
            }
            for mois, valeurs in sorted(par_mois.items())
        ],
        "par_produit": [
            {
                "nom": nom,
                "produits_sauves": valeurs["produits_sauves"],
                "co2_economise_kg": round(valeurs["co2_economise_kg"], 2),
            }
            for nom, valeurs in sorted(
                par_produit.items(),
                key=lambda item: item[1]["co2_economise_kg"],
                reverse=True,
            )
        ],
    }


def generer_rapport_mensuel(historique, mois=None):
    """Prepare un rapport mensuel texte a partir de l'historique d'utilisation."""
    mois = mois or mois_fr()
    lignes_mois = [
        ligne for ligne in historique
        if mois_fr(getattr(ligne, "consomme_le", None) or date.today()) == mois
    ]
    stats = construire_stats_depuis_historique(lignes_mois)

    lignes = [
        f"Rapport mensuel Frigo Anti-Gaspi - {mois}",
        "",
        f"Produits sauves : {stats['produits_sauves']}",
        f"CO2 economise : {stats['co2_economise_kg']} kg CO2e",
        "",
        "Detail par produit :",
    ]

    if not stats["par_produit"]:
        lignes.append("- Aucun produit consomme sur cette periode.")
    else:
        for item in stats["par_produit"]:
            lignes.append(
                f"- {item['nom']} : {item['produits_sauves']} produit(s), "
                f"{item['co2_economise_kg']} kg CO2e economises"
            )

    return "\n".join(lignes)
