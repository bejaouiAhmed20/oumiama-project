"""
Test Scenario 1 with Data Cleaning
"""

import pandas as pd
import numpy as np
from data_cleaning_module import clean_dataset

print("TESTING SCENARIO 1 WITH DATA CLEANING")
print("=" * 50)

try:
    # Load original data
    df_original = pd.read_excel('content/credit_risk_dataset.xlsx')
    print(f"Original dataset: {len(df_original):,} records")
    
    # Clean the data
    df_clean, cleaning_report = clean_dataset(df_original, "Scenario 1 Test")
    
    # Basic preprocessing
    df = df_clean.copy()
    df = df.dropna()
    print(f"After dropna: {len(df):,} records")
    
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
    
    # Verify data quality after cleaning
    print("\nDATA QUALITY VERIFICATION:")
    print(f"Age range: {df['person_age'].min():.0f} to {df['person_age'].max():.0f}")
    print(f"Employment length range: {df['person_emp_length'].min():.1f} to {df['person_emp_length'].max():.1f}")
    print(f"Credit history range: {df['cb_person_cred_hist_length'].min():.1f} to {df['cb_person_cred_hist_length'].max():.1f}")
    
    # Check for impossible values
    emp_gt_age = (df['person_emp_length'] > df['person_age']).sum()
    hist_gt_age = (df['cb_person_cred_hist_length'] > df['person_age']).sum()
    age_issues = ((df['person_age'] < 18) | (df['person_age'] > 100)).sum()
    
    print(f"\nQUALITY CHECKS:")
    print(f"Employment > Age: {emp_gt_age} records")
    print(f"Credit History > Age: {hist_gt_age} records") 
    print(f"Age issues (< 18 or > 100): {age_issues} records")
    
    if emp_gt_age == 0 and hist_gt_age == 0 and age_issues == 0:
        print("✅ ALL DATA QUALITY CHECKS PASSED!")
    else:
        print("❌ DATA QUALITY ISSUES STILL PRESENT!")
    
    print(f"\nFinal dataset ready for optimization: {len(df):,} records")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
