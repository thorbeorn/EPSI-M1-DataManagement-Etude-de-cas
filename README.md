# 📊 **People Analytics – Data Management & Dashboard RH**

### *(Sujet 1 – RH & People Analytics : Focus Sécurité & RGPD)*

Ce projet implémente une chaîne complète de traitement de données RH après fusion d’entreprise, incluant :

✔️ Ingestion et nettoyage d’un fichier CSV mal structuré
✔️ Normalisation et conversions (emails, salaire, dates)
✔️ Sécurisation & anonymisation des données sensibles (hash nom/prénom, masquage NIR)
✔️ Gestion des accès par rôle (Admin / Manager)
✔️ Génération du **dataset Gold** + métadonnées YAML
✔️ Dashboard RH interactif (Plotly)
✔️ Production des fichiers d’analyse (KPI, distributions)
✔️ Documentation Backfill, Gouvernance & RGPD

---

# 🗂️ **Structure du Projet**

```
project/
│
├── data/
│   └── employees_raw.csv        # Fichier CSV d’entrée (source brute)
│
├── output/                      # Tous les fichiers générés automatiquement
│   ├── dashboard_rh.html        # Dashboard RH interactif (ouvrir dans un navigateur)
│   ├── dashboard_rh.png         # Version image du dashboard
│   └── gold_Dataframe_Metadata.yaml  # Métadonnées du dataset GOLD
│
├── main.py                      # Script principal (ETL complet)
├── dashboard.py                 # Génération des dashboards Plotly
├── Backfill & Maintenance.md    # Réponse à la partie 3.2 de l’étude
├── Stratégie & Gouvernance.md   # Réponse à la partie 5 (RGPD & archivage)
├── Data Management - Etude de cas.pdf  # Sujet fourni
│
├── requirements.txt             # Dépendances Python
├── .gitignore                   # Fichiers à ne pas push
└── README.md                    # Documentation principale du projet
```

---

# ⚙️ **Installation**

### 1️⃣ Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate       # Windows : venv\Scripts\activate
```

### 2️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# 🚀 **Exécution du Pipeline**

Exécuter l’intégralité du traitement :

```bash
python main.py
```

Le script :

1. Charge le CSV brut
2. Nettoie & normalise les données
3. Applique les règles de sécurité / anonymisation
4. Génère les KPI
5. Crée les dashboards & fichiers dans `output/`
6. Produit le YAML du dataset Gold

---

# 🧹 **1. Ingestion & Nettoyage — Logique Implémentée**

## ✉️ `transform_Dataframe_Mail(df, kpi)`

* Supprime les emails sans `@`
* Corrige les emails du type `xxx@@domain.com`
* Normalise les domaines et TLD (`aa@bb` corrigé en fonction des domaines déjà détectés)
* Construit une **map des domaines** pour corriger les TLD manquants
* Met à jour les KPI :

  * emails supprimés
  * emails corrigés
  * emails irréparables

---

## 💶 `transform_Dataframe_Salary(df, kpi)`

* Supprime les salaires négatifs
* Supprime les entrées qui ne contiennent pas de chiffres
* Retire tout caractère non-numérique (`50000 €` → `50000`)
* Convertit en `BIGINT`
* Remplit les KPI correspondants

---

## 📅 `transform_Dataframe_Employment_Date(df, kpi)`

* Remplace tous les séparateurs par `-`
* Tente une conversion en date selon plusieurs patterns (`%d-%m-%Y`, `%Y-%m-%d`, etc.)
* Supprime les dates invalides ou futures
* Remplit les KPI (total / supprimés)

---

# 🔐 **2. Sécurité & Anonymisation**

## 🧬 `security_Dataframe_Full_Name(df)`

* Hash MD5 de `nom + prenom`
* Supprime les colonnes originales
* Génère la colonne `Hash_ID`

## 🛡️ `security_Dataframe_Social_Number(df)`

* Supprime les NIR invalides (< 15 char)
* Masque tout sauf les deux derniers chiffres :
  `***********89`

---

# 🧑‍💼 **Gestion des accès : `show_Dataframe_With_Role(df, role)`**

| Rôle        | Données visibles                                           |
| ----------- | ---------------------------------------------------------- |
| **Admin**   | Accès complet                                              |
| **Manager** | NIR masqué, salaires arrondis au millier (`41520 → 41000`) |

---

# 📑 **3. Dataset Gold – Métadonnées (YAML)**

Généré automatiquement via :

```
output/gold_Dataframe_Metadata.yaml
```

Contient pour chaque colonne :

* `type`
* `description`
* `confidentiality` (PII / Confidentiel / Public)
* `owner` (RH, IT, Finance)

---

# 🔄 **3.2 Backfill & Maintenance (Résumé)**

Document complet :
📄 *Backfill & Maintenance.md*

Principes :

* Recalcul uniquement pour les salariés **embauchés après 2022**
* Recalcul uniquement pour les années **2022–2025**
* Pas de recalcul depuis 2018 → traitement incrémental

### Format recommandé :

> **Parquet partitionné** (année/mois)
>
> * traitement via DuckDB

---

# 📊 **4. Dashboard Final**

Généré via `dashboard.py`

Fournit :

### Graphiques interactifs :

* Histogramme **salaires par sexe**
* Histogramme **salaires par catégorie**
* Histogramme **salaires par tranche d’âge**
* Pie chart effectifs par sexe
* Pie chart effectifs par catégorie

### KPI :

* Salaire moyen global
* Emails corrigés
* Emails supprimés
* Qualité des dates, salaires…

### Fichiers exportés :

```
output/dashboard_rh.html
output/dashboard_rh.png
output/kpi_report.txt   (si activé)
```

---

# 🛡️ **5. Stratégie & Gouvernance (RGPD & Archivage)**

Document complet :
📄 *Stratégie & Gouvernance.md*

Résumé :

* Données RH actives → **hot storage**
* Après départ : bascule en archive **12 mois après la sortie**
* Données supprimées : email personnel, adresse, téléphone, documents non obligatoires
* Données conservées (obligation légale) : bulletins de paie, preuves fiscales
* Données anonymisées pour analyses People Analytics

---

# 📦 **Dépendances**

```
pandas
duckdb
numpy
pyyaml
plotly
kaleido
```

---

# 🙌 **Auteur**

Projet réalisé dans le cadre du sujet :
**Data Management 2025–2026 — Étude de cas : People Analytics**
