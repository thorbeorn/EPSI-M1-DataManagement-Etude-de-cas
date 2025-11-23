import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

def generate_dashboard(gold_df, kpi, export_path="output"):
    """
    Génère un dashboard interactif avec Plotly
    
    Args:
        gold_df (pd.DataFrame): DataFrame gold après toutes les transformations
        kpi (dict): Dictionnaire contenant les KPI de traitement
        export_path (str): Chemin du dossier d'export (défaut: "output")
    """
    
    # Créer le dossier output s'il n'existe pas
    os.makedirs(export_path, exist_ok=True)
    
    # Préparation des données
    df = gold_df.copy()
    
    # Arrondir les salaires au millier près pour l'affichage
    df['salaire_brut'] = df['salaire_brut'].round(-3)
    
    # Calcul de l'âge
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    df['age'] = (pd.Timestamp.now() - df['date_naissance']).dt.days // 365
    df['tranche_age'] = pd.cut(df['age'], 
                                bins=[0, 30, 40, 50, 100], 
                                labels=['<30 ans', '30-39 ans', '40-49 ans', '50+ ans'])
    
    # Calcul du salaire moyen global
    salaire_moyen_global = df['salaire_brut'].mean()
    
    # Calcul emails corrigés/rejetés
    emails_corriges = kpi.get('emails_corriges_tld', 0)
    emails_rejetes = (kpi.get('emails_supprimes_sans_at', 0) + 
                      kpi.get('emails_supprimes_apres_fix', 0) + 
                      kpi.get('emails_supprimes_non_reparables', 0))
    
    # Distribution par sexe
    dist_sexe = df.groupby('sexe').agg({
        'salaire_brut': 'mean',
        'id': 'count'
    }).reset_index()
    dist_sexe.columns = ['sexe', 'salaire_moyen', 'effectif']
    dist_sexe['sexe'] = dist_sexe['sexe'].map({'M': 'Hommes', 'F': 'Femmes'})
    
    # Distribution par catégorie professionnelle
    dist_categorie = df.groupby('categorie_pro').agg({
        'salaire_brut': 'mean',
        'id': 'count'
    }).reset_index()
    dist_categorie.columns = ['categorie', 'salaire_moyen', 'effectif']
    
    # Distribution par âge
    dist_age = df.groupby('tranche_age', observed=True).agg({
        'salaire_brut': 'mean',
        'id': 'count'
    }).reset_index()
    dist_age.columns = ['tranche_age', 'salaire_moyen', 'effectif']
    
    # Création du dashboard avec subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Salaires Moyens par Sexe',
            'Salaires Moyens par Catégorie Professionnelle',
            'Salaires Moyens par Tranche d\'Âge',
            'KPI Globaux',
            'Distribution des Effectifs par Sexe',
            'Distribution des Effectifs par Catégorie'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "table"}],
            [{"type": "pie"}, {"type": "pie"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )
    
    # 1. Salaires par Sexe
    fig.add_trace(
        go.Bar(
            x=dist_sexe['sexe'],
            y=dist_sexe['salaire_moyen'],
            text=[f"{int(s):,} €".replace(',', ' ') for s in dist_sexe['salaire_moyen']],
            textposition='outside',
            marker_color=['#3b82f6', '#ef4444'],
            name='Salaire Moyen',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. Salaires par Catégorie
    fig.add_trace(
        go.Bar(
            x=dist_categorie['categorie'],
            y=dist_categorie['salaire_moyen'],
            text=[f"{int(s):,} €".replace(',', ' ') for s in dist_categorie['salaire_moyen']],
            textposition='outside',
            marker_color='#10b981',
            name='Salaire Moyen',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Salaires par Âge
    fig.add_trace(
        go.Bar(
            x=dist_age['tranche_age'].astype(str),
            y=dist_age['salaire_moyen'],
            text=[f"{int(s):,} €".replace(',', ' ') for s in dist_age['salaire_moyen']],
            textposition='outside',
            marker_color='#f59e0b',
            name='Salaire Moyen',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # 4. Table des KPI
    kpi_labels = []
    kpi_values = []
    
    # Tous les KPI disponibles
    all_kpis = {
        '💰 Salaire Moyen Global': f"{salaire_moyen_global:,.0f} €".replace(',', ' '),
        '👥 Nombre d\'employés': str(len(df)),
        '📧 Emails Total': str(kpi.get('emails_total', 'N/A')),
        '✅ Emails Corrigés (TLD)': str(emails_corriges),
        '❌ Emails Rejetés (Total)': str(emails_rejetes),
        '  ↳ Sans @': str(kpi.get('emails_supprimes_sans_at', 'N/A')),
        '  ↳ Après correction': str(kpi.get('emails_supprimes_apres_fix', 'N/A')),
        '  ↳ Non réparables': str(kpi.get('emails_supprimes_non_reparables', 'N/A')),
        '💼 Salaires Total': str(kpi.get('salaire_total', 'N/A')),
        '🗑️ Salaires Supprimés': str(kpi.get('salaire_supprimes', 'N/A')),
        '📅 Dates Embauche Total': str(kpi.get('date_embauche_total', 'N/A')),
        '🗑️ Dates Supprimées': str(kpi.get('date_embauche_supprimes', 'N/A')),
    }
    
    for label, value in all_kpis.items():
        kpi_labels.append(label)
        kpi_values.append(value)
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=['<b>KPI</b>', '<b>Valeur</b>'],
                fill_color='#3b82f6',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[kpi_labels, kpi_values],
                fill_color=[['#f0f9ff', '#e0f2fe'] * (len(kpi_labels) // 2 + 1)],
                align='left',
                font=dict(size=11),
                height=25
            )
        ),
        row=2, col=2
    )
    
    # 5. Effectifs par Sexe (Pie)
    fig.add_trace(
        go.Pie(
            labels=dist_sexe['sexe'],
            values=dist_sexe['effectif'],
            marker_colors=['#3b82f6', '#ef4444'],
            textinfo='label+percent',
            showlegend=True
        ),
        row=3, col=1
    )
    
    # 6. Effectifs par Catégorie (Pie)
    colors_cat = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    fig.add_trace(
        go.Pie(
            labels=dist_categorie['categorie'],
            values=dist_categorie['effectif'],
            marker_colors=colors_cat[:len(dist_categorie)],
            textinfo='label+percent',
            showlegend=True
        ),
        row=3, col=2
    )
    
    # Mise à jour du layout
    fig.update_layout(
        title_text=f"<b>Dashboard RH - Analyse des Salaires</b><br>" +
                   f"<sub>Salaire Moyen: {salaire_moyen_global:,.0f} € | " +
                   f"Emails Corrigés: {emails_corriges} | " +
                   f"Emails Rejetés: {emails_rejetes}</sub>".replace(',', ' '),
        title_x=0.5,
        title_font_size=20,
        height=1400,
        showlegend=False
    )
    
    # Axes
    fig.update_xaxes(title_text="Sexe", row=1, col=1)
    fig.update_yaxes(title_text="Salaire Brut (€)", row=1, col=1)
    
    fig.update_xaxes(title_text="Catégorie Professionnelle", row=1, col=2)
    fig.update_yaxes(title_text="Salaire Brut (€)", row=1, col=2)
    
    fig.update_xaxes(title_text="Tranche d'Âge", row=2, col=1)
    fig.update_yaxes(title_text="Salaire Brut (€)", row=2, col=1)
    
    # Affichage
    fig.show()
    
    # Export du dashboard en HTML
    html_path = os.path.join(export_path, "dashboard_rh.html")
    fig.write_html(html_path)
    
    # Export en image PNG
    png_path = os.path.join(export_path, "dashboard_rh.png")
    fig.write_image(png_path, width=1920, height=1400)
    
    return fig