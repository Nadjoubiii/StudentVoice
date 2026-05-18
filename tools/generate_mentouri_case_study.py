import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import database as db

CASE_TAG = "[Mentouri Case Study]"


def _mentouri_university_id(conn):
    row = conn.execute(
        """
        SELECT id FROM universities
        WHERE short_name = 'UMC1' OR name LIKE '%Mentouri%'
        ORDER BY id
        LIMIT 1
        """
    ).fetchone()
    if not row:
        raise RuntimeError("Could not find Universite des Freres Mentouri (UMC1) in universities table.")
    return row[0]


def generate_reports(count=25):
    db.init_db()
    conn = db.get_connection()
    c = conn.cursor()

    uid = _mentouri_university_id(conn)

    # Keep regeneration deterministic and clean by removing previous tagged case-study reports.
    c.execute("DELETE FROM reports WHERE university_id = ? AND title LIKE ?", (uid, f"%{CASE_TAG}%"))

    templates = [
        {
            "title": "Pannes d'eau chaude recurrentes a la residence Garidi",
            "description": "Plusieurs blocs de la residence affichent une absence d'eau chaude en soiree, surtout pendant les periodes de froid.",
            "location_type": "Résidence universitaire (Cité U)",
            "category": "🛏️ Hébergement & Résidences",
            "subcategory": "Eau chaude absente",
            "severity": 4,
        },
        {
            "title": "Surcharge des bus universitaires sur la ligne Mentouri-Campus",
            "description": "Aux heures de pointe, les bus sont pleins et des etudiants ratent les cours faute de place.",
            "location_type": "Transport universitaire",
            "category": "🚌 Transport",
            "subcategory": "Surcharge des bus",
            "severity": 3,
        },
        {
            "title": "WiFi instable dans le bloc des sciences economiques",
            "description": "Le reseau coupe toutes les 10 a 15 minutes, bloquant l'acces aux plateformes de cours et aux supports numeriques.",
            "location_type": "Amphithéâtre / Salle de cours",
            "category": "📡 Connectivité & Internet",
            "subcategory": "WiFi défaillant",
            "severity": 3,
        },
        {
            "title": "Toilettes hors service pres de l'amphi principal",
            "description": "La majorite des sanitaires sont fermes ou bouches, avec une odeur persistante et un manque d'entretien evident.",
            "location_type": "Amphithéâtre / Salle de cours",
            "category": "🚽 Hygiène & Assainissement",
            "subcategory": "Toilettes et sanitaires",
            "severity": 4,
        },
        {
            "title": "Fuites au plafond dans un couloir pedagogique",
            "description": "En cas de pluie, l'eau s'accumule au sol et cree un risque de glissade pour les etudiants.",
            "location_type": "Amphithéâtre / Salle de cours",
            "category": "🏗️ Infrastructures",
            "subcategory": "Toiture et murs",
            "severity": 4,
        },
        {
            "title": "Qualite des repas en baisse au RU du campus central",
            "description": "Les portions sont reduites et plusieurs etudiants signalent des repas froids et repetitifs.",
            "location_type": "Restaurant universitaire (RU)",
            "category": "🍽️ Alimentation & Restauration",
            "subcategory": "Qualite des repas",
            "severity": 3,
        },
        {
            "title": "Eclairage insuffisant aux abords de la cite universitaire",
            "description": "Certaines zones restent tres sombres apres 19h, ce qui augmente le sentiment d'insecurite.",
            "location_type": "Espace extérieur / Campus",
            "category": "🔒 Sécurité",
            "subcategory": "Éclairage insuffisant",
            "severity": 4,
        },
        {
            "title": "Ordinateurs en panne dans le laboratoire informatique",
            "description": "Une part importante des postes ne demarre pas ou plante pendant les TP, ralentissant le travail des groupes.",
            "location_type": "Laboratoire",
            "category": "📚 Équipements Pédagogiques",
            "subcategory": "Matériel informatique",
            "severity": 4,
        },
        {
            "title": "Retard de delivrance des attestations administratives",
            "description": "Les attestations d'inscription et releves sont souvent delivres avec plusieurs semaines de retard.",
            "location_type": "Administration",
            "category": "📋 Administration",
            "subcategory": "Retard dans les documents",
            "severity": 3,
        },
        {
            "title": "Coupures d'electricite pendant les seances de TP",
            "description": "Les coupures repetitives interrompent les manipulations et peuvent endommager les equipements sensibles.",
            "location_type": "Laboratoire",
            "category": "⚡ Eau & Électricité",
            "subcategory": "Coupures d'électricité",
            "severity": 4,
        },
    ]

    statuses = [
        "Signalé",
        "Signalé",
        "Signalé",
        "En cours d'examen",
        "En cours de résolution",
        "Résolu",
    ]
    status_weights = [35, 25, 15, 12, 8, 5]

    for i in range(count):
        t = templates[i % len(templates)]
        days_ago = random.randint(0, 120)
        ts = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        upvotes = random.randint(4, 95)

        title = f"{t['title']} ({CASE_TAG} #{i + 1})"
        description = (
            f"{t['description']} "
            "Signalement de cas d'etude concentre sur l'Universite des Freres Mentouri (UMC1), Constantine."
        )

        c.execute(
            """
            INSERT INTO reports
            (created_at, university_id, location_type, category, subcategory,
             severity, title, description, is_anonymous, status, upvotes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                uid,
                t["location_type"],
                t["category"],
                t["subcategory"],
                t["severity"],
                title,
                description,
                1,
                status,
                upvotes,
            ),
        )

    conn.commit()

    total = c.execute(
        "SELECT COUNT(*) FROM reports WHERE university_id = ? AND title LIKE ?",
        (uid, f"%{CASE_TAG}%"),
    ).fetchone()[0]

    conn.close()
    print(f"Inserted Mentouri case-study reports: {total}")


if __name__ == "__main__":
    random.seed(2026)
    generate_reports(count=25)
