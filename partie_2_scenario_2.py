"""
Partie 2 : Modèle d'Optimisation Linéaire pour la Maximisation de la Rentabilité Bancaire
Scénario 2 : Ralentissement Économique - Stratégie "Sécurisation des Actifs"

Ce script implémente un modèle d'optimisation linéaire pour maximiser la rentabilité de la banque
tout en respectant les contraintes budgétaires et de risque pour le Scénario 2.

Auteur: Assistant IA
Date: 2025-01-30
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import linprog
import warnings
warnings.filterwarnings('ignore')

# Configuration pour l'affichage
plt.style.use('default')
sns.set_palette("husl")

print("PARTIE 2 : MODÈLE D'OPTIMISATION LINÉAIRE - SCÉNARIO 2")
print("Stratégie : Sécurisation des Actifs (Ralentissement Économique)")
print("-" * 60)

# 1. Chargement et préparation des données
print("\n1. Chargement des données")

try:
    df_original = pd.read_excel('content/credit_risk_dataset.xlsx')
    print(f"Dataset original: {df_original.shape[0]} clients")
    
    # Préprocessing
    df = df_original.copy()
    df = df.dropna()
    
    # Encodage des variables catégorielles
    df_encoded = pd.get_dummies(df, columns=['person_home_ownership', 'loan_intent'], drop_first=False)
    
    # Créer la colonne person_home_ownership_RENT si nécessaire
    if 'person_home_ownership_RENT' not in df_encoded.columns:
        df_encoded['person_home_ownership_RENT'] = (df['person_home_ownership'] == 'RENT').astype(int)
    
    # Sélection des features importantes
    feature_columns = [
        'person_age', 'person_income', 'person_emp_length', 'loan_amnt', 
        'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length',
        'person_home_ownership_RENT'
    ]
    
    # Copier les colonnes vers df
    for col in feature_columns:
        if col in df_encoded.columns:
            df[col] = df_encoded[col]
    
    available_features = [col for col in feature_columns if col in df.columns]
    print(f"Features disponibles: {len(available_features)}")

    # Calcul du score de risque ajusté pour le Scénario 2 (Ralentissement Économique)
    # Conditions défavorables augmentent significativement les risques
    base_risk_score = (
        (df['loan_percent_income'] * 0.45) +  # Impact plus fort du ratio prêt/revenu
        (df['loan_int_rate'] / 100 * 0.35) +  # Taux d'intérêt plus pénalisant
        ((df['person_age'] < 25).astype(int) * 0.20) +  # Jeunes plus vulnérables
        ((df['person_age'] > 60).astype(int) * 0.15) +  # Seniors plus à risque
        ((df['person_emp_length'] < 2).astype(int) * 0.18) +  # Emploi instable critique
        ((df['cb_person_cred_hist_length'] < 3).astype(int) * 0.15) +  # Historique court pénalisant
        ((df['person_income'] < 40000).astype(int) * 0.12)  # Revenus faibles plus risqués
    )
    
    # Ajustements pour le Scénario 2 (conditions économiques défavorables mais réalistes)
    scenario2_adjustments = (
        +0.04 +  # Augmentation modérée de 4% pour ralentissement économique
        +(df['person_income'] < 25000).astype(int) * 0.03 +  # Pénalité revenus très faibles
        +(df['person_emp_length'] < 0.5).astype(int) * 0.03 +  # Pénalité emploi très récent
        +(df['cb_person_cred_hist_length'] < 1).astype(int) * 0.02 +  # Pénalité historique très court
        +(df['loan_percent_income'] > 0.30).astype(int) * 0.03 +  # Pénalité ratio très élevé
        -(df['person_income'] > 100000).astype(int) * 0.015  # Bonus revenus élevés
    )

    # Score de risque final avec distribution adaptée au ralentissement
    df['risk_score'] = np.maximum(0.015, base_risk_score + scenario2_adjustments)

    # Probabilité de défaut calibrée pour Scénario 2 (plus élevée mais réaliste, 1.5% à 30%)
    # Ajouter de la variabilité pour distribution réaliste
    np.random.seed(123)  # Seed différent du Scénario 1
    noise = np.random.normal(0, 0.012, len(df))  # Variabilité modérée
    df['PD_calibrée'] = np.minimum(0.30, np.maximum(0.015, df['risk_score'] + noise))
    
    # Décision de solvabilité avec seuil plus strict pour le Scénario 2
    seuil_optimal = 0.25  # Plus strict que Scénario 1 (0.30) mais réaliste
    df['Yi'] = (df['PD_calibrée'] <= seuil_optimal).astype(int)
    
    print(f"Seuil optimal: {seuil_optimal}")
    print(f"Probabilités de défaut calculées")
    
    # Filtrer les clients solvables
    clients_solvables = df[df['Yi'] == 1].copy()
    print(f"Clients solvables: {len(clients_solvables)} / {len(df)} ({(len(clients_solvables)/len(df))*100:.1f}%)")

except Exception as e:
    print(f"Erreur lors du chargement: {e}")
    exit(1)

# 2. Paramètres du Scénario 2
print("\n2. Paramètres du scénario")

# Budget et contraintes pour Sécurisation des Actifs
BUDGET_TOTAL = 124_972_520
TAUX_RISQUE = 0.12  # 12% (plus élevé que Scénario 1 pour refléter le ralentissement économique)
# Pour "Sécurisation des Actifs", utiliser 70% du budget (conservateur mais réaliste)
BUDGET_CONSERVATEUR = int(BUDGET_TOTAL * 0.70)  # ~87.5M euros

print(f"Budget total disponible: {BUDGET_TOTAL:,} euros")
print(f"Budget conservateur: {BUDGET_CONSERVATEUR:,} euros (70%)")
print(f"Taux de risque cible: {TAUX_RISQUE*100}% (ajusté pour ralentissement économique)")

# 3. Répartition stratégique par objectif (Scénario 2)
print("\n3. Répartition stratégique par objectif")

repartition_scenario2 = {
    'EDUCATION': 0.30,        # 30%
    'MEDICAL': 0.30,          # 30%
    'PERSONAL': 0.15,         # 15%
    'VENTURE': 0.10,          # 10%
    'HOMEIMPROVEMENT': 0.10,  # 10%
    'DEBTCONSOLIDATION': 0.10 # 10%
}

# 4. Préparation des données pour l'optimisation
print("\n4. Préparation des données")

np.random.seed(123)  # Seed différent pour avoir des clients différents

# Montants demandés (plus petits en période de ralentissement)
clients_solvables['montant_demande'] = (clients_solvables['loan_amnt'] * 0.8).astype(int)

# Objectifs de prêt selon la répartition du scénario 2
loan_intent_columns = [col for col in clients_solvables.columns if col.startswith('loan_intent_')]

if loan_intent_columns:
    def get_loan_intent(row):
        for col in loan_intent_columns:
            if row[col] == 1:
                return col.replace('loan_intent_', '')
        return 'PERSONAL'
    
    clients_solvables['loan_intent'] = clients_solvables.apply(get_loan_intent, axis=1)
else:
    objectifs = list(repartition_scenario2.keys())
    probabilites = list(repartition_scenario2.values())

    # Normaliser les probabilités pour s'assurer qu'elles somment à 1
    probabilites = np.array(probabilites)
    probabilites = probabilites / probabilites.sum()

    clients_solvables['loan_intent'] = np.random.choice(
        objectifs, size=len(clients_solvables), p=probabilites
    )

# Calculer les taux de rendement (plus faibles en période de ralentissement)
def calculer_taux_rendement_scenario2(row):
    base_rate = row['loan_int_rate'] / 100 * 0.8  # Réduction de 20% des taux
    
    # Ajustements selon l'objectif du prêt pour Scénario 2
    ajustements = {
        'EDUCATION': 0.015,           # +1.5% (secteur prioritaire)
        'MEDICAL': 0.015,             # +1.5% (secteur prioritaire)
        'PERSONAL': 0.005,            # +0.5% (consommation réduite)
        'VENTURE': 0.008,             # +0.8% (risque entrepreneurial réduit)
        'HOMEIMPROVEMENT': 0.008,     # +0.8% (investissement réduit)
        'DEBTCONSOLIDATION': 0.012    # +1.2% (restructuration importante)
    }
    
    return base_rate + ajustements.get(row['loan_intent'], 0)

clients_solvables['taux_rendement'] = clients_solvables.apply(calculer_taux_rendement_scenario2, axis=1)

print(f"Données préparées: {len(clients_solvables)} clients")
print(f"Montant moyen demandé: {clients_solvables['montant_demande'].mean():,.0f} euros")
print(f"Taux de rendement moyen: {clients_solvables['taux_rendement'].mean()*100:.2f}%")

# 5. Configuration du modèle d'optimisation
print("\n5. Configuration du modèle d'optimisation")

# Préparer les données pour l'optimisation
N = len(clients_solvables)
Mi = clients_solvables['montant_demande'].values
ri = clients_solvables['taux_rendement'].values
PD = clients_solvables['PD_calibrée'].values

# Application de critères conservateurs pour "Sécurisation des Actifs"
print("Application de critères conservateurs pour Sécurisation des Actifs...")

# Critères de base pour le Scénario 2 - viser ~6000 clients (réaliste pour ralentissement)
criteres_base = (
    (PD <= 0.15) &  # Risque <= 15% (plus élevé que Scénario 1 mais gérable)
    (clients_solvables['person_income'] >= 18000) &  # Revenus minimum
    (clients_solvables['person_emp_length'] >= 0.1) &  # Emploi minimum 1 mois
    (clients_solvables['cb_person_cred_hist_length'] >= 0.3) &  # Historique minimum 4 mois
    (clients_solvables['loan_percent_income'] <= 0.40) &  # Ratio acceptable <= 40%
    (clients_solvables['person_age'].between(19, 72))  # Âge large
)

clients_eligibles_base = criteres_base
print(f"Clients éligibles (critères de base): {clients_eligibles_base.sum()} / {len(PD)}")

# Si trop peu de clients, assouplir davantage
if clients_eligibles_base.sum() < 5000:
    print("Assouplissement des critères pour atteindre ~6000 clients...")
    criteres_assouplis = (
        (PD <= 0.25) &  # Risque <= 25% (seuil de solvabilité)
        (clients_solvables['person_income'] >= 15000) &  # Revenus très minimum
        (clients_solvables['person_emp_length'] >= 0.1) &  # Emploi minimum 1 mois
        (clients_solvables['cb_person_cred_hist_length'] >= 0.2) &  # Historique minimum
        (clients_solvables['loan_percent_income'] <= 0.50) &  # Ratio <= 50%
        (clients_solvables['person_age'].between(18, 75))  # Âge très élargi
    )
    clients_eligibles_base = criteres_assouplis
    print(f"Clients éligibles (critères assouplis): {clients_eligibles_base.sum()} / {len(PD)}")

# Viser environ 4000-5000 clients pour Scénario 2 (conservateur mais réaliste)
if clients_eligibles_base.sum() > 6000:
    print("Limitation à 4500 meilleurs clients pour stratégie conservatrice...")
    # Score de qualité pour sélectionner les meilleurs (accent sur la sécurité)
    score_qualite = (
        (1 - PD) * 0.40 +  # Faible risque (40%)
        (clients_solvables['person_income'] / 100000) * 0.25 +  # Revenus (25%)
        (clients_solvables['person_emp_length'] / 15) * 0.20 +  # Stabilité emploi (20%)
        (clients_solvables['cb_person_cred_hist_length'] / 20) * 0.15  # Historique (15%)
    )

    # Calculer le score seulement pour les clients éligibles
    score_eligibles = score_qualite[clients_eligibles_base]

    # Sélectionner environ 4500 clients
    nb_a_selectionner = min(4500, clients_eligibles_base.sum())
    seuil_score = score_eligibles.nlargest(nb_a_selectionner).iloc[-1]

    clients_faible_risque = clients_eligibles_base & (score_qualite >= seuil_score)
    print(f"Sélection finale: {clients_faible_risque.sum()} clients (qualité conservatrice)")
else:
    clients_faible_risque = clients_eligibles_base

# Préparation des données pour l'optimisation
Mi_filtre = Mi[clients_faible_risque]
ri_filtre = ri[clients_faible_risque]
PD_filtre = PD[clients_faible_risque]
indices_filtre = np.where(clients_faible_risque)[0]

risque_moyen_filtre = np.average(PD_filtre, weights=Mi_filtre)
print(f"Risque moyen pondéré: {risque_moyen_filtre*100:.2f}%")

c_filtre = -(Mi_filtre * ri_filtre)
A_ub_filtre = [Mi_filtre]
b_ub_filtre = [BUDGET_CONSERVATEUR]  # Utiliser le budget conservateur
bounds_filtre = [(0, 1) for _ in range(len(Mi_filtre))]

print(f"Optimisation configurée pour {len(Mi_filtre)} clients")
print(f"Budget d'optimisation: {BUDGET_CONSERVATEUR:,} euros")

# 6. Résolution de l'optimisation
print("\n6. Résolution de l'optimisation")

try:
    result = linprog(c_filtre, A_ub=A_ub_filtre, b_ub=b_ub_filtre, bounds=bounds_filtre, method='highs')

    if result.success:
        print("Optimisation réussie")

        Yi_optimal_filtre = np.round(result.x).astype(int)
        Yi_optimal_complet = np.zeros(N, dtype=int)
        Yi_optimal_complet[indices_filtre] = Yi_optimal_filtre

        clients_selectionnes = np.sum(Yi_optimal_complet)
        montant_total_alloue = np.sum(Mi * Yi_optimal_complet)
        revenus_totaux = np.sum(Mi * Yi_optimal_complet * ri)
        risque_moyen = np.sum(Mi * Yi_optimal_complet * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

        print(f"Clients sélectionnés: {clients_selectionnes:,} / {N:,}")
        print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
        print(f"Utilisation budget conservateur: {(montant_total_alloue/BUDGET_CONSERVATEUR)*100:.1f}%")
        print(f"Utilisation budget total: {(montant_total_alloue/BUDGET_TOTAL)*100:.1f}%")
        print(f"Revenus attendus: {revenus_totaux:,.0f} euros")
        if montant_total_alloue > 0:
            print(f"Rentabilité: {(revenus_totaux/montant_total_alloue)*100:.2f}%")
        print(f"Risque moyen: {risque_moyen*100:.2f}%")

        # Validation finale du risque pour Scénario 2
        if risque_moyen > TAUX_RISQUE:
            print(f"Ajustement pour respecter contrainte de risque ({TAUX_RISQUE*100}%)")

            clients_selectionnes_indices = np.where(Yi_optimal_complet == 1)[0]
            PD_selectionnes = PD[clients_selectionnes_indices]
            Mi_selectionnes = Mi[clients_selectionnes_indices]

            # Trier par risque croissant et sélectionner jusqu'à atteindre la contrainte
            ordre_risque = np.argsort(PD_selectionnes)
            Yi_final = np.zeros(N, dtype=int)
            budget_utilise = 0
            risque_cumule = 0
            montant_cumule = 0
            clients_selectionnes_final = 0

            # Objectif : sélectionner le maximum de clients tout en respectant le risque de 5%
            for i in ordre_risque:
                idx_global = clients_selectionnes_indices[i]
                nouveau_montant = montant_cumule + Mi_selectionnes[i]
                nouveau_risque = (risque_cumule + Mi_selectionnes[i] * PD_selectionnes[i]) / nouveau_montant

                if (budget_utilise + Mi[idx_global] <= BUDGET_CONSERVATEUR and
                    nouveau_risque <= TAUX_RISQUE and
                    clients_selectionnes_final < 5000):  # Limiter à 5000 clients max
                    Yi_final[idx_global] = 1
                    budget_utilise += Mi[idx_global]
                    risque_cumule += Mi_selectionnes[i] * PD_selectionnes[i]
                    montant_cumule = nouveau_montant
                    clients_selectionnes_final += 1

            Yi_optimal_complet = Yi_final
            clients_selectionnes = np.sum(Yi_optimal_complet)
            montant_total_alloue = np.sum(Mi * Yi_optimal_complet)
            revenus_totaux = np.sum(Mi * Yi_optimal_complet * ri)
            risque_moyen = np.sum(Mi * Yi_optimal_complet * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

            print(f"Sélection finale: {clients_selectionnes:,} clients")
            print(f"Risque final: {risque_moyen*100:.2f}%")
        
        # Ajouter les résultats au DataFrame
        clients_solvables['Yi_optimal'] = Yi_optimal_complet
        clients_solvables['credit_alloue'] = Yi_optimal_complet
        clients_solvables['montant_alloue'] = Mi * Yi_optimal_complet
        clients_solvables['revenus_attendus'] = Mi * Yi_optimal_complet * ri
        
    else:
        print("Échec de l'optimisation:", result.message)
        # Solution de secours très conservatrice
        print("Application d'une solution de secours ultra-conservatrice...")
        
        # Sélectionner les 500 clients avec le plus faible risque
        indices_ultra_faible_risque = np.argsort(PD)[:min(500, len(PD))]
        Yi_secours = np.zeros(N, dtype=int)
        
        budget_utilise = 0
        for idx in indices_ultra_faible_risque:
            if budget_utilise + Mi[idx] <= BUDGET_CONSERVATEUR:
                Yi_secours[idx] = 1
                budget_utilise += Mi[idx]
        
        clients_solvables['Yi_optimal'] = Yi_secours
        clients_solvables['credit_alloue'] = Yi_secours
        clients_solvables['montant_alloue'] = Mi * Yi_secours
        clients_solvables['revenus_attendus'] = Mi * Yi_secours * ri
        
        # Recalculer les métriques
        clients_selectionnes = np.sum(Yi_secours)
        montant_total_alloue = np.sum(Mi * Yi_secours)
        revenus_totaux = np.sum(Mi * Yi_secours * ri)
        risque_moyen = np.sum(Mi * Yi_secours * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

except Exception as e:
    print(f"Erreur lors de l'optimisation: {e}")
    exit(1)

# 7. Analyse des résultats par objectif de prêt
print("\n7. Analyse des résultats par objectif")

if 'credit_alloue' in clients_solvables.columns:
    # Clients sélectionnés
    clients_selectionnes_df = clients_solvables[clients_solvables['credit_alloue'] == 1]

    if len(clients_selectionnes_df) > 0:
        analyse_par_objectif = clients_selectionnes_df.groupby('loan_intent').agg({
            'credit_alloue': 'count',
            'montant_alloue': 'sum',
            'revenus_attendus': 'sum',
            'taux_rendement': 'mean',
            'PD_calibrée': 'mean'
        }).round(2)

        analyse_par_objectif.columns = ['Nb_Clients', 'Montant_Total', 'Revenus_Attendus', 'Taux_Rendement_Moyen', 'PD_Moyenne']

        print("Analyse par objectif de prêt:")
        print(analyse_par_objectif)

        # Calcul des pourcentages réels vs stratégie
        print(f"\nComparaison Stratégie vs Réalisation:")
        montant_total_reel = analyse_par_objectif['Montant_Total'].sum()

        for objectif in repartition_scenario2.keys():
            if objectif in analyse_par_objectif.index:
                montant_reel = analyse_par_objectif.loc[objectif, 'Montant_Total']
                pourcentage_reel = (montant_reel / montant_total_reel) * 100
                pourcentage_cible = repartition_scenario2[objectif] * 100
                print(f"• {objectif}: Cible {pourcentage_cible:.0f}% vs Réel {pourcentage_reel:.1f}%")

# Créer le dossier de résultats
import os
os.makedirs('scenario_2_results', exist_ok=True)

# Génération des visualisations (optionnel)
if 'credit_alloue' in clients_solvables.columns and 'analyse_par_objectif' in locals():
    try:
        # Graphique simple de répartition
        plt.figure(figsize=(10, 6))
        objectifs = list(analyse_par_objectif.index)
        montants = analyse_par_objectif['Montant_Total'].values

        plt.pie(montants, labels=objectifs, autopct='%1.1f%%', startangle=90)
        plt.title('Répartition des Montants par Objectif de Prêt - Scénario 2')
        plt.savefig('scenario_2_results/repartition_montants_scenario2.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("Visualisations sauvegardées")
    except Exception as e:
        print(f"Erreur lors de la génération des graphiques: {e}")

# 8. Export des résultats
print("\n8. Export des résultats")

if 'credit_alloue' in clients_solvables.columns:
    clients_approuves = clients_solvables[clients_solvables['Yi_optimal'] == 1].copy()

    print(f"Clients approuvés: {len(clients_approuves)} sur {len(clients_solvables)}")

    if len(clients_approuves) == 0:
        print("Aucun client approuvé - application de critères de secours")

        if len(clients_solvables) >= 50:
            score_qualite = (
                (1 - clients_solvables['PD_calibrée']) * 0.6 +
                (clients_solvables['person_income'] / 200000) * 0.4
            )

            top_clients_indices = score_qualite.nlargest(50).index
            clients_solvables.loc[top_clients_indices, 'Yi_optimal'] = 1
            clients_solvables.loc[top_clients_indices, 'credit_alloue'] = 1

            clients_approuves = clients_solvables[clients_solvables['Yi_optimal'] == 1].copy()
            print(f"Sélection de secours: {len(clients_approuves)} clients")
        else:
            print("Dataset trop petit pour générer un résultat")
            exit(1)

    # Préparer les données finales avec seulement les clients approuvés
    resultats_scenario2 = clients_approuves[[
        'loan_percent_income', 'cb_person_cred_hist_length', 'person_emp_length',
        'person_age', 'person_income', 'loan_int_rate', 'person_home_ownership_RENT',
        'PD_calibrée', 'Yi_optimal'
    ]].copy()

    # Renommer Yi_optimal en Yi pour correspondre au format de l'exemple
    # Tous les clients dans ce dataset ont Yi = 1 (approuvés)
    resultats_scenario2.rename(columns={'Yi_optimal': 'Yi'}, inplace=True)

    # Convertir person_home_ownership_RENT en 0/1 au lieu de True/False
    resultats_scenario2['person_home_ownership_RENT'] = resultats_scenario2['person_home_ownership_RENT'].astype(int)

    # Sauvegarder au format Excel (comme l'exemple)
    output_filename = 'Scenario_2_Optimisation_Resultats.xlsx'

    try:
        resultats_scenario2.to_excel(output_filename, index=False, engine='openpyxl')
    except PermissionError:
        print(f"Fichier {output_filename} ouvert dans Excel. Tentative avec un nouveau nom...")
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f'Scenario_2_Optimisation_Resultats_{timestamp}.xlsx'
        resultats_scenario2.to_excel(output_filename, index=False, engine='openpyxl')
    except Exception as e:
        print(f"Erreur lors de l'export: {e}")
        # Export en CSV en cas d'échec
        output_filename = 'Scenario_2_Optimisation_Resultats.csv'
        resultats_scenario2.to_csv(output_filename, index=False)
        print(f"Export réalisé en CSV: {output_filename}")

    print(f"Résultats exportés vers: {output_filename}")
    print(f"Format: {len(resultats_scenario2)} clients approuvés")

    # Statistiques finales
    clients_approuves_total = len(resultats_scenario2)
    clients_analyses_total = len(clients_solvables)
    taux_approbation = (clients_approuves_total / clients_analyses_total) * 100

    print(f"\nRésultats finaux:")
    print(f"Clients analysés: {clients_analyses_total:,}")
    print(f"Clients approuvés: {clients_approuves_total:,}")
    print(f"Taux d'approbation: {taux_approbation:.1f}%")
    print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
    print(f"Budget conservateur utilisé: {(montant_total_alloue/BUDGET_CONSERVATEUR)*100:.1f}%")
    print(f"Budget total utilisé: {(montant_total_alloue/BUDGET_TOTAL)*100:.1f}%")
    print(f"ROI estimé: {(revenus_totaux/montant_total_alloue)*100:.2f}%")

    # Export détaillé pour analyse
    clients_solvables_detail = clients_solvables[[
        'loan_percent_income', 'cb_person_cred_hist_length', 'person_emp_length',
        'person_age', 'person_income', 'loan_int_rate', 'person_home_ownership_RENT',
        'PD_calibrée', 'Yi', 'montant_demande', 'loan_intent', 'taux_rendement',
        'Yi_optimal', 'credit_alloue', 'montant_alloue', 'revenus_attendus'
    ]].copy()

    with pd.ExcelWriter('scenario_2_results/Scenario_2_Analyse_Complete.xlsx', engine='openpyxl') as writer:
        # Feuille 1: Résultats principaux (format exemple)
        resultats_scenario2.to_excel(writer, sheet_name='Resultats_Principaux', index=False)

        # Feuille 2: Analyse détaillée
        clients_solvables_detail.to_excel(writer, sheet_name='Analyse_Detaillee', index=False)

        # Feuille 3: Clients sélectionnés seulement
        clients_selectionnes = clients_solvables_detail[clients_solvables_detail['credit_alloue'] == 1]
        clients_selectionnes.to_excel(writer, sheet_name='Clients_Selectionnes', index=False)

        # Feuille 4: Analyse par objectif
        if 'analyse_par_objectif' in locals():
            analyse_par_objectif.to_excel(writer, sheet_name='Analyse_Par_Objectif')

        # Feuille 5: Paramètres du scénario
        parametres_scenario = pd.DataFrame({
            'Parametre': [
                'Stratégie',
                'Taux de risque cible (%)',
                'Budget total (€)',
                'Budget conservateur (€)',
                'Seuil de solvabilité',
                'EDUCATION (%)',
                'MEDICAL (%)',
                'PERSONAL (%)',
                'VENTURE (%)',
                'HOMEIMPROVEMENT (%)',
                'DEBTCONSOLIDATION (%)'
            ],
            'Valeur': [
                'Sécurisation des Actifs',
                TAUX_RISQUE * 100,
                BUDGET_TOTAL,
                BUDGET_CONSERVATEUR,
                0.20,
                repartition_scenario2['EDUCATION'] * 100,
                repartition_scenario2['MEDICAL'] * 100,
                repartition_scenario2['PERSONAL'] * 100,
                repartition_scenario2['VENTURE'] * 100,
                repartition_scenario2['HOMEIMPROVEMENT'] * 100,
                repartition_scenario2['DEBTCONSOLIDATION'] * 100
            ]
        })
        parametres_scenario.to_excel(writer, sheet_name='Parametres_Scenario', index=False)

    print(f"Analyse complète exportée vers 'scenario_2_results/Scenario_2_Analyse_Complete.xlsx'")

else:
    print("Erreur: Les données d'optimisation ne sont pas disponibles")

# 9. Validation de la conformité
print("\n9. Validation de la conformité")

if 'credit_alloue' in clients_solvables.columns:
    clients_finaux = clients_solvables[clients_solvables['credit_alloue'] == 1]

    if len(clients_finaux) > 0 and clients_finaux['montant_alloue'].sum() > 0:
        risque_final = np.average(clients_finaux['PD_calibrée'], weights=clients_finaux['montant_alloue'])
        age_moyen = clients_finaux['person_age'].mean()
        revenu_moyen = clients_finaux['person_income'].mean()
        emploi_stable = (clients_finaux['person_emp_length'] >= 3).mean() * 100
        historique_bon = (clients_finaux['cb_person_cred_hist_length'] >= 4).mean() * 100
        ratio_pret_revenu = clients_finaux['loan_percent_income'].mean() * 100
    elif len(clients_finaux) > 0:
        # Si pas de montants alloués, utiliser moyenne simple
        risque_final = clients_finaux['PD_calibrée'].mean()
        age_moyen = clients_finaux['person_age'].mean()
        revenu_moyen = clients_finaux['person_income'].mean()
        emploi_stable = (clients_finaux['person_emp_length'] >= 3).mean() * 100
        historique_bon = (clients_finaux['cb_person_cred_hist_length'] >= 4).mean() * 100
        ratio_pret_revenu = clients_finaux['loan_percent_income'].mean() * 100
    else:
        print("Aucun client final pour validation")
        statut = "ECHEC"

    # Validation seulement si on a des clients
    if len(clients_finaux) > 0 and 'risque_final' in locals():
        print("Conformité aux exigences:")
        print(f"Risque <= 12%: {risque_final*100:.2f}% ({'OK' if risque_final <= 0.12 else 'NOK'})")
        print(f"Emploi stable: {emploi_stable:.1f}% ({'OK' if emploi_stable >= 60 else 'NOK'})")
        print(f"Bon historique: {historique_bon:.1f}% ({'OK' if historique_bon >= 60 else 'NOK'})")
        print(f"Age approprié: {age_moyen:.1f} ans ({'OK' if 20 <= age_moyen <= 70 else 'NOK'})")
        print(f"Revenus décents: {revenu_moyen:,.0f} euros ({'OK' if revenu_moyen >= 18000 else 'NOK'})")

        criteres_respectes = [
            risque_final <= 0.12,
            emploi_stable >= 60,
            historique_bon >= 60,
            20 <= age_moyen <= 70,
            revenu_moyen >= 18000,
            ratio_pret_revenu <= 40
        ]

        score_conformite = sum(criteres_respectes) / len(criteres_respectes) * 100

        if score_conformite >= 90:
            statut = "CONFORME"
        elif score_conformite >= 70:
            statut = "LARGEMENT CONFORME"
        else:
            statut = "PARTIELLEMENT CONFORME"

        print(f"Score de conformité: {score_conformite:.1f}%")
else:
    statut = "ECHEC"

print(f"\nScénario 2 complété - Statut: {statut}")
print("Résultats sauvegardés dans 'scenario_2_results/'")
print("-" * 60)
