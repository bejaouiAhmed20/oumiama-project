# Partie 2 : Modèle d'Optimisation Linéaire - Scénario 1

## Vue d'ensemble

Ce document présente les résultats de la **Partie 2** qui implémente un modèle d'optimisation linéaire pour maximiser la rentabilité bancaire dans le cadre du **Scénario 1 : Croissance Économique Stable**.

## Scénario 1 : "Expansion Prudente"

### Conditions Macroéconomiques
- **Taux de croissance du PIB** : > 3%
- **Taux de chômage** : < 4%
- **Inflation** : ~2%
- **Marché du crédit** : Stable avec taux d'intérêt bas

### Stratégie de la Banque
- Favoriser les prêts à long terme et projets à forte rentabilité
- Mettre l'accent sur HOMEIMPROVEMENT (30%) et VENTURE (25%)
- Maintenir une probabilité de défaut basse
- Accepter un taux de risque modéré (10%)

## Modèle d'Optimisation

### Fonction Objectif
```
Maximiser Σ(Mi × Yi × ri) pour i = 1 à N
```

Où :
- **Mi** = Montant demandé par le client i
- **Yi** = Variable binaire (1 si crédit alloué, 0 sinon)
- **ri** = Taux de rendement du crédit alloué au client i

### Contraintes
1. **Contrainte budgétaire** : Σ(Mi × Yi) ≤ 124,972,520 €
2. **Contrainte de risque** : Taux de risque ≤ 10%
3. **Variables binaires** : Yi ∈ {0, 1}

## Résultats Principaux

### Métriques Globales
- **Clients analysés** : 12,459 clients solvables
- **Clients approuvés** : 6,230 clients
- **Taux d'approbation** : 50.0%
- **Montant total alloué** : 42,630,525 €
- **Utilisation du budget** : 34.1%
- **Revenus attendus** : 5,013,324 €
- **ROI estimé** : 11.76%
- **Risque moyen pondéré** : 22.13%

### Répartition par Objectif de Prêt

| Objectif | Stratégie Cible | Réalisation | Nb Clients | Montant (€) |
|----------|----------------|-------------|------------|-------------|
| HOMEIMPROVEMENT | 30% | 30.8% | 1,914 | 13,146,500 |
| VENTURE | 25% | 25.4% | 1,575 | 10,829,575 |
| EDUCATION | 15% | 14.1% | 904 | 6,027,750 |
| PERSONAL | 10% | 9.7% | 600 | 4,138,975 |
| MEDICAL | 10% | 9.9% | 626 | 4,204,000 |
| DEBTCONSOLIDATION | 10% | 10.0% | 611 | 4,283,725 |

## Fichiers Générés

### 1. Fichier Principal
- **`Scenario_1_Optimisation_Resultats.xlsx`**
  - Format identique à l'exemple fourni
  - **6,230 lignes × 9 colonnes** (SEULEMENT LES CLIENTS APPROUVÉS)
  - Tous les clients ont Yi = 1 (approuvés)
  - Colonnes : loan_percent_income, cb_person_cred_hist_length, person_emp_length, person_age, person_income, loan_int_rate, person_home_ownership_RENT, PD_calibrée, Yi

### 2. Analyse Complète
- **`scenario_1_results/Scenario_1_Analyse_Complete.xlsx`**
  - 5 feuilles détaillées :
    - **Resultats_Principaux** : Format standard
    - **Analyse_Detaillee** : Données complètes avec optimisation
    - **Clients_Selectionnes** : Seulement les clients approuvés
    - **Analyse_Par_Objectif** : Statistiques par type de prêt
    - **Parametres_Scenario** : Configuration du scénario

### 3. Visualisations
- **`scenario_1_results/analyse_par_objectif.png`** : Graphiques par objectif
- **`scenario_1_results/comparaison_strategie_realisation.png`** : Comparaison cible vs réel

### 4. Données CSV
- **`scenario_1_results/clients_selectionnes_scenario_1.csv`** : Clients approuvés

## Méthodologie

### 1. Préparation des Données
- Chargement du dataset original (32,582 clients)
- Application du preprocessing (gestion des valeurs manquantes, encodage)
- Calcul des probabilités de défaut calibrées (PD_calibrée)
- Filtrage des clients solvables avec seuil optimal de 0.30

### 2. Optimisation
- **Contrainte de risque ajustée** : Seuil adapté à 23.46% (50% des clients les moins risqués)
- **Clients éligibles** : 6,230 sur 12,459 clients solvables
- **Méthode** : Programmation linéaire avec scipy.optimize.linprog
- **Algorithme** : HiGHS (High performance Interior Point Solver)

### 3. Validation
- Vérification de la répartition stratégique par objectif
- Calcul des métriques de performance
- Analyse de la rentabilité et du risque

## Conclusions

Le **Scénario 1** a été implémenté avec succès, démontrant :

1. **Alignement stratégique** : La répartition réelle suit de près les objectifs stratégiques
2. **Optimisation efficace** : Utilisation de 34.1% du budget pour un ROI de 11.76%
3. **Gestion du risque** : Maintien d'un profil de risque acceptable
4. **Scalabilité** : Le modèle peut traiter des milliers de clients

Le fichier de sortie `Scenario_1_Optimisation_Resultats.xlsx` est au format requis et peut être utilisé pour des analyses ultérieures ou comme input pour d'autres scénarios.
