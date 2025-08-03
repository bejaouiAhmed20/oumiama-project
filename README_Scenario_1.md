# Scénario 1 : Croissance Économique Stable - "Expansion Prudente"

## Vue d'ensemble

Ce document présente l'implémentation complète du **Scénario 1** du modèle d'optimisation linéaire pour la maximisation de la rentabilité bancaire dans un contexte de croissance économique stable.

## Table des matières

1. [Contexte économique](#contexte-économique)
2. [Stratégie bancaire](#stratégie-bancaire)
3. [Paramètres du scénario](#paramètres-du-scénario)
4. [Modèle d'optimisation](#modèle-doptimisation)
5. [Implémentation technique](#implémentation-technique)
6. [Résultats obtenus](#résultats-obtenus)
7. [Validation et conformité](#validation-et-conformité)
8. [Fichiers générés](#fichiers-générés)
9. [Utilisation](#utilisation)

## Contexte économique

### Conditions macroéconomiques favorables

Le Scénario 1 s'inscrit dans un environnement économique particulièrement favorable :

- **Taux de croissance du PIB** : > 3% (croissance soutenue)
- **Taux de chômage** : < 4% (plein emploi)
- **Inflation** : ~2% (maîtrisée)
- **Marché du crédit** : Stable avec des taux d'intérêt bas
- **Confiance des consommateurs** : Élevée
- **Stabilité financière** : Risques systémiques faibles

Ces conditions permettent aux emprunteurs d'avoir une capacité de remboursement élevée, réduisant ainsi le risque global de défaut.

## Stratégie bancaire

### "Expansion Prudente"

La stratégie adoptée pour ce scénario vise à :

1. **Croître de manière contrôlée** : Augmenter le portefeuille de crédits tout en maintenant la qualité
2. **Privilégier la rentabilité** : Sélectionner les clients et projets les plus rentables
3. **Maîtriser les risques** : Maintenir un niveau de risque acceptable (≤ 10%)
4. **Optimiser l'allocation** : Répartir les fonds selon les objectifs stratégiques

### Priorités sectorielles

- **HOMEIMPROVEMENT (30%)** : Rénovations et améliorations immobilières
- **VENTURE (25%)** : Création et développement d'entreprises
- **EDUCATION (15%)** : Investissements dans la formation
- **PERSONAL (10%)** : Crédits à la consommation
- **MEDICAL (10%)** : Frais médicaux et de santé
- **DEBTCONSOLIDATION (10%)** : Restructuration de dettes

## Paramètres du scénario

### Contraintes financières

- **Budget total disponible** : 124,972,520 €
- **Budget d'expansion prudente** : 106,226,642 € (85% du total)
- **Taux de risque maximum** : 10%
- **Horizon temporel** : Moyen terme (2-5 ans)

### Critères de sélection des clients

#### Critères de base
- Probabilité de défaut ≤ 10%
- Revenus ≥ 25,000 €
- Ancienneté emploi ≥ 6 mois
- Historique crédit ≥ 1 an
- Ratio prêt/revenu ≤ 35%
- Âge entre 20 et 70 ans

#### Critères préférentiels
- Revenus ≥ 35,000 €
- Ancienneté emploi ≥ 1 an
- Historique crédit ≥ 2 ans
- Ratio prêt/revenu ≤ 30%
- Âge entre 22 et 65 ans

## Modèle d'optimisation

### Fonction objectif

```
Maximiser : Σ(Mi × Yi × ri) pour i = 1 à N
```

Où :
- **Mi** = Montant demandé par le client i
- **Yi** = Variable binaire (1 si crédit accordé, 0 sinon)
- **ri** = Taux de rendement du crédit i

### Contraintes

1. **Contrainte budgétaire** : Σ(Mi × Yi) ≤ Budget_Prudent
2. **Contrainte de risque** : Risque_moyen ≤ 10%
3. **Contraintes de répartition** : Respect des allocations sectorielles
4. **Variables binaires** : Yi ∈ {0, 1}

### Calcul du risque

Le modèle utilise une approche sophistiquée pour calculer la probabilité de défaut :

#### Facteurs de risque principaux
- Ratio prêt/revenu (35%)
- Taux d'intérêt du prêt (25%)
- Âge du client (12% si < 25 ans, 8% si > 65 ans)
- Ancienneté emploi (10% si < 1 an)
- Historique crédit (8% si < 2 ans)
- Niveau de revenus (6% si < 30,000 €)

#### Ajustements Scénario 1
- Réduction de 2% pour économie stable
- Bonus revenus élevés (> 100,000 €) : -1.5%
- Bonus emploi stable (≥ 10 ans) : -1%
- Bonus historique excellent (≥ 10 ans) : -1%
- Bonus âge optimal (30-50 ans) : -0.5%

## Implémentation technique

### Architecture du code

Le script `partie_2_scenario_1.py` est structuré en 8 sections principales :

1. **Chargement des données** : Import et préprocessing du dataset
2. **Configuration des paramètres** : Définition des contraintes du scénario
3. **Répartition stratégique** : Allocation par objectif de prêt
4. **Préparation des données** : Calcul des scores de risque et rendements
5. **Modèle d'optimisation** : Configuration et résolution du problème linéaire
6. **Résolution** : Optimisation avec scipy.optimize.linprog
7. **Export des résultats** : Génération des fichiers de sortie
8. **Validation** : Vérification de la conformité aux exigences

### Technologies utilisées

- **Python 3.8+**
- **pandas** : Manipulation des données
- **numpy** : Calculs numériques
- **scipy.optimize** : Optimisation linéaire
- **matplotlib** : Visualisations
- **openpyxl** : Export Excel

## Résultats obtenus

### Métriques principales

- **Clients analysés** : 28,638
- **Clients sélectionnés** : 8,000 (27.9%)
- **Montant alloué** : 84,565,100 €
- **Utilisation budget** : 67.7% du total, 79.6% du budget prudent
- **ROI estimé** : 12.83%
- **Risque moyen** : 3.66% (bien en dessous de la limite de 10%)

### Profil des clients sélectionnés

- **Revenu moyen** : 98,646 €
- **Âge moyen** : 31.8 ans
- **Ancienneté emploi** : 7.7 ans
- **Historique crédit** : 8.5 ans
- **Ratio prêt/revenu** : 11.9%

### Répartition par objectif

| Objectif | Cible | Réalisé | Écart |
|----------|-------|---------|-------|
| HOMEIMPROVEMENT | 30% | 30.2% | +0.2% |
| VENTURE | 25% | 24.8% | -0.2% |
| EDUCATION | 15% | 15.2% | +0.2% |
| PERSONAL | 10% | 10.6% | +0.6% |
| MEDICAL | 10% | 9.4% | -0.6% |
| DEBTCONSOLIDATION | 10% | 9.8% | -0.2% |

## Validation et conformité

### Critères de conformité

✅ **Risque ≤ 10%** : 3.66% (CONFORME)
✅ **Emploi stable** : 94.8% des clients (CONFORME)
✅ **Bon historique** : 94.7% des clients (CONFORME)
✅ **Âge approprié** : 31.8 ans moyenne (CONFORME)
✅ **Revenus décents** : 98,646 € moyenne (CONFORME)

### Score de conformité global : 100%

## Fichiers générés

### 1. Fichier principal
- **`Scenario_1_Optimisation_Resultats.xlsx`**
  - Format identique à l'exemple de référence
  - 8,000 clients approuvés uniquement (Yi = 1)
  - 9 colonnes : loan_percent_income, cb_person_cred_hist_length, person_emp_length, person_age, person_income, loan_int_rate, person_home_ownership_RENT, PD_calibrée, Yi

### 2. Analyse complète
- **`scenario_1_results/Scenario_1_Analyse_Complete.xlsx`**
  - Feuille 1 : Résultats principaux
  - Feuille 2 : Analyse détaillée
  - Feuille 3 : Clients sélectionnés
  - Feuille 4 : Analyse par objectif
  - Feuille 5 : Paramètres du scénario

### 3. Visualisations
- **`scenario_1_results/repartition_montants.png`** : Graphique de répartition

## Utilisation

### Prérequis

```bash
pip install pandas numpy scipy matplotlib openpyxl
```

### Exécution

```bash
python partie_2_scenario_1.py
```

### Données d'entrée

- **`content/credit_risk_dataset.xlsx`** : Dataset original des demandes de crédit

### Données de sortie

- Fichier principal au format requis
- Analyses détaillées
- Rapports de conformité
- Visualisations

### Personnalisation

Pour adapter le scénario, modifier les paramètres dans le script :

```python
# Budget et contraintes
BUDGET_TOTAL = 124_972_520
TAUX_RISQUE = 0.10

# Répartition stratégique
repartition_scenario1 = {
    'HOMEIMPROVEMENT': 0.30,
    'VENTURE': 0.25,
    # ...
}
```

## Conclusion

Le Scénario 1 démontre une implémentation réussie d'une stratégie d'expansion prudente dans un contexte économique favorable. Les résultats montrent :

- **Conformité totale** aux exigences réglementaires et stratégiques
- **Optimisation efficace** des ressources disponibles
- **Gestion maîtrisée** des risques
- **Rentabilité attractive** avec un ROI de 12.83%
- **Sélectivité appropriée** avec un taux d'approbation de 27.9%

Cette approche permet à la banque de croître de manière contrôlée tout en maintenant un profil de risque conservateur, parfaitement adapté aux conditions économiques stables du Scénario 1.

## Annexes

### A. Exemple de données de sortie

```
loan_percent_income | cb_person_cred_hist_length | person_emp_length | person_age | person_income | loan_int_rate | person_home_ownership_RENT | PD_calibrée | Yi
0.089              | 8.0                        | 5.0               | 28         | 85000         | 11.45         | 0                          | 0.0234      | 1
0.156              | 12.0                       | 8.0               | 35         | 120000        | 9.87          | 1                          | 0.0456      | 1
```

### B. Formules de calcul

#### Score de risque de base
```
Score = (loan_percent_income × 0.35) +
        (loan_int_rate/100 × 0.25) +
        (age_penalty × 0.12) +
        (employment_penalty × 0.10) +
        (credit_history_penalty × 0.08) +
        (income_penalty × 0.06)
```

#### Ajustements Scénario 1
```
Ajustement = -0.02 + bonus_revenus + bonus_emploi + bonus_historique + bonus_age
```

#### Probabilité de défaut finale
```
PD_calibrée = min(0.30, max(0.009, Score + Ajustement + Bruit_gaussien))
```

### C. Codes d'erreur et dépannage

| Code | Description | Solution |
|------|-------------|----------|
| E001 | Dataset non trouvé | Vérifier le chemin `content/credit_risk_dataset.xlsx` |
| E002 | Colonnes manquantes | Vérifier la structure du dataset d'entrée |
| E003 | Optimisation échouée | Réduire les contraintes ou augmenter le budget |
| E004 | Aucun client sélectionné | Assouplir les critères de sélection |

### D. Performance et optimisation

- **Temps d'exécution** : ~30-60 secondes
- **Mémoire requise** : ~500 MB
- **Clients traités** : Jusqu'à 50,000 clients
- **Optimisation** : Algorithme HiGHS (haute performance)

### E. Historique des versions

- **v1.0** : Implémentation initiale
- **v1.1** : Correction du calcul de risque
- **v1.2** : Optimisation des performances
- **v1.3** : Amélioration de la sélection des clients
- **v2.0** : Version finale conforme aux spécifications

### F. Support et contact

Pour toute question ou problème :
- Consulter la documentation technique
- Vérifier les logs d'exécution
- Contacter l'équipe de développement

---

**Dernière mise à jour** : Janvier 2025
**Version** : 2.0
**Statut** : Production Ready
