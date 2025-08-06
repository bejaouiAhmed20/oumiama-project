"""
Data Cleaning Module for Banking Optimization Scenarios
Comprehensive data validation and outlier removal functions
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def clean_dataset(df, scenario_name="Unknown"):
    """
    Comprehensive data cleaning function to remove abnormal values
    
    Parameters:
    df: pandas DataFrame - the raw dataset
    scenario_name: str - name of the scenario for logging
    
    Returns:
    df_clean: pandas DataFrame - cleaned dataset
    cleaning_report: dict - report of cleaning actions
    """
    
    print(f"\n{'='*60}")
    print(f"DATA CLEANING REPORT - {scenario_name}")
    print(f"{'='*60}")
    
    # Initialize cleaning report
    cleaning_report = {
        'original_records': len(df),
        'removed_records': 0,
        'final_records': 0,
        'cleaning_actions': []
    }
    
    df_clean = df.copy()
    initial_count = len(df_clean)
    
    print(f"Original dataset: {initial_count:,} records")
    
    # 1. Remove records with unrealistic ages
    print(f"\n1. AGE VALIDATION")
    age_issues = (df_clean['person_age'] < 18) | (df_clean['person_age'] > 100)
    age_removed = age_issues.sum()
    
    if age_removed > 0:
        print(f"   Removing {age_removed:,} records with age < 18 or > 100")
        print(f"   Age range of removed records: {df_clean[age_issues]['person_age'].min():.0f} to {df_clean[age_issues]['person_age'].max():.0f}")
        df_clean = df_clean[~age_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {age_removed} records with unrealistic ages")
    else:
        print(f"   ✓ No age issues found")
    
    # 2. Remove records with impossible employment lengths
    print(f"\n2. EMPLOYMENT LENGTH VALIDATION")
    emp_issues = (
        (df_clean['person_emp_length'] > df_clean['person_age']) |  # Employment > age
        (df_clean['person_emp_length'] > 80) |  # Employment > 80 years
        (df_clean['person_emp_length'] < 0)     # Negative employment
    )
    emp_removed = emp_issues.sum()
    
    if emp_removed > 0:
        print(f"   Removing {emp_removed:,} records with employment length issues")
        # Show specific issues
        emp_gt_age = (df_clean['person_emp_length'] > df_clean['person_age']).sum()
        emp_gt_80 = (df_clean['person_emp_length'] > 80).sum()
        emp_negative = (df_clean['person_emp_length'] < 0).sum()
        
        if emp_gt_age > 0:
            print(f"   - Employment > age: {emp_gt_age:,} records")
        if emp_gt_80 > 0:
            print(f"   - Employment > 80 years: {emp_gt_80:,} records")
        if emp_negative > 0:
            print(f"   - Negative employment: {emp_negative:,} records")
            
        df_clean = df_clean[~emp_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {emp_removed} records with employment length issues")
    else:
        print(f"   ✓ No employment length issues found")
    
    # 3. Remove records with impossible credit history lengths
    print(f"\n3. CREDIT HISTORY VALIDATION")
    hist_issues = (
        (df_clean['cb_person_cred_hist_length'] > df_clean['person_age']) |  # History > age
        (df_clean['cb_person_cred_hist_length'] > 80) |  # History > 80 years
        (df_clean['cb_person_cred_hist_length'] < 0)     # Negative history
    )
    hist_removed = hist_issues.sum()
    
    if hist_removed > 0:
        print(f"   Removing {hist_removed:,} records with credit history issues")
        # Show specific issues
        hist_gt_age = (df_clean['cb_person_cred_hist_length'] > df_clean['person_age']).sum()
        hist_gt_80 = (df_clean['cb_person_cred_hist_length'] > 80).sum()
        hist_negative = (df_clean['cb_person_cred_hist_length'] < 0).sum()
        
        if hist_gt_age > 0:
            print(f"   - Credit history > age: {hist_gt_age:,} records")
        if hist_gt_80 > 0:
            print(f"   - Credit history > 80 years: {hist_gt_80:,} records")
        if hist_negative > 0:
            print(f"   - Negative credit history: {hist_negative:,} records")
            
        df_clean = df_clean[~hist_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {hist_removed} records with credit history issues")
    else:
        print(f"   ✓ No credit history issues found")
    
    # 4. Remove records with unrealistic income values
    print(f"\n4. INCOME VALIDATION")
    income_issues = (
        (df_clean['person_income'] <= 0) |  # Zero or negative income
        (df_clean['person_income'] > 10_000_000)  # Income > 10M (unrealistic)
    )
    income_removed = income_issues.sum()
    
    if income_removed > 0:
        print(f"   Removing {income_removed:,} records with income issues")
        zero_income = (df_clean['person_income'] <= 0).sum()
        high_income = (df_clean['person_income'] > 10_000_000).sum()
        
        if zero_income > 0:
            print(f"   - Zero/negative income: {zero_income:,} records")
        if high_income > 0:
            print(f"   - Income > 10M: {high_income:,} records")
            
        df_clean = df_clean[~income_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {income_removed} records with income issues")
    else:
        print(f"   ✓ No income issues found")
    
    # 5. Remove records with unrealistic loan amounts
    print(f"\n5. LOAN AMOUNT VALIDATION")
    loan_issues = (
        (df_clean['loan_amnt'] <= 0) |  # Zero or negative loan
        (df_clean['loan_amnt'] > 1_000_000)  # Loan > 1M (very high)
    )
    loan_removed = loan_issues.sum()
    
    if loan_removed > 0:
        print(f"   Removing {loan_removed:,} records with loan amount issues")
        zero_loan = (df_clean['loan_amnt'] <= 0).sum()
        high_loan = (df_clean['loan_amnt'] > 1_000_000).sum()
        
        if zero_loan > 0:
            print(f"   - Zero/negative loan: {zero_loan:,} records")
        if high_loan > 0:
            print(f"   - Loan > 1M: {high_loan:,} records")
            
        df_clean = df_clean[~loan_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {loan_removed} records with loan amount issues")
    else:
        print(f"   ✓ No loan amount issues found")
    
    # 6. Remove records with unrealistic interest rates
    print(f"\n6. INTEREST RATE VALIDATION")
    rate_issues = (
        (df_clean['loan_int_rate'] <= 0) |  # Zero or negative rate
        (df_clean['loan_int_rate'] > 100)   # Rate > 100%
    )
    rate_removed = rate_issues.sum()
    
    if rate_removed > 0:
        print(f"   Removing {rate_removed:,} records with interest rate issues")
        zero_rate = (df_clean['loan_int_rate'] <= 0).sum()
        high_rate = (df_clean['loan_int_rate'] > 100).sum()
        
        if zero_rate > 0:
            print(f"   - Zero/negative rate: {zero_rate:,} records")
        if high_rate > 0:
            print(f"   - Rate > 100%: {high_rate:,} records")
            
        df_clean = df_clean[~rate_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {rate_removed} records with interest rate issues")
    else:
        print(f"   ✓ No interest rate issues found")
    
    # 7. Remove records with unrealistic loan-to-income ratios
    print(f"\n7. LOAN-TO-INCOME RATIO VALIDATION")
    ratio_issues = (
        (df_clean['loan_percent_income'] <= 0) |  # Zero or negative ratio
        (df_clean['loan_percent_income'] > 5)     # Ratio > 500%
    )
    ratio_removed = ratio_issues.sum()
    
    if ratio_removed > 0:
        print(f"   Removing {ratio_removed:,} records with loan-to-income ratio issues")
        zero_ratio = (df_clean['loan_percent_income'] <= 0).sum()
        high_ratio = (df_clean['loan_percent_income'] > 5).sum()
        
        if zero_ratio > 0:
            print(f"   - Zero/negative ratio: {zero_ratio:,} records")
        if high_ratio > 0:
            print(f"   - Ratio > 500%: {high_ratio:,} records")
            
        df_clean = df_clean[~ratio_issues]
        cleaning_report['cleaning_actions'].append(f"Removed {ratio_removed} records with ratio issues")
    else:
        print(f"   ✓ No loan-to-income ratio issues found")
    
    # 8. Remove duplicate records
    print(f"\n8. DUPLICATE RECORDS VALIDATION")
    duplicates = df_clean.duplicated()
    dup_removed = duplicates.sum()
    
    if dup_removed > 0:
        print(f"   Removing {dup_removed:,} duplicate records")
        df_clean = df_clean[~duplicates]
        cleaning_report['cleaning_actions'].append(f"Removed {dup_removed} duplicate records")
    else:
        print(f"   ✓ No duplicate records found")
    
    # Final statistics
    final_count = len(df_clean)
    total_removed = initial_count - final_count
    
    print(f"\n{'='*60}")
    print(f"CLEANING SUMMARY")
    print(f"{'='*60}")
    print(f"Original records:    {initial_count:,}")
    print(f"Records removed:     {total_removed:,} ({(total_removed/initial_count*100):.2f}%)")
    print(f"Final clean records: {final_count:,} ({(final_count/initial_count*100):.2f}%)")
    
    # Update cleaning report
    cleaning_report['removed_records'] = total_removed
    cleaning_report['final_records'] = final_count
    
    # Validate data consistency after cleaning
    print(f"\n9. POST-CLEANING VALIDATION")
    validate_cleaned_data(df_clean)
    
    return df_clean, cleaning_report

def validate_cleaned_data(df):
    """
    Validate that the cleaned data meets all consistency requirements
    """
    issues = []
    
    # Check age consistency
    if (df['person_age'] < 18).any() or (df['person_age'] > 100).any():
        issues.append("Age issues still present")
    
    # Check employment consistency
    if (df['person_emp_length'] > df['person_age']).any():
        issues.append("Employment > age still present")
    if (df['person_emp_length'] > 80).any():
        issues.append("Employment > 80 years still present")
    if (df['person_emp_length'] < 0).any():
        issues.append("Negative employment still present")
    
    # Check credit history consistency
    if (df['cb_person_cred_hist_length'] > df['person_age']).any():
        issues.append("Credit history > age still present")
    if (df['cb_person_cred_hist_length'] > 80).any():
        issues.append("Credit history > 80 years still present")
    if (df['cb_person_cred_hist_length'] < 0).any():
        issues.append("Negative credit history still present")
    
    # Check income consistency
    if (df['person_income'] <= 0).any():
        issues.append("Zero/negative income still present")
    if (df['person_income'] > 10_000_000).any():
        issues.append("Income > 10M still present")
    
    # Check loan amount consistency
    if (df['loan_amnt'] <= 0).any():
        issues.append("Zero/negative loan amount still present")
    if (df['loan_amnt'] > 1_000_000).any():
        issues.append("Loan > 1M still present")
    
    # Check interest rate consistency
    if (df['loan_int_rate'] <= 0).any():
        issues.append("Zero/negative interest rate still present")
    if (df['loan_int_rate'] > 100).any():
        issues.append("Interest rate > 100% still present")
    
    # Check ratio consistency
    if (df['loan_percent_income'] <= 0).any():
        issues.append("Zero/negative ratio still present")
    if (df['loan_percent_income'] > 5).any():
        issues.append("Ratio > 500% still present")
    
    if issues:
        print(f"   ⚠️  VALIDATION ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"   ✅ All data consistency checks passed")
        return True
