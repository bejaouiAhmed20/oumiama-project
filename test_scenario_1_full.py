"""
Test Full Scenario 1 with Data Cleaning - Simplified Version
"""

import pandas as pd
import numpy as np
from data_cleaning_module import clean_dataset
from scipy.optimize import linprog

print("SCENARIO 1 - EXPANSION PRUDENTE (WITH DATA CLEANING)")
print("=" * 60)

try:
    # 1. Load and clean data
    df_original = pd.read_excel('content/credit_risk_dataset.xlsx')
    print(f"Dataset original: {df_original.shape[0]} clients")

    # Data cleaning and validation
    df_clean, cleaning_report = clean_dataset(df_original, "Scénario 1 - Expansion Prudente")
    
    # Preprocessing
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
    print(f"Features disponibles: {len(available_features)}")

    # 2. Calculate risk scores (simplified)
    np.random.seed(42)
    base_risk_score = (
        (df['loan_percent_income'] * 0.35) +
        (df['loan_int_rate'] / 100 * 0.25) +
        ((df['person_age'] < 25).astype(int) * 0.12) +
        ((df['person_age'] > 65).astype(int) * 0.08) +
        ((df['person_emp_length'] < 1).astype(int) * 0.1) +
        ((df['cb_person_cred_hist_length'] < 2).astype(int) * 0.08) +
        ((df['person_income'] < 30000).astype(int) * 0.06)
    )

    scenario1_adjustments = (
        -0.02 +
        -(df['person_income'] > 100000).astype(int) * 0.015 +
        -(df['person_emp_length'] >= 10).astype(int) * 0.01 +
        -(df['cb_person_cred_hist_length'] >= 10).astype(int) * 0.01 +
        -(df['person_age'].between(30, 50)).astype(int) * 0.005
    )

    df['risk_score'] = np.maximum(0.005, base_risk_score + scenario1_adjustments)
    
    noise = np.random.normal(0, 0.01, len(df))
    df['PD_calibrée'] = np.minimum(0.30, np.maximum(0.009, df['risk_score'] + noise))
    
    seuil_optimal = 0.30
    df['Yi'] = (df['PD_calibrée'] <= seuil_optimal).astype(int)
    
    clients_solvables = df[df['Yi'] == 1].copy()
    print(f"Clients solvables: {len(clients_solvables)} / {len(df)} ({(len(clients_solvables)/len(df))*100:.1f}%)")

    # 3. Parameters
    BUDGET_TOTAL = 124_972_520
    TAUX_RISQUE = 0.10
    BUDGET_PRUDENT = int(BUDGET_TOTAL * 0.85)

    print(f"Budget total disponible: {BUDGET_TOTAL:,} euros")
    print(f"Budget pour expansion prudente: {BUDGET_PRUDENT:,} euros (85%)")
    print(f"Taux de risque cible: {TAUX_RISQUE*100}%")

    # 4. Loan distribution
    repartition_scenario1 = {
        'HOMEIMPROVEMENT': 0.30,
        'VENTURE': 0.25,
        'EDUCATION': 0.15,
        'PERSONAL': 0.10,
        'MEDICAL': 0.10,
        'DEBTCONSOLIDATION': 0.10
    }

    # 5. Prepare optimization data
    np.random.seed(42)
    clients_solvables['montant_demande'] = clients_solvables['loan_amnt'].astype(int)
    
    # Assign loan intents
    objectifs = list(repartition_scenario1.keys())
    probabilites = list(repartition_scenario1.values())
    clients_solvables['loan_intent'] = np.random.choice(
        objectifs, size=len(clients_solvables), p=probabilites
    )

    # Calculate return rates
    def calculer_taux_rendement(row):
        base_rate = row['loan_int_rate'] / 100
        ajustements = {
            'HOMEIMPROVEMENT': 0.02,
            'VENTURE': 0.03,
            'EDUCATION': 0.01,
            'PERSONAL': 0.005,
            'MEDICAL': 0.005,
            'DEBTCONSOLIDATION': 0.015
        }
        return base_rate + ajustements.get(row['loan_intent'], 0)

    clients_solvables['taux_rendement'] = clients_solvables.apply(calculer_taux_rendement, axis=1)

    print(f"Données préparées: {len(clients_solvables)} clients")
    print(f"Montant moyen demandé: {clients_solvables['montant_demande'].mean():,.0f} euros")
    print(f"Taux de rendement moyen: {clients_solvables['taux_rendement'].mean()*100:.2f}%")

    # 6. Simple selection (top 8000 clients by quality score)
    N = len(clients_solvables)
    Mi = clients_solvables['montant_demande'].values
    ri = clients_solvables['taux_rendement'].values
    PD = clients_solvables['PD_calibrée'].values

    # Quality score for selection
    score_qualite = (
        (1 - PD) * 0.35 +
        (clients_solvables['person_income'] / 150000) * 0.25 +
        (clients_solvables['person_emp_length'] / 20) * 0.20 +
        (clients_solvables['cb_person_cred_hist_length'] / 25) * 0.20
    )

    # Select top 8000 clients
    top_indices = score_qualite.nlargest(min(8000, len(clients_solvables))).index
    Yi_optimal = np.zeros(N, dtype=int)
    Yi_optimal[clients_solvables.index.get_indexer(top_indices)] = 1

    clients_selectionnes = np.sum(Yi_optimal)
    montant_total_alloue = np.sum(Mi * Yi_optimal)
    revenus_totaux = np.sum(Mi * Yi_optimal * ri)
    risque_moyen = np.sum(Mi * Yi_optimal * PD) / montant_total_alloue if montant_total_alloue > 0 else 0

    print(f"\n7. RÉSULTATS FINAUX")
    print(f"Clients sélectionnés: {clients_selectionnes:,} / {N:,}")
    print(f"Montant alloué: {montant_total_alloue:,.0f} euros")
    print(f"Utilisation budget: {(montant_total_alloue/BUDGET_PRUDENT)*100:.1f}%")
    print(f"Revenus attendus: {revenus_totaux:,.0f} euros")
    print(f"Rentabilité: {(revenus_totaux/montant_total_alloue)*100:.2f}%")
    print(f"Risque moyen: {risque_moyen*100:.2f}%")

    # Add results to dataframe
    clients_solvables['Yi_optimal'] = Yi_optimal
    clients_solvables['credit_alloue'] = Yi_optimal
    clients_solvables['montant_alloue'] = Mi * Yi_optimal
    clients_solvables['revenus_attendus'] = Mi * Yi_optimal * ri

    # 8. Analysis by loan objective
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
        
        print(f"\n8. ANALYSE PAR OBJECTIF DE PRÊT")
        print(analyse_par_objectif)
        
        # Compare strategy vs realization
        print(f"\nComparaison Stratégie vs Réalisation:")
        montant_total_reel = analyse_par_objectif['Montant_Total'].sum()
        
        for objectif in repartition_scenario1.keys():
            if objectif in analyse_par_objectif.index:
                montant_reel = analyse_par_objectif.loc[objectif, 'Montant_Total']
                pourcentage_reel = (montant_reel / montant_total_reel) * 100
                pourcentage_cible = repartition_scenario1[objectif] * 100
                print(f"• {objectif}: Cible {pourcentage_cible:.0f}% vs Réel {pourcentage_reel:.1f}%")

    # 9. Final validation
    clients_finaux = clients_solvables[clients_solvables['credit_alloue'] == 1]
    
    if len(clients_finaux) > 0:
        risque_final = np.average(clients_finaux['PD_calibrée'], weights=clients_finaux['montant_alloue'])
        age_moyen = clients_finaux['person_age'].mean()
        revenu_moyen = clients_finaux['person_income'].mean()
        
        print(f"\n9. VALIDATION FINALE")
        print(f"Risque final: {risque_final*100:.2f}% ({'OK' if risque_final <= 0.10 else 'NOK'})")
        print(f"Age moyen: {age_moyen:.1f} ans")
        print(f"Revenu moyen: {revenu_moyen:,.0f} euros")
        print(f"Nombre de clients: {len(clients_finaux):,}")
        
        # Data quality final check
        emp_gt_age = (clients_finaux['person_emp_length'] > clients_finaux['person_age']).sum()
        hist_gt_age = (clients_finaux['cb_person_cred_hist_length'] > clients_finaux['person_age']).sum()
        age_issues = ((clients_finaux['person_age'] < 18) | (clients_finaux['person_age'] > 100)).sum()
        
        print(f"\nDATA QUALITY FINAL CHECK:")
        print(f"Employment > Age: {emp_gt_age} ({'OK' if emp_gt_age == 0 else 'NOK'})")
        print(f"Credit History > Age: {hist_gt_age} ({'OK' if hist_gt_age == 0 else 'NOK'})")
        print(f"Age issues: {age_issues} ({'OK' if age_issues == 0 else 'NOK'})")
        
        if emp_gt_age == 0 and hist_gt_age == 0 and age_issues == 0:
            print("✅ SCENARIO 1 - 100% DATA QUALITY COMPLIANT!")
        else:
            print("❌ Data quality issues still present")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
