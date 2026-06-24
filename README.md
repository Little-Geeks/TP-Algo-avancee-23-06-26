# Institut Supérieur Polytechnique de Madagascar (ISPM)

**Projet : Fanoron-telo avec IA**

---

# Section 1 : En-tête Institutionnel et Identification

- Site officiel de l'ISPM : https://www.ispm-edu.com
- Nom du groupe : Little Geeks

| Nom complet | Numéro d'étudiant | Classe | Rôle précis pour ce Hackathon |
|------------|-------------------|---------|-------------------------------|
| FANOMEZANTSOA Maminirina Aina Fitiavana | À compléter | À compléter | Lead IA |
| À compléter | À compléter | À compléter | Développeur Frontend |
| À compléter | À compléter | À compléter | Développeur Backend |

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
- JavaScript / TypeScript
- React (si utilisé)

### Backend
- Node.js (si utilisé)

### Intelligence Artificielle
- Algorithme Minimax
- Élagage Alpha-Bêta

## Déploiement

Application en ligne :
- URL : **[À compléter]**

Dépôt Git :
- URL : **[À compléter]**

---

# Section 3 : Guide d'Installation Rapide (3 commandes max)

```bash
git clone <url_du_depot>
npm install
npm run dev
```

Ou avec un projet Python :

```bash
git clone <url_du_depot>
pip install -r requirements.txt
python main.py
```

---

# Section 4 : Outils d'Aide IA Utilisés

## Outils utilisés

- ChatGPT
- GitHub Copilot
- Claude (si utilisé)

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
a1  b1  c1
a2  b2  c2
a3  b3  c3
```

Chaque case peut contenir :

- 0 : vide
- 1 : joueur humain
- -1 : IA

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

## Techniques avancées (si implémentées)

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
| Facile | À mesurer |
| Moyen | À mesurer |
| Difficile | À mesurer |

## Résultats IA vs IA

| Confrontation | Résultat |
|--------------|-----------|
| Difficile vs Moyen | À compléter |
| Moyen vs Facile | À compléter |
| Difficile vs Facile | À compléter |

## Métriques supplémentaires

- Nombre moyen de nœuds explorés
- Profondeur moyenne atteinte
- Temps maximal observé
- Taux de victoire par niveau

---

# Conclusion

Le projet Fanoron-telo avec IA démontre l'application pratique des algorithmes de recherche adversariale tels que Minimax et Alpha-Bêta dans un jeu de stratégie traditionnel malgache. L'objectif principal a été de proposer une expérience de jeu fluide tout en offrant différents niveaux de difficulté adaptés aux utilisateurs.
