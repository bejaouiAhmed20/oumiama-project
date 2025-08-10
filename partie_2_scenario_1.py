"""
Scénario 1 : Expansion Prudente
Stratégie d'optimisation pour période de croissance économique stable
Maximise la rentabilité avec un risque contrôlé (≤ 10%)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import linprog
import warnings
warnings.filterwarnings('ignore')

# Import data cleaning module
from data_cleaning_module import clean_dataset

# Configuration pour l'affichage
plt.style.use('default')
sns.set_palette("husl")

print("Scénario 1 : Expansion Prudente")
print("Chargement et nettoyage des données...")

try:
    df_original = pd.read_excel('content/credit_risk_dataset.xlsx')
    print(f"Dataset original: {df_original.shape[0]} clients")

    # Data cleaning and validation
    df_clean, cleaning_report = clean_dataset(df_original, "Scénario 1 - Expansion Prudente")

    # Préprocessing
    df = df_clean.copy()
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

    base_risk_score = (
        (df['loan_percent_income'] * 0.35) +  # Facteur principal
        (df['loan_int_rate'] / 100 * 0.25) +  # Taux d'intérêt
        ((df['person_age'] < 25).astype(int) * 0.12) +  # Âge jeune
        ((df['person_age'] > 65).astype(int) * 0.08) +  # Âge avancé
        ((df['person_emp_length'] < 1).astype(int) * 0.1) +  # Emploi très récent
        ((df['cb_person_cred_hist_length'] < 2).astype(int) * 0.08) +  # Historique court
        ((df['person_income'] < 30000).astype(int) * 0.06)  # Revenus faibles
    )

    # Ajustements pour le Scénario 1 (conditions économiques favorables)
    scenario1_adjustments = (
        -0.02 +  # Réduction de base de 2% pour économie stable
        -(df['person_income'] > 100000).astype(int) * 0.015 +  # Bonus revenus très élevés
        -(df['person_emp_length'] >= 10).astype(int) * 0.01 +  # Bonus emploi très stable
        -(df['cb_person_cred_hist_length'] >= 10).astype(int) * 0.01 +  # Bonus historique excellent
        -(df['person_age'].between(30, 50)).astype(int) * 0.005  # Bonus âge optimal
    )

    # Score de risque final avec distribution réaliste
    df['risk_score'] = np.maximum(0.005, base_risk_score + scenario1_adjustments)

    # Probabilité de défaut calibrée similaire à l'exemple (0.009 à 0.30)
    # Ajouter de la variabilité pour avoir une distribution plus riche
    noise = np.random.normal(0, 0.01, len(df))  # Bruit gaussien
    df['PD_calibrée'] = np.minimum(0.30, np.maximum(0.009, df['risk_score'] + noise))

    # Décision de solvabilité
    seuil_optimal = 0.30
    df['Yi'] = (df['PD_calibrée'] <= seuil_optimal).astype(int)

    # Filtrer les clients solvables
    clients_solvables = df[df['Yi'] == 1].copy()
    print(f"Clients solvables: {len(clients_solvables):,}")

except Exception as e:
    print(f"Erreur: {e}")
    exit(1)

# Paramètres du Scénario 1
BUDGET_TOTAL = 93_729_390  # Budget fixe pour les deux scénarios
TAUX_RISQUE = 0.10  # 10%
LGD = 0.6  # Loss Given Default = 60% (paramètre manquant ajouté)
# Scénario 1: Expansion - utiliser plus de budget pour avoir plus de clients
BUDGET_UTILISE = int(BUDGET_TOTAL * 0.95)  # 95% du budget pour expansion

print(f"Budget total: {BUDGET_TOTAL:,} euros")
print(f"Budget utilisé (expansion): {BUDGET_UTILISE:,} euros (95%)")
print(f"Risque max: {TAUX_RISQUE*100}%, LGD: {LGD*100}%")

# Répartition stratégique
repartition_scenario1 = {
    'HOMEIMPROVEMENT': 0.30,
    'VENTURE': 0.25,
    'EDUCATION': 0.15,
    'PERSONAL': 0.10,
    'MEDICAL': 0.10,
    'DEBTCONSOLIDATION': 0.10
}

np.random.seed(42)

# Montants demandés
clients_solvables['montant_demande'] = clients_solvables['loan_amnt'].astype(int)

# Objectifs de prêt
loan_intent_columns = [col for col in clients_solvables.columns if col.startswith('loan_intent_')]

if loan_intent_columns:
    def get_loan_intent(row):
        for col in loan_intent_columns:
            if row[col] == 1:
                return col.replace('loan_intent_', '')
        return 'PERSONAL'

    clients_solvables['loan_intent'] = clients_solvables.apply(get_loan_intent, axis=1)
else:
    objectifs = list(repartition_scenario1.keys())
    probabilites = list(repartition_scenario1.values())

    clients_solvables['loan_intent'] = np.random.choice(
        objectifs, size=len(clients_solvables), p=probabilites
    )

# Calculer les taux de rendement (ri) basés sur les taux d'intérêt et l'objectif
def calculer_taux_rendement(row):
    base_rate = row['loan_int_rate'] / 100  # Convertir en décimal

    # Ajustements selon l'objectif du prêt (primes de risque/rendement du Scénario 1)
    ajustements = {
        'HOMEIMPROVEMENT': 0.02,    # +2% (investissement productif prioritaire)
        'VENTURE': 0.03,            # +3% (risque entrepreneurial mais prioritaire)
        'EDUCATION': 0.01,          # +1% (investissement social)
        'PERSONAL': 0.005,          # +0.5% (consommation)
        'MEDICAL': 0.005,           # +0.5% (nécessité)
        'DEBTCONSOLIDATION': 0.015  # +1.5% (restructuration)
    }

    return base_rate + ajustements.get(row['loan_intent'], 0)

clients_solvables['taux_rendement'] = clients_solvables.apply(calculer_taux_rendement, axis=1)

# Préparer les données pour l'optimisation
N = len(clients_solvables)
Mi = clients_solvables['montant_demande'].values
ri = clients_solvables['taux_rendement'].values
PD = clients_solvables['PD_calibrée'].values

# Fonction objectif: Maximiser le profit net attendu
# profit_i = ri * Mi - PDi * LGD * Mi (revenus - pertes attendues)
profit_net = Mi * ri - PD * LGD * Mi
c = -profit_net  # Négatif pour maximisation avec linprog

# Contraintes d'inégalité (A_ub × x ≤ b_ub)
A_ub = []
b_ub = []

# 1. Contrainte budgétaire: Σ(Mi × Yi) ≤ BUDGET_UTILISE
A_ub.append(Mi)
b_ub.append(BUDGET_UTILISE)

# 2. Contrainte de risque: Σ(PDi × Mi × Yi) ≤ TR × B
A_ub.append(PD * Mi)
b_ub.append(TAUX_RISQUE * BUDGET_UTILISE)

# 3. Contraintes d'allocation par catégorie de prêt
# Pour chaque catégorie: pct × B × (1-ε) ≤ Σ(Mi × Yi pour cette catégorie) ≤ pct × B × (1+ε)
epsilon = 0.05  # Tolérance de 5%

# Créer des masques pour chaque catégorie de prêt
categories_masks = {}
for categorie in repartition_scenario1.keys():
    mask = (clients_solvables['loan_intent'] == categorie).values
    categories_masks[categorie] = mask

    if mask.sum() > 0:  # Si on a des clients dans cette catégorie
        pct_target = repartition_scenario1[categorie]
        budget_min = pct_target * BUDGET_UTILISE * (1 - epsilon)
        budget_max = pct_target * BUDGET_UTILISE * (1 + epsilon)

        # Contrainte minimum: -Σ(Mi × Yi pour catégorie) ≤ -budget_min
        A_ub.append(-(Mi * mask))
        b_ub.append(-budget_min)

        # Contrainte maximum: Σ(Mi × Yi pour catégorie) ≤ budget_max
        A_ub.append(Mi * mask)
        b_ub.append(budget_max)

# Bornes des variables (0 ≤ Yi ≤ 1, variables binaires)
bounds = [(0, 1) for _ in range(N)]

try:
    # Convertir les listes en arrays numpy
    A_ub_array = np.array(A_ub)
    b_ub_array = np.array(b_ub)

    result = linprog(c, A_ub=A_ub_array, b_ub=b_ub_array, bounds=bounds, method='highs')

    if result.success:


        # Variables de décision optimales (arrondir à 0 ou 1 pour binaire)
        Yi_optimal = np.round(result.x).astype(int)

        # Calculer les métriques de la solution
        clients_selectionnes = np.sum(Yi_optimal)
        montant_total_alloue = np.sum(Mi * Yi_optimal)
        revenus_totaux = np.sum(Mi * Yi_optimal * ri)
        pertes_attendues = np.sum(Mi * Yi_optimal * PD * LGD)
        profit_net = revenus_totaux - pertes_attendues
        risque_moyen = np.sum(Mi * Yi_optimal * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

        print(f"Clients sélectionnés: {clients_selectionnes:,} / {N:,}")
        print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
        print(f"Utilisation budget: {(montant_total_alloue/BUDGET_UTILISE)*100:.1f}% du budget alloué")
        print(f"Utilisation budget total: {(montant_total_alloue/BUDGET_TOTAL)*100:.1f}% du budget total")
        print(f"Revenus totaux: {revenus_totaux:,.0f} euros")
        print(f"Pertes attendues: {pertes_attendues:,.0f} euros")
        print(f"Profit net: {profit_net:,.0f} euros")
        print(f"Risque moyen: {risque_moyen*100:.2f}%")
        if montant_total_alloue > 0:
            print(f"ROI net: {(profit_net/montant_total_alloue)*100:.2f}%")

        # Vérifier les allocations par catégorie
        print("\nVérification des allocations par catégorie:")
        for categorie, pct_target in repartition_scenario1.items():
            mask = (clients_solvables['loan_intent'] == categorie).values
            montant_categorie = np.sum(Mi * Yi_optimal * mask)
            pct_reel = (montant_categorie / montant_total_alloue) * 100 if montant_total_alloue > 0 else 0
            print(f"  {categorie}: {pct_reel:.1f}% (cible: {pct_target*100:.0f}%)")

        # Ajouter les résultats au DataFrame
        clients_solvables['Yi_optimal'] = Yi_optimal
        clients_solvables['credit_alloue'] = Yi_optimal
        clients_solvables['montant_alloue'] = Mi * Yi_optimal
        clients_solvables['revenus_attendus'] = Mi * Yi_optimal * ri
        clients_solvables['pertes_attendues'] = Mi * Yi_optimal * PD * LGD
        clients_solvables['profit_net'] = clients_solvables['revenus_attendus'] - clients_solvables['pertes_attendues']

    else:
        print("✗ Échec de l'optimisation:", result.message)
        # En cas d'échec, utiliser une approche heuristique simple
        print("🔄 Application d'une approche heuristique...")

        # Trier les clients par profit net décroissant
        profit_net_individuel = Mi * ri - PD * LGD * Mi
        indices_tries = np.argsort(-profit_net_individuel)

        Yi_heuristique = np.zeros(N, dtype=int)
        budget_utilise = 0
        risque_cumule = 0

        for idx in indices_tries:
            nouveau_budget = budget_utilise + Mi[idx]
            nouveau_risque_total = risque_cumule + Mi[idx] * PD[idx]
            nouveau_risque_moyen = nouveau_risque_total / nouveau_budget if nouveau_budget > 0 else 0

            if (nouveau_budget <= BUDGET_UTILISE and
                nouveau_risque_moyen <= TAUX_RISQUE):
                Yi_heuristique[idx] = 1
                budget_utilise = nouveau_budget
                risque_cumule = nouveau_risque_total

        # Calculer les métriques de la solution heuristique
        clients_selectionnes = np.sum(Yi_heuristique)
        montant_total_alloue = np.sum(Mi * Yi_heuristique)
        revenus_totaux = np.sum(Mi * Yi_heuristique * ri)
        pertes_attendues = np.sum(Mi * Yi_heuristique * PD * LGD)
        profit_net = revenus_totaux - pertes_attendues
        risque_moyen = np.sum(Mi * Yi_heuristique * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

        print(f"Solution heuristique: {clients_selectionnes:,} clients")
        print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
        print(f"Profit net: {profit_net:,.0f} euros")
        print(f"Risque: {risque_moyen*100:.2f}%")

        # Ajouter les résultats au DataFrame
        clients_solvables['Yi_optimal'] = Yi_heuristique
        clients_solvables['credit_alloue'] = Yi_heuristique
        clients_solvables['montant_alloue'] = Mi * Yi_heuristique
        clients_solvables['revenus_attendus'] = Mi * Yi_heuristique * ri
        clients_solvables['pertes_attendues'] = Mi * Yi_heuristique * PD * LGD
        clients_solvables['profit_net'] = clients_solvables['revenus_attendus'] - clients_solvables['pertes_attendues']
        clients_solvables['revenus_attendus'] = Mi * Yi_heuristique * ri

except Exception as e:
    print(f"Erreur lors de l'optimisation: {e}")
    # Solution de secours très simple

    # Sélectionner les 1000 premiers clients avec le plus faible risque
    indices_faible_risque = np.argsort(PD)[:min(1000, len(PD))]
    Yi_secours = np.zeros(N, dtype=int)

    budget_utilise = 0
    for idx in indices_faible_risque:
        if budget_utilise + Mi[idx] <= BUDGET_TOTAL:
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

# 8. Analyse des résultats par objectif de prêt
print("\n8. ANALYSE DES RÉSULTATS PAR OBJECTIF DE PRÊT")
print("-" * 40)

if 'credit_alloue' in clients_solvables.columns:
    # Clients sélectionnés
    clients_selectionnes_df = clients_solvables[clients_solvables['credit_alloue'] == 1]
    
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
    
    for objectif in repartition_scenario1.keys():
        if objectif in analyse_par_objectif.index:
            montant_reel = analyse_par_objectif.loc[objectif, 'Montant_Total']
            pourcentage_reel = (montant_reel / montant_total_reel) * 100
            pourcentage_cible = repartition_scenario1[objectif] * 100
            print(f"• {objectif}: Cible {pourcentage_cible:.0f}% vs Réel {pourcentage_reel:.1f}%")

# Créer le dossier de résultats
import os
os.makedirs('scenario_1_results', exist_ok=True)

# Génération des visualisations (optionnel)
if 'credit_alloue' in clients_solvables.columns and 'analyse_par_objectif' in locals():
    try:
        # Graphique simple de répartition
        plt.figure(figsize=(10, 6))
        objectifs = list(analyse_par_objectif.index)
        montants = analyse_par_objectif['Montant_Total'].values

        plt.pie(montants, labels=objectifs, autopct='%1.1f%%', startangle=90)
        plt.title('Répartition des Montants par Objectif de Prêt')
        plt.savefig('scenario_1_results/repartition_montants.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("Visualisations sauvegardées")
    except Exception as e:
        print(f"Erreur lors de la génération des graphiques: {e}")

# 7. Export des résultats
print("\n7. Export des résultats")

if 'credit_alloue' in clients_solvables.columns:
    clients_approuves = clients_solvables[clients_solvables['Yi_optimal'] == 1].copy()

    print(f"Clients approuvés: {len(clients_approuves)} sur {len(clients_solvables)}")

    if len(clients_approuves) == 0:
        print("Aucun client approuvé - application de critères de secours")

        if len(clients_solvables) >= 100:
            score_qualite = (
                (clients_solvables['person_income'] / 100000) * 0.3 +
                (clients_solvables['person_emp_length'] / 10) * 0.2 +
                (clients_solvables['cb_person_cred_hist_length'] / 15) * 0.2 +
                ((1 - clients_solvables['PD_calibrée']) * 2) * 0.3
            )

            top_clients_indices = score_qualite.nlargest(100).index
            clients_solvables.loc[top_clients_indices, 'Yi_optimal'] = 1
            clients_solvables.loc[top_clients_indices, 'credit_alloue'] = 1

            clients_approuves = clients_solvables[clients_solvables['Yi_optimal'] == 1].copy()
            print(f"Sélection de secours: {len(clients_approuves)} clients")
        else:
            print("Dataset trop petit pour générer un résultat")
            exit(1)

    # Préparer les données finales avec seulement les clients approuvés
    resultats_scenario1 = clients_approuves[[
        'loan_percent_income', 'cb_person_cred_hist_length', 'person_emp_length',
        'person_age', 'person_income', 'loan_int_rate', 'person_home_ownership_RENT',
        'montant_demande', 'loan_intent', 'PD_calibrée', 'Yi_optimal',
        'montant_alloue', 'revenus_attendus', 'pertes_attendues', 'profit_net'
    ]].copy()

    # Renommer les colonnes pour correspondre aux exigences
    resultats_scenario1.rename(columns={
        'montant_demande': 'loan_amnt',
        'Yi_optimal': 'Yi'
    }, inplace=True)

    # Renommer Yi_optimal en Yi pour correspondre au format de l'exemple
    # Tous les clients dans ce dataset ont Yi = 1 (approuvés)
    resultats_scenario1.rename(columns={'Yi_optimal': 'Yi'}, inplace=True)

    # Convertir person_home_ownership_RENT en 0/1 au lieu de True/False
    resultats_scenario1['person_home_ownership_RENT'] = resultats_scenario1['person_home_ownership_RENT'].astype(int)

    # Sauvegarder au format Excel (comme l'exemple)
    output_filename = 'Scenario_1_Optimisation_Resultats.xlsx'

    try:
        resultats_scenario1.to_excel(output_filename, index=False, engine='openpyxl')
    except PermissionError:
        print(f"⚠️  Fichier {output_filename} ouvert dans Excel. Tentative avec un nouveau nom...")
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f'Scenario_1_Optimisation_Resultats_{timestamp}.xlsx'
        resultats_scenario1.to_excel(output_filename, index=False, engine='openpyxl')
    except Exception as e:
        print(f"✗ Erreur lors de l'export: {e}")
        # Export en CSV en cas d'échec
        output_filename = 'Scenario_1_Optimisation_Resultats.csv'
        resultats_scenario1.to_csv(output_filename, index=False)
        print(f"✓ Export réalisé en CSV: {output_filename}")

    print(f"Résultats exportés vers: {output_filename}")
    print(f"Format: {len(resultats_scenario1)} clients approuvés")

    # Statistiques finales
    clients_approuves_total = len(resultats_scenario1)
    clients_analyses_total = len(clients_solvables)
    taux_approbation = (clients_approuves_total / clients_analyses_total) * 100

    print(f"\nRésultats finaux:")
    print(f"Clients analysés: {clients_analyses_total:,}")
    print(f"Clients approuvés: {clients_approuves_total:,}")
    print(f"Taux d'approbation: {taux_approbation:.1f}%")
    print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
    print(f"Budget utilisé: {(montant_total_alloue/BUDGET_TOTAL)*100:.1f}%")
    print(f"Budget total utilisé: {(montant_total_alloue/BUDGET_TOTAL)*100:.1f}%")
    print(f"ROI estimé: {(revenus_totaux/montant_total_alloue)*100:.2f}%")

    # Export détaillé pour analyse
    os.makedirs('scenario_1_results', exist_ok=True)

    # Fichier détaillé avec toutes les informations
    clients_solvables_detail = clients_solvables[[
        'loan_percent_income', 'cb_person_cred_hist_length', 'person_emp_length',
        'person_age', 'person_income', 'loan_int_rate', 'person_home_ownership_RENT',
        'PD_calibrée', 'Yi', 'montant_demande', 'loan_intent', 'taux_rendement',
        'Yi_optimal', 'credit_alloue', 'montant_alloue', 'revenus_attendus'
    ]].copy()

    with pd.ExcelWriter('scenario_1_results/Scenario_1_Analyse_Complete.xlsx', engine='openpyxl') as writer:
        # Feuille 1: Résultats principaux (format exemple)
        resultats_scenario1.to_excel(writer, sheet_name='Resultats_Principaux', index=False)

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
                'Seuil de solvabilité',
                'HOMEIMPROVEMENT (%)',
                'VENTURE (%)',
                'EDUCATION (%)',
                'PERSONAL (%)',
                'MEDICAL (%)',
                'DEBTCONSOLIDATION (%)'
            ],
            'Valeur': [
                'Expansion Prudente',
                TAUX_RISQUE * 100,
                BUDGET_TOTAL,
                0.30,
                repartition_scenario1['HOMEIMPROVEMENT'] * 100,
                repartition_scenario1['VENTURE'] * 100,
                repartition_scenario1['EDUCATION'] * 100,
                repartition_scenario1['PERSONAL'] * 100,
                repartition_scenario1['MEDICAL'] * 100,
                repartition_scenario1['DEBTCONSOLIDATION'] * 100
            ]
        })
        parametres_scenario.to_excel(writer, sheet_name='Parametres_Scenario', index=False)

    print(f"✓ Analyse complète exportée vers 'scenario_1_results/Scenario_1_Analyse_Complete.xlsx'")

else:
    print("✗ Erreur: Les données d'optimisation ne sont pas disponibles")

# 8. Validation finale
print("\n8. Validation de la conformité")

if 'credit_alloue' in clients_solvables.columns:
    clients_finaux = clients_solvables[clients_solvables['credit_alloue'] == 1]

    if len(clients_finaux) > 0:
        risque_final = np.average(clients_finaux['PD_calibrée'], weights=clients_finaux['montant_alloue'])
        age_moyen = clients_finaux['person_age'].mean()
        revenu_moyen = clients_finaux['person_income'].mean()
        emploi_stable = (clients_finaux['person_emp_length'] >= 2).mean() * 100
        historique_bon = (clients_finaux['cb_person_cred_hist_length'] >= 3).mean() * 100
        ratio_pret_revenu = clients_finaux['loan_percent_income'].mean() * 100

        print("Conformité aux exigences:")
        print(f"Risque <= 10%: {risque_final*100:.2f}% ({'OK' if risque_final <= 0.10 else 'NOK'})")
        print(f"Emploi stable: {emploi_stable:.1f}% ({'OK' if emploi_stable >= 80 else 'NOK'})")
        print(f"Bon historique: {historique_bon:.1f}% ({'OK' if historique_bon >= 80 else 'NOK'})")
        print(f"Age approprié: {age_moyen:.1f} ans ({'OK' if 25 <= age_moyen <= 50 else 'NOK'})")
        print(f"Revenus décents: {revenu_moyen:,.0f} euros ({'OK' if revenu_moyen >= 50000 else 'NOK'})")

        criteres_respectes = [
            risque_final <= 0.10,
            emploi_stable >= 80,
            historique_bon >= 80,
            25 <= age_moyen <= 50,
            revenu_moyen >= 50000,
            ratio_pret_revenu <= 20
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
else:
    statut = "ECHEC"

print(f"\nScénario 1 complété - Statut: {statut}")
print("Résultats sauvegardés dans 'scenario_1_results/'")
print("-" * 60)
