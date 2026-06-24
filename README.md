# Institut Supérieur Polytechnique de Madagascar (ISPM)

**Projet : Fanoron-telo avec IA**

---

# Section 1 : En-tête Institutionnel et Identification

- Site officiel de l'ISPM : https://www.ispm-edu.com
- Nom du groupe : Little Geeks

| Nom complet | Numéro d'étudiant | Classe | Rôle précis pour ce Hackathon |
|------------|-------------------|---------|-------------------------------|
| FANOMEZANTSOA Maminirina Aina Fitiavana | 08 | ESIIA 4 | Lead AI Engeneer - Conception des Algorithmes |
| RAKOTONDRANAIVO Tsiory Mihajanirina | 09 | ESIIA 4 | Développeur frontend - Interractions et Fonctionalités |
| ANDRIANTOVOSOA Aina Harentsoa | 19 | ESIIA 4 | Expert en OptimisationIA et Bitboards |
| RAZANAKOLONA Joanna Tsiafoy | 20 | ESIIA 4 | Product Owner, QA et Rédacteur Technique |
| FIFALIANASOA Aina Nomenjanahary | 22 | ESIIA 4 | Lead DevOps et Déploiement |
| RAHANITRINOMENA Heriarimanitra Fitianà | 31 | ESIIA 4 | UI/UX Lead Designer et Développeur Frontend |
---

# Section 2 : Description du Travail Réalisé

## Présentation générale

Cette application implémente le jeu traditionnel malgache **Fanoron-telo** sur un plateau 3x3. Elle propose plusieurs modes de jeu :

- Humain vs Humain
- Humain vs IA (Facile)
- Humain vs IA (Moyen)
- Humain vs IA (Difficile)
- IA vs IA (mode démonstration)

## Fonctionnalités implémentées

- Gestion complète des règles du Fanoron-telo
- Validation des mouvements
- Détection automatique des victoires
- Interface utilisateur interactive
- Plusieurs niveaux de difficulté IA
- Historique des coups
- Undo / Redo (si implémenté)
- Animations et effets visuels (si implémentés)

## Architecture et Stack Technologique

### Frontend
- HTML5 / CSS3
- JavaScript

### Backend
- Python

### Intelligence Artificielle
- Algorithme Minimax
- Élagage Alpha-Bêta

## Déploiement


Dépôt Git :
- URL : https://github.com/Little-Geeks/TP-Algo-avancee-23-06-26

---

# Section 3 : Guide d'Installation Rapide (3 commandes max)

```bash
git clone https://github.com/Little-Geeks/TP-Algo-avancee-23-06-26
npm install
npm run dev

cd backend
 
# Créer l'environnement virtuel:
python3 -m venv venv

# Activer l'environnemet virtuel:
venv\Scripts\activate.bat
```
- Ouvrir index.html dans un navigateur

---

# Section 4 : Outils d'Aide IA Utilisés

## Outils utilisés

- ChatGPT
- GLM
- Claude

## Utilisation

Les assistants IA ont été utilisés pour :

- Génération de structures de code
- Conception des algorithmes
- Débogage
- Optimisation du Minimax
- Génération de documentation
- Création de cas de tests

## Gain obtenu

L'utilisation de ces outils a permis :

- Une réduction du temps de développement
- Une meilleure qualité du code
- Une accélération des phases de test et de correction

---

# Section 5 : Modélisation et Algorithmes de l'IA du Jeu

## Représentation du plateau

Le plateau est représenté sous forme d'une matrice 3x3 :

```text
0  1  2
3  4  5
6  7  8
```

Chaque case peut contenir :

- 0 : vide
- 1 : joueur humain
- 2 : IA

## Algorithme Minimax

L'intelligence artificielle repose sur l'algorithme Minimax qui explore les états futurs du jeu afin de sélectionner le meilleur coup possible.

### Fonction d'évaluation

L'évaluation prend en compte :

- Alignement potentiel de 3 pions
- Blocage de l'adversaire
- Possibilités de victoire au prochain tour
- Contrôle des positions stratégiques

## Élagage Alpha-Bêta

L'algorithme Alpha-Bêta est utilisé afin de réduire le nombre d'états explorés.

### Avantages

- Réduction du temps de calcul
- Recherche plus profonde
- Meilleure réactivité de l'IA

## Techniques avancées

### Table de transposition

Mémorisation des états déjà évalués afin d'éviter les calculs redondants.

### Iterative Deepening

Recherche progressive avec augmentation graduelle de la profondeur.

### Opening Book

Bibliothèque de coups d'ouverture prédéfinis.

### Machine Learning

Possibilité d'apprentissage basé sur des parties enregistrées.

---

# Section 6 : Analyse des Performances

## Temps moyen de réponse

| Niveau IA | Temps moyen |
|------------|------------|
| Facile |  |
| Moyen |  |
| Difficile |  |

## Résultats IA vs IA

| Confrontation | Résultat |
|--------------|-----------|
| Difficile vs Moyen |  |
| Moyen vs Facile |  |
| Difficile vs Facile |  |

## Métriques supplémentaires

- Nombre moyen de nœuds explorés
- Profondeur moyenne atteinte
- Temps maximal observé
- Taux de victoire par niveau

---

# Conclusion

Le projet Fanoron-telo avec IA démontre l'application pratique des algorithmes de recherche adversariale tels que Minimax et Alpha-Bêta dans un jeu de stratégie traditionnel malgache. L'objectif principal a été de proposer une expérience de jeu fluide tout en offrant différents niveaux de difficulté adaptés aux utilisateurs.
