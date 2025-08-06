"""
Data Quality Analysis Script
Analyzes the credit risk dataset for abnormal values and data inconsistencies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data_quality(df):
    """
    Comprehensive data quality analysis
    """
    print("=" * 60)
    print("DATA QUALITY ANALYSIS REPORT")
    print("=" * 60)
    
    # Basic dataset info
    print(f"\n1. DATASET OVERVIEW")
    print(f"Total records: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Missing values
    print(f"\n2. MISSING VALUES")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values found")
    
    # Duplicate records
    print(f"\n3. DUPLICATE RECORDS")
    duplicates = df.duplicated().sum()
    print(f"Duplicate records: {duplicates:,}")
    
    # Age analysis
    print(f"\n4. AGE ANALYSIS")
    if 'person_age' in df.columns:
        age_stats = df['person_age'].describe()
        print(f"Age statistics:")
        print(age_stats)
        
        # Abnormal ages
        abnormal_ages = df[(df['person_age'] < 18) | (df['person_age'] > 100)]
        print(f"Abnormal ages (< 18 or > 100): {len(abnormal_ages):,}")
        if len(abnormal_ages) > 0:
            print(f"Age range: {abnormal_ages['person_age'].min()} to {abnormal_ages['person_age'].max()}")
    
    # Employment length analysis
    print(f"\n5. EMPLOYMENT LENGTH ANALYSIS")
    if 'person_emp_length' in df.columns:
        emp_stats = df['person_emp_length'].describe()
        print(f"Employment length statistics:")
        print(emp_stats)
        
        # Employment length > age (impossible)
        if 'person_age' in df.columns:
            impossible_emp = df[df['person_emp_length'] > df['person_age']]
            print(f"Employment length > age: {len(impossible_emp):,}")
            
            # Employment length > 80 years (unrealistic)
            long_emp = df[df['person_emp_length'] > 80]
            print(f"Employment length > 80 years: {len(long_emp):,}")
            
            # Negative employment length
            negative_emp = df[df['person_emp_length'] < 0]
            print(f"Negative employment length: {len(negative_emp):,}")
    
    # Income analysis
    print(f"\n6. INCOME ANALYSIS")
    if 'person_income' in df.columns:
        income_stats = df['person_income'].describe()
        print(f"Income statistics:")
        print(income_stats)
        
        # Unrealistic incomes
        zero_income = df[df['person_income'] <= 0]
        print(f"Zero or negative income: {len(zero_income):,}")
        
        very_high_income = df[df['person_income'] > 10_000_000]  # > 10M
        print(f"Income > 10M: {len(very_high_income):,}")
    
    # Credit history length analysis
    print(f"\n7. CREDIT HISTORY ANALYSIS")
    if 'cb_person_cred_hist_length' in df.columns:
        hist_stats = df['cb_person_cred_hist_length'].describe()
        print(f"Credit history statistics:")
        print(hist_stats)
        
        # Credit history > age (impossible)
        if 'person_age' in df.columns:
            impossible_hist = df[df['cb_person_cred_hist_length'] > df['person_age']]
            print(f"Credit history > age: {len(impossible_hist):,}")
            
            # Credit history > 80 years (unrealistic)
            long_hist = df[df['cb_person_cred_hist_length'] > 80]
            print(f"Credit history > 80 years: {len(long_hist):,}")
            
            # Negative credit history
            negative_hist = df[df['cb_person_cred_hist_length'] < 0]
            print(f"Negative credit history: {len(negative_hist):,}")
    
    # Loan amount analysis
    print(f"\n8. LOAN AMOUNT ANALYSIS")
    if 'loan_amnt' in df.columns:
        loan_stats = df['loan_amnt'].describe()
        print(f"Loan amount statistics:")
        print(loan_stats)
        
        # Zero or negative loans
        zero_loan = df[df['loan_amnt'] <= 0]
        print(f"Zero or negative loan amount: {len(zero_loan):,}")
        
        # Very high loans
        very_high_loan = df[df['loan_amnt'] > 1_000_000]  # > 1M
        print(f"Loan amount > 1M: {len(very_high_loan):,}")
    
    # Interest rate analysis
    print(f"\n9. INTEREST RATE ANALYSIS")
    if 'loan_int_rate' in df.columns:
        rate_stats = df['loan_int_rate'].describe()
        print(f"Interest rate statistics:")
        print(rate_stats)
        
        # Unrealistic rates
        zero_rate = df[df['loan_int_rate'] <= 0]
        print(f"Zero or negative interest rate: {len(zero_rate):,}")
        
        very_high_rate = df[df['loan_int_rate'] > 100]  # > 100%
        print(f"Interest rate > 100%: {len(very_high_rate):,}")
    
    # Loan to income ratio analysis
    print(f"\n10. LOAN-TO-INCOME RATIO ANALYSIS")
    if 'loan_percent_income' in df.columns:
        ratio_stats = df['loan_percent_income'].describe()
        print(f"Loan-to-income ratio statistics:")
        print(ratio_stats)
        
        # Unrealistic ratios
        zero_ratio = df[df['loan_percent_income'] <= 0]
        print(f"Zero or negative ratio: {len(zero_ratio):,}")
        
        very_high_ratio = df[df['loan_percent_income'] > 5]  # > 500%
        print(f"Ratio > 500%: {len(very_high_ratio):,}")
    
    return df

def identify_outliers(df):
    """
    Identify all outliers that need to be removed
    """
    print(f"\n" + "=" * 60)
    print("OUTLIERS TO REMOVE")
    print("=" * 60)
    
    outliers_mask = pd.Series([False] * len(df), index=df.index)
    outlier_reasons = []
    
    # Age outliers
    if 'person_age' in df.columns:
        age_outliers = (df['person_age'] < 18) | (df['person_age'] > 100)
        outliers_mask |= age_outliers
        outlier_reasons.extend(['Age < 18 or > 100'] * age_outliers.sum())
        print(f"Age outliers: {age_outliers.sum():,}")
    
    # Employment length outliers
    if 'person_emp_length' in df.columns and 'person_age' in df.columns:
        emp_outliers = (df['person_emp_length'] > df['person_age']) | (df['person_emp_length'] > 80) | (df['person_emp_length'] < 0)
        outliers_mask |= emp_outliers
        outlier_reasons.extend(['Employment length issues'] * emp_outliers.sum())
        print(f"Employment length outliers: {emp_outliers.sum():,}")
    
    # Income outliers
    if 'person_income' in df.columns:
        income_outliers = (df['person_income'] <= 0) | (df['person_income'] > 10_000_000)
        outliers_mask |= income_outliers
        outlier_reasons.extend(['Income issues'] * income_outliers.sum())
        print(f"Income outliers: {income_outliers.sum():,}")
    
    # Credit history outliers
    if 'cb_person_cred_hist_length' in df.columns and 'person_age' in df.columns:
        hist_outliers = (df['cb_person_cred_hist_length'] > df['person_age']) | (df['cb_person_cred_hist_length'] > 80) | (df['cb_person_cred_hist_length'] < 0)
        outliers_mask |= hist_outliers
        outlier_reasons.extend(['Credit history issues'] * hist_outliers.sum())
        print(f"Credit history outliers: {hist_outliers.sum():,}")
    
    # Loan amount outliers
    if 'loan_amnt' in df.columns:
        loan_outliers = (df['loan_amnt'] <= 0) | (df['loan_amnt'] > 1_000_000)
        outliers_mask |= loan_outliers
        outlier_reasons.extend(['Loan amount issues'] * loan_outliers.sum())
        print(f"Loan amount outliers: {loan_outliers.sum():,}")
    
    # Interest rate outliers
    if 'loan_int_rate' in df.columns:
        rate_outliers = (df['loan_int_rate'] <= 0) | (df['loan_int_rate'] > 100)
        outliers_mask |= rate_outliers
        outlier_reasons.extend(['Interest rate issues'] * rate_outliers.sum())
        print(f"Interest rate outliers: {rate_outliers.sum():,}")
    
    # Loan-to-income ratio outliers
    if 'loan_percent_income' in df.columns:
        ratio_outliers = (df['loan_percent_income'] <= 0) | (df['loan_percent_income'] > 5)
        outliers_mask |= ratio_outliers
        outlier_reasons.extend(['Loan-to-income ratio issues'] * ratio_outliers.sum())
        print(f"Loan-to-income ratio outliers: {ratio_outliers.sum():,}")
    
    print(f"\nTotal outliers to remove: {outliers_mask.sum():,} ({(outliers_mask.sum()/len(df)*100):.2f}%)")
    
    return outliers_mask

if __name__ == "__main__":
    # Load and analyze the dataset
    try:
        df = pd.read_excel('content/credit_risk_dataset.xlsx')
        print(f"Loaded dataset with {len(df):,} records")
        
        # Analyze data quality
        df_analyzed = analyze_data_quality(df)
        
        # Identify outliers
        outliers_mask = identify_outliers(df)
        
        # Show sample of outliers
        if outliers_mask.sum() > 0:
            print(f"\nSample of outliers:")
            outliers_sample = df[outliers_mask].head(10)
            print(outliers_sample[['person_age', 'person_emp_length', 'person_income', 'cb_person_cred_hist_length', 'loan_amnt', 'loan_int_rate', 'loan_percent_income']])
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
