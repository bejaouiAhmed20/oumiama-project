# Projet d'Optimisation Bancaire

## Vue d'Ensemble

Ce projet implémente un système d'optimisation pour l'allocation de crédits bancaires basé sur deux scénarios économiques distincts. Le système utilise des algorithmes d'optimisation pour maximiser la rentabilité tout en respectant les contraintes de risque.

## Objectifs du Projet

- Optimiser l'allocation des crédits selon les conditions économiques
- Minimiser les risques tout en maximisant la rentabilité
- Respecter les répartitions stratégiques par type de prêt
- Garantir la qualité des données avec un nettoyage automatique

## Structure du Projet

### Fichiers Principaux
- `partie_2_scenario_1.py` - Scénario 1: Expansion Prudente
- `partie_2_scenario_2.py` - Scénario 2: Sécurisation des Actifs
- `data_cleaning_module.py` - Module de nettoyage des données

### Données
- `content/credit_risk_dataset.xlsx` - Dataset principal (32,582 clients)

### Documentation
- `README_Scenario_1.md` - Guide du Scénario 1
- `README_Scenario_2.md` - Guide du Scénario 2

### Résultats
- `Scenario_1_Optimisation_Resultats.xlsx` - Résultats Scénario 1 (8,000 clients)
- `Scenario_2_Optimisation_Resultats.xlsx` - Résultats Scénario 2 (7,000 clients)

## Scénarios Implémentés

### Scénario 1: Expansion Prudente
**Contexte**: Croissance économique stable
- PIB en croissance élevée (> 3%)
- Chômage faible (< 4%)
- Inflation modérée (~2%)
- Marché du crédit stable

**Stratégie**:
- Favoriser les prêts à long terme et projets rentables
- Focus sur HOMEIMPROVEMENT et VENTURE
- Taux de risque: 10% maximum
- Clients sélectionnés: 8,000

**Répartition des prêts**:
- HOMEIMPROVEMENT: 30% (Amélioration habitat)
- VENTURE: 25% (Création d'entreprise)
- EDUCATION: 15% (Éducation)
- PERSONAL: 10% (Personnel)
- MEDICAL: 10% (Médical)
- DEBTCONSOLIDATION: 10% (Consolidation dettes)

### Scénario 2: Sécurisation des Actifs
**Contexte**: Ralentissement économique
- PIB en faible croissance (1-2%)
- Chômage en hausse (7-8%)
- Inflation stable mais sous pression
- Marché du crédit tendu

**Stratégie**:
- Privilégier les prêts à court terme et faible risque
- Focus sur EDUCATION et MEDICAL (besoins essentiels)
- Taux de risque: 5% maximum
- Clients sélectionnés: 6,500-7,500

**Répartition des prêts**:
- EDUCATION: 30% (Éducation - priorité)
- MEDICAL: 30% (Médical - priorité)
- PERSONAL: 15% (Personnel)
- VENTURE: 10% (Création d'entreprise)
- HOMEIMPROVEMENT: 10% (Amélioration habitat)
- DEBTCONSOLIDATION: 10% (Consolidation dettes)

## Utilisation

### Exécution des Scénarios

Scénario 1 - Expansion Prudente:
```bash
python partie_2_scenario_1.py
```

Scénario 2 - Sécurisation des Actifs:
```bash
python partie_2_scenario_2.py
```

### Résultats Générés
Chaque scénario génère automatiquement:
- Fichier Excel avec les clients sélectionnés
- Analyses de répartition des montants
- Rapports de conformité

## Qualité des Données

### Nettoyage Automatique
Le système élimine automatiquement:
- Ages irréalistes (< 18 ou > 100 ans): 5 records supprimés
- Durées d'emploi impossibles (> âge): 2 records supprimés
- Durées d'emploi irréalistes (> 80 ans): 2 records supprimés
- Montants de prêt extrêmes (> 1M euros): 1 record supprimé
- Ratios incohérents (≤ 0): 8 records supprimés
- Doublons: 165 records supprimés

**Résultat**: 32,401 records propres (99.44% de rétention)

### Validation
- 0 valeurs aberrantes restantes
- 100% de cohérence des données
- Validation automatique de tous les critères

## Résultats et Performance

### Scénario 1 - Résultats
- Clients sélectionnés: 8,000
- Montant alloué: 84,407,250 euros
- ROI: 12.82%
- Risque final: 4.43% (≤ 10%)
- Conformité: 100%

### Scénario 2 - Résultats
- Clients sélectionnés: 7,000
- Montant alloué: 68,602,600 euros
- ROI: 10.26%
- Risque final: 4.66% (≤ 5%)
- Conformité: 100%

## Statut de Conformité

### Validation
- Qualité des données: 100% validée
- Scénario 1: 100% conforme aux exigences
- Scénario 2: 100% conforme aux exigences
- Nettoyage automatique intégré
- Tous les tests passés avec succès

Le système est prêt pour la production avec garantie de qualité des données.

## Technologies Utilisées

- Python 3.x - Langage principal
- Pandas - Manipulation des données
- NumPy - Calculs numériques
- SciPy - Optimisation mathématique
- Matplotlib - Visualisations
- OpenPyXL - Export Excel

## Documentation

- [README_Scenario_1.md](README_Scenario_1.md) - Documentation du Scénario 1
- [README_Scenario_2.md](README_Scenario_2.md) - Documentation du Scénario 2

## Démarrage Rapide

1. Installer les dépendances: `pip install pandas numpy scipy matplotlib openpyxl`
2. Exécuter Scénario 1: `python partie_2_scenario_1.py`
3. Exécuter Scénario 2: `python partie_2_scenario_2.py`
4. Consulter les résultats dans les fichiers Excel générés

Système validé et prêt pour la production avec 100% de conformité aux exigences.
