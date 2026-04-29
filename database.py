"""
database.py – Data layer for Sawt Taleb (صوت الطالب)
All SQLite operations, seed data, and analytics queries.
"""

import sqlite3
import os
import random
import hashlib
from datetime import datetime, timedelta

DB_PATH = "sawt_taleb.db"

# ─────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────

UNIVERSITIES = [
    # Alger
    {"name": "Université d'Alger 1 – Benyoucef Benkhedda",          "short": "UA1",    "wilaya": "Alger",          "city": "Alger",          "type": "Université"},
    {"name": "Université d'Alger 2 – Abou El Kacem Saâdallah",       "short": "UA2",    "wilaya": "Alger",          "city": "Alger",          "type": "Université"},
    {"name": "Université d'Alger 3",                                  "short": "UA3",    "wilaya": "Alger",          "city": "Alger",          "type": "Université"},
    {"name": "USTHB – Université des Sciences et Technologie H.B.",   "short": "USTHB",  "wilaya": "Alger",          "city": "Bab Ezzouar",    "type": "Université"},
    {"name": "École Nationale Polytechnique (ENP)",                   "short": "ENP",    "wilaya": "Alger",          "city": "El Harrach",     "type": "Grande École"},
    {"name": "École Nationale Supérieure d'Informatique (ESI)",       "short": "ESI",    "wilaya": "Alger",          "city": "Alger",          "type": "Grande École"},
    {"name": "ENSIA – École Nat. Sup. des Industries Alimentaires",   "short": "ENSIA",  "wilaya": "Alger",          "city": "Alger",          "type": "Grande École"},
    {"name": "École Nationale Supérieure Agronomique (ENSA)",         "short": "ENSA",   "wilaya": "Alger",          "city": "El Harrach",     "type": "Grande École"},
    # Constantine
    {"name": "Université des Frères Mentouri – Constantine 1",        "short": "UMC1",   "wilaya": "Constantine",    "city": "Constantine",    "type": "Université"},
    {"name": "Université Abdelhamid Mehri – Constantine 2",           "short": "UMC2",   "wilaya": "Constantine",    "city": "Constantine",    "type": "Université"},
    {"name": "Université Salah Boubnider – Constantine 3",            "short": "UMC3",   "wilaya": "Constantine",    "city": "Constantine",    "type": "Université"},
    # Oran
    {"name": "Université Ahmed Ben Bella – Oran 1",                   "short": "UO1",    "wilaya": "Oran",           "city": "Oran",           "type": "Université"},
    {"name": "Université Mohamed Ben Ahmed – Oran 2",                 "short": "UO2",    "wilaya": "Oran",           "city": "Oran",           "type": "Université"},
    {"name": "USTO – Université des Sciences et Technologie d'Oran",  "short": "USTO",   "wilaya": "Oran",           "city": "Oran",           "type": "Université"},
    # Annaba
    {"name": "Université Badji Mokhtar – Annaba",                     "short": "UBA",    "wilaya": "Annaba",         "city": "Annaba",         "type": "Université"},
    {"name": "École Nat. Sup. des Mines et Métallurgie (ENSMM)",      "short": "ENSMM",  "wilaya": "Annaba",         "city": "Annaba",         "type": "Grande École"},
    # Béjaïa
    {"name": "Université Abderrahmane Mira – Béjaïa",                 "short": "UBBA",   "wilaya": "Béjaïa",         "city": "Béjaïa",         "type": "Université"},
    # Tizi Ouzou
    {"name": "Université Mouloud Mammeri – Tizi Ouzou",               "short": "UMMTO",  "wilaya": "Tizi Ouzou",     "city": "Tizi Ouzou",     "type": "Université"},
    # Sétif
    {"name": "Université Ferhat Abbas – Sétif 1",                     "short": "UFA1",   "wilaya": "Sétif",          "city": "Sétif",          "type": "Université"},
    {"name": "Université Mohamed Lamine Debaghine – Sétif 2",         "short": "UFA2",   "wilaya": "Sétif",          "city": "Sétif",          "type": "Université"},
    # Blida
    {"name": "Université Saad Dahleb – Blida 1",                      "short": "UB1",    "wilaya": "Blida",          "city": "Blida",          "type": "Université"},
    {"name": "Université Lounici Ali – Blida 2",                      "short": "UB2",    "wilaya": "Blida",          "city": "Blida",          "type": "Université"},
    # Batna
    {"name": "Université Hadj Lakhdar – Batna 1",                     "short": "UHB1",   "wilaya": "Batna",          "city": "Batna",          "type": "Université"},
    {"name": "Université Mostefa Ben Boulaid – Batna 2",              "short": "UHB2",   "wilaya": "Batna",          "city": "Batna",          "type": "Université"},
    # Tlemcen
    {"name": "Université Abou Bakr Belkaid – Tlemcen",                "short": "UABB",   "wilaya": "Tlemcen",        "city": "Tlemcen",        "type": "Université"},
    # Biskra
    {"name": "Université Mohamed Khider – Biskra",                    "short": "UMK",    "wilaya": "Biskra",         "city": "Biskra",         "type": "Université"},
    # Jijel
    {"name": "Université Mohamed Seddik Ben Yahia – Jijel",           "short": "UMSBY",  "wilaya": "Jijel",          "city": "Jijel",          "type": "Université"},
    # Médéa
    {"name": "Université Yahia Fares – Médéa",                        "short": "UYF",    "wilaya": "Médéa",          "city": "Médéa",          "type": "Université"},
    # Mostaganem
    {"name": "Université Abdelhamid Ibn Badis – Mostaganem",          "short": "UAIB",   "wilaya": "Mostaganem",     "city": "Mostaganem",     "type": "Université"},
    # M'Sila
    {"name": "Université Mohamed Boudiaf – M'Sila",                   "short": "UMB",    "wilaya": "M'Sila",         "city": "M'Sila",         "type": "Université"},
    # Djelfa
    {"name": "Université Ziane Achour – Djelfa",                      "short": "UZA",    "wilaya": "Djelfa",         "city": "Djelfa",         "type": "Université"},
    # Skikda
    {"name": "Université 20 Août 1955 – Skikda",                      "short": "U20A",   "wilaya": "Skikda",         "city": "Skikda",         "type": "Université"},
    # Guelma
    {"name": "Université 8 Mai 1945 – Guelma",                        "short": "U8M",    "wilaya": "Guelma",         "city": "Guelma",         "type": "Université"},
    # Others
    {"name": "Université de Souk Ahras",                              "short": "USA",    "wilaya": "Souk Ahras",     "city": "Souk Ahras",     "type": "Université"},
    {"name": "Université de Khenchela",                               "short": "UK",     "wilaya": "Khenchela",      "city": "Khenchela",      "type": "Université"},
    {"name": "Université Kasdi Merbah – Ouargla",                     "short": "UKM",    "wilaya": "Ouargla",        "city": "Ouargla",        "type": "Université"},
    {"name": "Université de Ghardaïa",                                "short": "UG",     "wilaya": "Ghardaïa",       "city": "Ghardaïa",       "type": "Université"},
    {"name": "Université de Tamanrasset",                             "short": "UTAM",   "wilaya": "Tamanrasset",    "city": "Tamanrasset",    "type": "Université"},
    {"name": "Université Ahmed Draia – Adrar",                        "short": "UAD",    "wilaya": "Adrar",          "city": "Adrar",          "type": "Université"},
    {"name": "Université El Oued",                                    "short": "UEO",    "wilaya": "El Oued",        "city": "El Oued",        "type": "Université"},
    {"name": "Université Larbi Ben M'Hidi – Oum El Bouaghi",          "short": "ULBM",   "wilaya": "Oum El Bouaghi", "city": "Oum El Bouaghi", "type": "Université"},
    {"name": "Université Chadli Bendjedid – El Tarf",                 "short": "UCB",    "wilaya": "El Tarf",        "city": "El Tarf",        "type": "Université"},
    {"name": "Université de Tébessa",                                 "short": "UTB",    "wilaya": "Tébessa",        "city": "Tébessa",        "type": "Université"},
    {"name": "Université Amar Telidji – Laghouat",                    "short": "UAT",    "wilaya": "Laghouat",       "city": "Laghouat",       "type": "Université"},
    {"name": "Université Ibn Khaldoun – Tiaret",                      "short": "UIK",    "wilaya": "Tiaret",         "city": "Tiaret",         "type": "Université"},
    {"name": "Université Akli Mohand Oulhadj – Bouira",               "short": "UAMO",   "wilaya": "Bouira",         "city": "Bouira",         "type": "Université"},
    {"name": "Université Djilali Bounaama – Khemis Miliana",          "short": "UDBK",   "wilaya": "Aïn Defla",      "city": "Khemis Miliana", "type": "Université"},
    {"name": "Université de Relizane",                                "short": "UREL",   "wilaya": "Relizane",       "city": "Relizane",       "type": "Université"},
    {"name": "Université de Tissemsilt",                              "short": "UTIS",   "wilaya": "Tissemsilt",     "city": "Tissemsilt",     "type": "Université"},
]

CATEGORIES = {
    "🏗️ Infrastructures":            ["Toiture et murs", "Portes et fenêtres", "Sols et escaliers", "Plomberie", "Mobilier cassé", "Autre"],
    "🚽 Hygiène & Assainissement":    ["Toilettes et sanitaires", "Gestion des déchets", "Nuisibles (rats, cafards)", "Propreté générale", "Canalisations bouchées", "Autre"],
    "🍽️ Alimentation & Restauration": ["Qualité des repas", "Quantité insuffisante", "Hygiène de la cuisine", "Horaires de service", "Prix excessifs", "Fermeture non prévue", "Autre"],
    "🛏️ Hébergement & Résidences":   ["Surpopulation", "Mobilier défectueux", "Eau chaude absente", "Chauffage / Climatisation", "Sécurité du dortoir", "Invasion de nuisibles", "Autre"],
    "📚 Équipements Pédagogiques":    ["Équipements de laboratoire", "Bibliothèque", "Matériel informatique", "État des amphithéâtres", "Manque de salles", "Autre"],
    "⚡ Eau & Électricité":           ["Coupures d'eau", "Coupures d'électricité", "Pression insuffisante", "Eau non potable", "Éclairage défaillant", "Autre"],
    "🔒 Sécurité":                    ["Éclairage insuffisant", "Accès non contrôlé", "Incidents violents", "Sorties de secours bloquées", "Absence de gardiens", "Autre"],
    "📡 Connectivité & Internet":     ["WiFi défaillant", "Débit insuffisant", "Réseau indisponible", "Absence de couverture", "Autre"],
    "🚌 Transport":                   ["Bus manquants", "Horaires non respectés", "Surcharge des bus", "Pannes fréquentes", "Itinéraire insuffisant", "Autre"],
    "📋 Administration":              ["Retard dans les documents", "Bureaucratie excessive", "Mauvaise communication", "Problèmes d'inscription", "Autre"],
}

LOCATION_TYPES = [
    "Résidence universitaire (Cité U)",
    "Amphithéâtre / Salle de cours",
    "Laboratoire",
    "Bibliothèque",
    "Restaurant universitaire (RU)",
    "Administration",
    "Installations sportives",
    "Espace extérieur / Campus",
    "Transport universitaire",
    "Autre",
]

SEVERITY_INFO = {
    1: ("Très faible", "🟢", "#22c55e"),
    2: ("Faible",      "🟡", "#84cc16"),
    3: ("Modéré",      "🟠", "#f59e0b"),
    4: ("Grave",       "🔴", "#f97316"),
    5: ("Critique",    "🚨", "#ef4444"),
}

STATUS_OPTIONS = [
    "Signalé",
    "En cours d'examen",
    "En cours de résolution",
    "Résolu",
    "Rejeté",
]

STATUS_COLORS = {
    "Signalé":                "#dc2626",
    "En cours d'examen":      "#ca8a04",
    "En cours de résolution": "#2563eb",
    "Résolu":                 "#16a34a",
    "Rejeté":                 "#6b7280",
}

# ─────────────────────────────────────────────
# SEED REPORT TEMPLATES
# ─────────────────────────────────────────────

SAMPLE_REPORTS = [
    {
        "title": "Fuite de toiture dans l'Amphithéâtre A depuis 3 mois",
        "description": "La toiture de l'amphithéâtre A fuit depuis début octobre. Les étudiants sont contraints d'utiliser des parapluies pendant les cours quand il pleut. Des seaux ont été placés mais la situation empire. Des cours ont déjà été annulés à cause de cela. L'administration a été notifiée plusieurs fois sans résultat.",
        "category": "🏗️ Infrastructures", "subcategory": "Toiture et murs",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 4,
    },
    {
        "title": "Coupure d'eau quotidienne à la Cité Universitaire",
        "description": "Depuis 3 semaines, l'eau est coupée entre 7h et 14h chaque jour. Les étudiants ne peuvent pas se doucher avant les cours. L'administration n'a fourni aucune explication ni calendrier de résolution. Des bouteilles d'eau sont distribuées aléatoirement.",
        "category": "⚡ Eau & Électricité", "subcategory": "Coupures d'eau",
        "location_type": "Résidence universitaire (Cité U)", "severity": 5,
    },
    {
        "title": "Présence de rats dans les chambres du Bloc 3",
        "description": "Des rats ont été aperçus dans plusieurs chambres du Bloc 3. La situation est inacceptable et pose de sérieux risques sanitaires. Les étudiants ont signalé le problème à l'administration il y a 6 semaines sans aucun résultat concret. Des pièges rudimentaires ont été placés par les étudiants eux-mêmes.",
        "category": "🚽 Hygiène & Assainissement", "subcategory": "Nuisibles (rats, cafards)",
        "location_type": "Résidence universitaire (Cité U)", "severity": 5,
    },
    {
        "title": "WiFi inexistant au bloc des sciences depuis 1 mois",
        "description": "Le réseau WiFi de l'université est complètement inaccessible dans tout le bloc des sciences depuis un mois. Les étudiants dépendent de leur 4G personnelle pour accéder aux cours en ligne et aux ressources pédagogiques. Cela coûte cher et ralentit considérablement le travail universitaire.",
        "category": "📡 Connectivité & Internet", "subcategory": "WiFi défaillant",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 3,
    },
    {
        "title": "Restaurant universitaire fermé sans préavis toute la semaine",
        "description": "Le restaurant universitaire est fermé depuis lundi sans aucune annonce préalable. Des centaines d'étudiants, dont beaucoup viennent de loin, se retrouvent sans repas. Aucune solution alternative n'a été proposée par l'administration. Beaucoup d'étudiants boursiers ne peuvent pas se permettre de manger dehors.",
        "category": "🍽️ Alimentation & Restauration", "subcategory": "Fermeture non prévue",
        "location_type": "Restaurant universitaire (RU)", "severity": 4,
    },
    {
        "title": "Toilettes hors service dans le bâtiment central",
        "description": "La majorité des toilettes du bâtiment central sont hors service depuis plus de 10 jours. Seulement 2 cabines fonctionnent pour toute la faculté (environ 800 étudiants). La situation crée de l'insalubrité et un inconfort majeur. Des étudiantes ont déclaré ne plus venir à l'université.",
        "category": "🚽 Hygiène & Assainissement", "subcategory": "Toilettes et sanitaires",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 4,
    },
    {
        "title": "Absence totale de chauffage en hiver à la cité U",
        "description": "Aucun chauffage dans les chambres des résidences universitaires. Les températures nocturnes descendent sous 5°C. Les étudiants dorment avec tous leurs vêtements. L'administration affirme que la réparation est 'en cours' depuis 4 semaines. Plusieurs étudiants ont été malades.",
        "category": "🛏️ Hébergement & Résidences", "subcategory": "Chauffage / Climatisation",
        "location_type": "Résidence universitaire (Cité U)", "severity": 5,
    },
    {
        "title": "Laboratoire informatique avec 70% des PC hors service",
        "description": "Sur les 30 ordinateurs du laboratoire, seulement 9 fonctionnent correctement. Les TP pratiques sont impossibles dans ces conditions. Le matériel n'a pas été renouvelé depuis 2018. Les étudiants sont obligés de partager des postes à 3 ou 4 personnes.",
        "category": "📚 Équipements Pédagogiques", "subcategory": "Matériel informatique",
        "location_type": "Laboratoire", "severity": 4,
    },
    {
        "title": "Bus universitaire absent après 17h – étudiantes en danger",
        "description": "Le bus de transport universitaire arrête de fonctionner à 17h, obligeant des centaines d'étudiants à rentrer par leurs propres moyens jusqu'à 22h ou plus. Cela représente un problème de sécurité grave, surtout pour les étudiantes. Plusieurs incidents ont déjà été signalés.",
        "category": "🚌 Transport", "subcategory": "Horaires non respectés",
        "location_type": "Transport universitaire", "severity": 4,
    },
    {
        "title": "Rampe d'escalier du Bloc B cassée – risque d'accident grave",
        "description": "La rampe de l'escalier principal du bloc B est complètement cassée depuis 2 mois. Des étudiants ont déjà glissé et se sont blessés. La situation est particulièrement dangereuse par temps de pluie. Une personne âgée ou une étudiante enceinte pourrait avoir un accident grave.",
        "category": "🏗️ Infrastructures", "subcategory": "Sols et escaliers",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 4,
    },
    {
        "title": "Intoxications alimentaires répétées au restaurant universitaire",
        "description": "Plusieurs étudiants ont signalé des intoxications alimentaires après avoir mangé au restaurant universitaire cette semaine. La qualité de la nourriture s'est considérablement dégradée. Des insectes ont été trouvés dans les plats. Une inspection sanitaire urgente est nécessaire.",
        "category": "🍽️ Alimentation & Restauration", "subcategory": "Qualité des repas",
        "location_type": "Restaurant universitaire (RU)", "severity": 5,
    },
    {
        "title": "4 étudiants par chambre – surpopulation inacceptable",
        "description": "Des chambres prévues pour 2 personnes accueillent maintenant 4 étudiants. Il n'y a pas assez d'espace, de lits ni d'armoires. La situation empire chaque année avec l'augmentation des inscriptions sans aucune expansion des capacités d'hébergement. C'est une violation des droits fondamentaux des étudiants.",
        "category": "🛏️ Hébergement & Résidences", "subcategory": "Surpopulation",
        "location_type": "Résidence universitaire (Cité U)", "severity": 4,
    },
    {
        "title": "Bibliothèque fermée pendant toute la période des examens",
        "description": "La bibliothèque universitaire est fermée pendant la période d'examens en raison de travaux de rénovation. Aucun espace de remplacement n'a été proposé. Les étudiants sont obligés de travailler dans des couloirs ou des cafés. C'est une décision absurde et préjudiciable.",
        "category": "📚 Équipements Pédagogiques", "subcategory": "Bibliothèque",
        "location_type": "Bibliothèque", "severity": 3,
    },
    {
        "title": "Coupures d'électricité quotidiennes pendant les TPs",
        "description": "Des coupures d'électricité se produisent plusieurs fois par jour, perturbant les cours et les TPs qui nécessitent des équipements. Le groupe électrogène de secours est en panne depuis 6 mois. Des données de projets sont perdues à chaque coupure.",
        "category": "⚡ Eau & Électricité", "subcategory": "Coupures d'électricité",
        "location_type": "Laboratoire", "severity": 4,
    },
    {
        "title": "Murs couverts de moisissures dans les chambres de la résidence",
        "description": "Les murs des chambres de la résidence sont couverts de moisissures noires en raison de l'humidité chronique. Plusieurs étudiants ont développé des problèmes respiratoires et des allergies. La situation empire en hiver avec le froid et l'absence de ventilation.",
        "category": "🏗️ Infrastructures", "subcategory": "Toiture et murs",
        "location_type": "Résidence universitaire (Cité U)", "severity": 4,
    },
    {
        "title": "Retard de 2 mois pour les attestations d'inscription",
        "description": "Les étudiants attendent depuis 2 mois leurs attestations d'inscription nécessaires pour leurs dossiers bancaires, logement et visa. L'administration invoque des 'problèmes techniques' récurrents. Des étudiants ont raté des échéances administratives importantes à cause de cela.",
        "category": "📋 Administration", "subcategory": "Retard dans les documents",
        "location_type": "Administration", "severity": 3,
    },
    {
        "title": "Eau jaunâtre et malodorante aux fontaines du campus",
        "description": "L'eau des fontaines du campus est jaunâtre et dégage une odeur suspecte. Les étudiants sont obligés d'acheter de l'eau en bouteille, ce qui représente une dépense supplémentaire non négligeable pour des boursiers. Des analyses informelles suggèrent une contamination.",
        "category": "⚡ Eau & Électricité", "subcategory": "Eau non potable",
        "location_type": "Espace extérieur / Campus", "severity": 5,
    },
    {
        "title": "Décharge sauvage à l'entrée principale depuis 2 semaines",
        "description": "Les poubelles ne sont pas collectées depuis 2 semaines. Des montagnes de déchets s'accumulent à l'entrée principale, créant des odeurs nauséabondes et des risques sanitaires évidents. Des nuisibles ont été observés. L'image de l'université est ternie.",
        "category": "🚽 Hygiène & Assainissement", "subcategory": "Gestion des déchets",
        "location_type": "Espace extérieur / Campus", "severity": 4,
    },
    {
        "title": "Sortie de secours du 2ème étage bloquée par du matériel stocké",
        "description": "La sortie de secours du 2ème étage est bloquée par des meubles et du matériel de stockage empilés. En cas d'incendie ou d'urgence, cette situation pourrait être catastrophique. C'est une violation flagrante des normes de sécurité incendie.",
        "category": "🔒 Sécurité", "subcategory": "Sorties de secours bloquées",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 5,
    },
    {
        "title": "Pas de réseau internet au bloc de droit depuis 1 mois",
        "description": "Le bloc de droit est sans connexion internet depuis un mois. Les étudiants ne peuvent pas accéder à la plateforme pédagogique, aux cours en ligne ni effectuer leurs recherches. Le délai de résolution communiqué était 'dans 48h' il y a 3 semaines.",
        "category": "📡 Connectivité & Internet", "subcategory": "Réseau indisponible",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 4,
    },
    {
        "title": "Absence de gardiens la nuit à la cité universitaire",
        "description": "La sécurité nocturne de la cité universitaire est inexistante. Des inconnus entrent librement dans les résidences la nuit. Des vols ont déjà été signalés. Les étudiantes se sentent particulièrement vulnérables et plusieurs ont demandé à leurs parents de les ramener à la maison.",
        "category": "🔒 Sécurité", "subcategory": "Absence de gardiens",
        "location_type": "Résidence universitaire (Cité U)", "severity": 5,
    },
    {
        "title": "Bus bondés – étudiants ne peuvent pas monter",
        "description": "Les bus universitaires sont systématiquement bondés aux heures de pointe. Des étudiants restent à l'arrêt pendant 1h à 2h sans pouvoir monter. Le nombre de bus n'a pas augmenté alors que les effectifs étudiants ont doublé en 5 ans.",
        "category": "🚌 Transport", "subcategory": "Surcharge des bus",
        "location_type": "Transport universitaire", "severity": 3,
    },
    {
        "title": "Portes des salles de TP qui ne ferment plus à clé",
        "description": "Les serrures des salles de TP sont hors service depuis 3 mois. Le matériel informatique et scientifique coûteux est accessible à tous, sans aucune protection. Des équipements ont déjà disparu. L'université refuse d'assumer la responsabilité.",
        "category": "🔒 Sécurité", "subcategory": "Accès non contrôlé",
        "location_type": "Laboratoire", "severity": 3,
    },
    {
        "title": "Amphi surchargé – 400 étudiants pour une salle de 150",
        "description": "L'amphithéâtre principal accueille 400 étudiants pour une capacité maximale de 150. Des étudiants s'assoient par terre dans les allées et dehors. La qualité audio est nulle pour ceux qui sont loin. Les examens dans ces conditions sont une catastrophe.",
        "category": "📚 Équipements Pédagogiques", "subcategory": "Manque de salles",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 4,
    },
    {
        "title": "Douches non fonctionnelles au bloc résidence depuis 3 semaines",
        "description": "Les douches des blocs B et C de la résidence sont hors service depuis 3 semaines. Les étudiants doivent se laver dans des conditions dégradantes. L'administration a promis une réparation 'sous 48h' il y a 15 jours.",
        "category": "🏗️ Infrastructures", "subcategory": "Plomberie",
        "location_type": "Résidence universitaire (Cité U)", "severity": 4,
    },
    {
        "title": "Cours suspendus – pas de chauffage dans les salles en décembre",
        "description": "Suite à une panne du système de chauffage central, plusieurs salles de cours sont inutilisables en hiver. Des professeurs refusent de dispenser leurs cours dans ces conditions. Les étudiants perdent des semaines entières de formation.",
        "category": "🏗️ Infrastructures", "subcategory": "Plomberie",
        "location_type": "Amphithéâtre / Salle de cours", "severity": 3,
    },
]

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables, insert universities, and seed sample data if needed."""
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS universities (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            short_name TEXT,
            wilaya     TEXT NOT NULL,
            city       TEXT,
            type       TEXT DEFAULT 'Université'
        );

        CREATE TABLE IF NOT EXISTS reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at    TEXT DEFAULT (datetime('now','localtime')),
            university_id INTEGER NOT NULL,
            location_type TEXT NOT NULL,
            category      TEXT NOT NULL,
            subcategory   TEXT,
            severity      INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 5),
            title         TEXT NOT NULL,
            description   TEXT NOT NULL,
            reporter_name TEXT,
            reporter_email TEXT,
            is_anonymous  INTEGER DEFAULT 1,
            status        TEXT DEFAULT 'Signalé',
            upvotes       INTEGER DEFAULT 0,
            FOREIGN KEY (university_id) REFERENCES universities(id)
        );

        CREATE TABLE IF NOT EXISTS report_images (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id   INTEGER NOT NULL,
            image_data  TEXT NOT NULL,
            caption     TEXT,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        );

        CREATE TABLE IF NOT EXISTS upvote_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id   INTEGER NOT NULL,
            session_hash TEXT NOT NULL,
            UNIQUE(report_id, session_hash),
            FOREIGN KEY (report_id) REFERENCES reports(id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id      INTEGER NOT NULL,
            comment_text   TEXT NOT NULL,
            commenter_name TEXT DEFAULT 'Anonyme',
            created_at     TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (report_id) REFERENCES reports(id)
        );

        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
    """)

    # Populate universities once
    uni_count = c.execute("SELECT COUNT(*) FROM universities").fetchone()[0]
    if uni_count == 0:
        for u in UNIVERSITIES:
            c.execute(
                "INSERT INTO universities (name, short_name, wilaya, city, type) VALUES (?,?,?,?,?)",
                (u["name"], u["short"], u["wilaya"], u["city"], u["type"]),
            )

    # Seed sample data once
    seeded = c.execute("SELECT value FROM meta WHERE key='seeded'").fetchone()
    if not seeded:
        _seed_sample_data(c)
        c.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('seeded','1')")

    conn.commit()
    conn.close()


def _seed_sample_data(c):
    """Insert realistic sample reports spread over the last 180 days."""
    random.seed(42)
    uni_ids = [row[0] for row in c.execute("SELECT id FROM universities").fetchall()]
    statuses = ["Signalé", "Signalé", "Signalé", "En cours d'examen",
                "En cours de résolution", "Résolu", "Rejeté"]

    for i in range(120):
        template = SAMPLE_REPORTS[i % len(SAMPLE_REPORTS)]
        days_ago  = random.randint(0, 180)
        ts        = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        uid       = random.choice(uni_ids)
        upvotes   = random.randint(0, 87)
        status    = random.choices(statuses, weights=[30, 30, 20, 5, 5, 8, 2])[0]
        # Vary title slightly
        title = template["title"]
        if i >= len(SAMPLE_REPORTS):
            title = title + f" (Cas #{i+1})"
        c.execute(
            """INSERT INTO reports
               (created_at, university_id, location_type, category, subcategory,
                severity, title, description, is_anonymous, status, upvotes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (ts, uid, template["location_type"], template["category"],
             template["subcategory"], template["severity"], title,
             template["description"], 1, status, upvotes),
        )


# ─────────────────────────────────────────────
# UNIVERSITIES
# ─────────────────────────────────────────────

def get_universities():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM universities ORDER BY wilaya, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_university_by_id(uid):
    conn = get_connection()
    row = conn.execute("SELECT * FROM universities WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─────────────────────────────────────────────
# REPORTS – CRUD
# ─────────────────────────────────────────────

def add_report(university_id, location_type, category, subcategory,
               severity, title, description,
               reporter_name=None, reporter_email=None, is_anonymous=True):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO reports
           (university_id, location_type, category, subcategory,
            severity, title, description, reporter_name, reporter_email, is_anonymous)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (university_id, location_type, category, subcategory,
         severity, title, description,
         reporter_name, reporter_email, int(is_anonymous)),
    )
    report_id = c.lastrowid
    conn.commit()
    conn.close()
    return report_id


def add_images(report_id, images):
    """images: list of (base64_string, caption)"""
    if not images:
        return
    conn = get_connection()
    conn.executemany(
        "INSERT INTO report_images (report_id, image_data, caption) VALUES (?,?,?)",
        [(report_id, img_data, caption) for img_data, caption in images],
    )
    conn.commit()
    conn.close()


def get_reports(university_id=None, category=None, location_type=None,
                min_severity=1, max_severity=5, status=None,
                search_query=None, sort_by="newest", limit=None):
    conn = get_connection()
    sql = """
        SELECT r.*, u.name AS university_name, u.short_name, u.wilaya
        FROM reports r
        JOIN universities u ON r.university_id = u.id
        WHERE r.severity BETWEEN ? AND ?
    """
    params = [min_severity, max_severity]

    if university_id:
        sql += " AND r.university_id = ?"
        params.append(university_id)
    if category:
        sql += " AND r.category = ?"
        params.append(category)
    if location_type:
        sql += " AND r.location_type = ?"
        params.append(location_type)
    if status:
        sql += " AND r.status = ?"
        params.append(status)
    if search_query:
        sql += " AND (r.title LIKE ? OR r.description LIKE ?)"
        q = f"%{search_query}%"
        params += [q, q]

    order = {
        "newest":      "r.created_at DESC",
        "oldest":      "r.created_at ASC",
        "most_voted":  "r.upvotes DESC",
        "severity":    "r.severity DESC",
    }.get(sort_by, "r.created_at DESC")

    sql += f" ORDER BY {order}"
    if limit:
        sql += f" LIMIT {int(limit)}"

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_report_by_id(report_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT r.*, u.name AS university_name, u.short_name, u.wilaya "
        "FROM reports r JOIN universities u ON r.university_id=u.id WHERE r.id=?",
        (report_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_images_for_report(report_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT image_data, caption FROM report_images WHERE report_id=? ORDER BY id",
        (report_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_report_status(report_id, new_status):
    conn = get_connection()
    conn.execute("UPDATE reports SET status=? WHERE id=?", (new_status, report_id))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# UPVOTES
# ─────────────────────────────────────────────

def has_upvoted(report_id, session_hash):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM upvote_sessions WHERE report_id=? AND session_hash=?",
        (report_id, session_hash),
    ).fetchone()
    conn.close()
    return row is not None


def toggle_upvote(report_id, session_hash):
    """Returns new upvote count."""
    conn = get_connection()
    c = conn.cursor()
    already = c.execute(
        "SELECT 1 FROM upvote_sessions WHERE report_id=? AND session_hash=?",
        (report_id, session_hash),
    ).fetchone()

    if already:
        c.execute(
            "DELETE FROM upvote_sessions WHERE report_id=? AND session_hash=?",
            (report_id, session_hash),
        )
        c.execute("UPDATE reports SET upvotes = MAX(0, upvotes-1) WHERE id=?", (report_id,))
    else:
        c.execute(
            "INSERT OR IGNORE INTO upvote_sessions (report_id, session_hash) VALUES (?,?)",
            (report_id, session_hash),
        )
        c.execute("UPDATE reports SET upvotes = upvotes+1 WHERE id=?", (report_id,))

    count = c.execute("SELECT upvotes FROM reports WHERE id=?", (report_id,)).fetchone()[0]
    conn.commit()
    conn.close()
    return count


# ─────────────────────────────────────────────
# COMMENTS
# ─────────────────────────────────────────────

def add_comment(report_id, comment_text, commenter_name="Anonyme"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO comments (report_id, comment_text, commenter_name) VALUES (?,?,?)",
        (report_id, comment_text, commenter_name),
    )
    conn.commit()
    conn.close()


def get_comments(report_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comments WHERE report_id=? ORDER BY created_at DESC",
        (report_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────

def get_platform_stats():
    conn = get_connection()
    total     = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    resolved  = conn.execute("SELECT COUNT(*) FROM reports WHERE status='Résolu'").fetchone()[0]
    unis      = conn.execute("SELECT COUNT(DISTINCT university_id) FROM reports").fetchone()[0]
    avg_sev   = conn.execute("SELECT AVG(severity) FROM reports").fetchone()[0] or 0
    pending   = conn.execute("SELECT COUNT(*) FROM reports WHERE status='Signalé'").fetchone()[0]
    conn.close()
    return {"total": total, "resolved": resolved, "universities": unis,
            "avg_severity": round(avg_sev, 2), "pending": pending}


def get_category_breakdown(university_id=None):
    conn = get_connection()
    sql = "SELECT category, COUNT(*) as count FROM reports"
    params = []
    if university_id:
        sql += " WHERE university_id=?"
        params.append(university_id)
    sql += " GROUP BY category ORDER BY count DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_severity_breakdown(university_id=None):
    conn = get_connection()
    sql = "SELECT severity, COUNT(*) as count FROM reports"
    params = []
    if university_id:
        sql += " WHERE university_id=?"
        params.append(university_id)
    sql += " GROUP BY severity ORDER BY severity"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_status_breakdown(university_id=None):
    conn = get_connection()
    sql = "SELECT status, COUNT(*) as count FROM reports"
    params = []
    if university_id:
        sql += " WHERE university_id=?"
        params.append(university_id)
    sql += " GROUP BY status"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_location_breakdown(university_id=None):
    conn = get_connection()
    sql = "SELECT location_type, COUNT(*) as count FROM reports"
    params = []
    if university_id:
        sql += " WHERE university_id=?"
        params.append(university_id)
    sql += " GROUP BY location_type ORDER BY count DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_timeline_data(university_id=None, days=180):
    conn = get_connection()
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    sql = """
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM reports WHERE created_at >= ?
    """
    params = [cutoff]
    if university_id:
        sql += " AND university_id=?"
        params.append(university_id)
    sql += " GROUP BY month ORDER BY month"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_university_stats(university_id):
    conn = get_connection()
    total   = conn.execute("SELECT COUNT(*) FROM reports WHERE university_id=?", (university_id,)).fetchone()[0]
    open_r  = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE university_id=? AND status NOT IN ('Résolu','Rejeté')",
        (university_id,),
    ).fetchone()[0]
    resolved = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE university_id=? AND status='Résolu'",
        (university_id,),
    ).fetchone()[0]
    avg_sev = conn.execute(
        "SELECT AVG(severity) FROM reports WHERE university_id=?",
        (university_id,),
    ).fetchone()[0] or 0
    top_cat = conn.execute(
        "SELECT category, COUNT(*) as c FROM reports WHERE university_id=? GROUP BY category ORDER BY c DESC LIMIT 1",
        (university_id,),
    ).fetchone()
    conn.close()
    return {
        "total": total,
        "open": open_r,
        "resolved": resolved,
        "avg_severity": round(avg_sev, 2),
        "top_category": top_cat["category"] if top_cat else "N/A",
        "resolution_rate": round(resolved / total * 100, 1) if total else 0,
    }


def get_wilaya_breakdown():
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.wilaya, COUNT(r.id) as count
        FROM reports r JOIN universities u ON r.university_id=u.id
        GROUP BY u.wilaya ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_university_ranking():
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.name, u.short_name, u.wilaya,
               COUNT(r.id)                                     AS total,
               AVG(r.severity)                                 AS avg_severity,
               SUM(CASE WHEN r.status='Résolu' THEN 1 ELSE 0 END) AS resolved,
               SUM(CASE WHEN r.status NOT IN ('Résolu','Rejeté') THEN 1 ELSE 0 END) AS open_count
        FROM universities u
        LEFT JOIN reports r ON r.university_id = u.id
        GROUP BY u.id
        HAVING total > 0
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_priority_issues(limit=10):
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*, u.name AS university_name, u.short_name
        FROM reports r JOIN universities u ON r.university_id=u.id
        WHERE r.status NOT IN ('Résolu','Rejeté')
        ORDER BY (r.upvotes * 2 + r.severity * 10) DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
