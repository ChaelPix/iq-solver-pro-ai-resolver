# Rapport IA41 : IQ Puzzler Pro

[toc]

*– un rappel de l'énoncé du problème,
– votre spécification (formalisation) du problème,
– l'analyse du problème,
– la méthode proposée, avec en annexe le listing du programme commenté,
– la description détaillée d'une ou de plusieurs situations traitées par votre programme,
– les résultats obtenus par votre programme sur ces situations,
– les difficultés éventuellement rencontrées,
– les améliorations possibles (méthodes de résolution) et
– les perspectives d'ouverture possibles du sujet traité.*


## I/ Présentation du projet

### Contextualisation

Le projet porte sur le jeu IQ Puzzler Pro, un puzzle assez connu dont l’objectif est de compléter des grilles en positionnant correctement des pièces de formes variées.

Nous avons identifié trois questions fondamentales à résoudre dans ce contexte :  
- **Comment représenter les différentes pièces, en tenant compte de leurs variations de rotations ?**  
- **Comment résoudre efficacement les niveaux du jeu IQ Puzzler Pro ?**  
- **Comment concevoir et implémenter un algorithme capable de résoudre automatiquement chaque niveau ?**

Pour débuter, nous avons commandé le jeu afin de l’explorer concrètement : pour manipuler les pièces, comprendre leurs interactions et résoudre manuellement plusieurs niveaux. Cela nous à permis de réfléchir aux problématiques liées à la représentation du jeu, à la résolution et d’identifier des stratégies potentiellement efficaces.

Nous avons choisi de concentrer notre travail sur le mode de jeu principal, qui repose sur une grille de 5 x 11 cases et des pièces avec chacune 8 variantes possibles (rotations et symétries incluses).

Les niveaux du jeu sont répartis en plusieurs paliers de difficulté croissante. Grâce à nos essais pratiques et à des recherches en ligne auprès de forums de passionnés, nous avons constaté que la résolution humaine reposait sur la même stratégie : tester différentes configurations en plaçant d’abord les pièces les plus grandes, souvent le long des bords ou autour des éléments déjà positionnés.

À partir de ces observations, nous avons choisi d’implémenter un algorithme de **backtracking** avec des optimisations comme l’exploration de l’espace des solutions, et des heuristiques comme la prioritisation des pièces de plus grandes tailles afin de limiter le nombre de calculs

### Vue globale du projet

#### Classes
Voici une représentation de notre projet sous forme de diagramme UML de classes, afin de montrer une vue d’ensemble sur la conception et la structure globale.  

![Diagramme UML de classe]()  
*Figure 1 : Diagramme de classes UML du projet*  

Nous avons veillé à bien séparer la logique algorithmique de l’interface utilisateur. Cette séparation permet de réutiliser l’interface dans d’autres contextes, indépendamment de l’algorithme. 

L’algorithme lui-même a été structuré en plusieurs classes afin de segmenter les différents modules qui le composent afin d'une meilleure facilité de maintenance et de compréhension.

#### Séquences  
Voici une représentation des interactions entre les différents acteurs et composants de notre projet, illustrée par un diagramme UML de séquences.  

![Diagramme UML de séquence]()  
*Figure 2 : Diagramme de séquence UML du projet*  

#### États et transitions  
Enfin, pour mieux comprendre le déroulement principal de notre programme, voici un diagramme d’états et de transitions.

![Diagramme UML d’états et transitions]()  
*Figure 3 : Diagramme d’états et transitions UML du projet*  

### Les outils utilisés

Pour la réalisation de ce projet, nous avons utilisé les outils suivants :  

- **Langage de programmation : Python**  
  Nous avions peur de ne pas avoir le temps d'assez explorer le projet et d'être découragés en utilisant le langage Prolog. Nous avons ainsi préféré choisir Python.

- **Interface utilisateur : Tkinter**  
  Nous avons utilisé Tkinter pour concevoir et implémenter l’interface graphique. Afin de réaliser nos premiers tests, cet outil nous a permis de rapidement visualiser nos résultats.  Nous avons ensuite continué à développer notre classe d'interface tout au long de nos avancées, et il est finalement devenu trop tard pour envisager un changement d'interface, malgré les limites liées au multithreading.

- **Gestion de version : GitHub**  
  Pour la gestion de notre projet, Github est un outil indispensable que ce soit pour le versionning, le système de branches pour nos tests, le travail collaboratif.

## II/ Pieces & Tableau

### Représentation des éléments du jeu

Le tableau est simple à représenter : c'est une matrice de la taille du plateau, `5x11`. 

```python
class Plateau:
    def __init__(self, lignes=5, colonnes=11):
        self.lignes = lignes  
        self.colonnes = colonnes  
        self.plateau = np.zeros((lignes, colonnes), dtype=int) # remplissage du tabeau avec des 0
```

Puis, pour faciliter l'intéraction avec ce dernier, nous avons ajouté 3 méthodes explicites :

```python
    def placer_piece(self, piece, variante_index, position):
    def peut_placer(self, variante, position):
    def retirer_piece(self, piece, variante_index, position):
```
Ces méthodes permettent respectivement de :

- Placer une pièce sur le plateau,
- Vérifier si une pièce peut être placée à une position donnée,
- Retirer une pièce précédemment placée.


Afin de représenter les pièces, nous devons avoir le **nom** de la pièce pour la couleur, ainsi que sa **forme de base** représentée par une matrice.

```python
class Piece:
    def __init__(self, nom, forme_base):
        self.nom = nom
        self.forme_base = np.array(forme_base)
        self.variantes = self.generer_variantes()
```

Pour que l'algorithme puisse utiliser les variantes, nous avons implémenté une méthode qui vient retourner les **8 variantes** possibles.

```python
    def generer_variantes(self):
        variantes = []
        for i in range(4):  # (0°, 90°, 180°, 270°)
            rotation = np.rot90(self.forme_base, i)
            variantes.append(rotation)
            # symétrie horizontale
            symetrie = np.fliplr(rotation)
            variantes.append(symetrie)

        # sécurité pour retirer les doublons
        variantes_uniques = []
        for var in variantes:
            if not any(np.array_equal(var, existante) for existante in variantes_uniques):
                variantes_uniques.append(var)

        return variantes_uniques
```

### Placer les pieces sur l'interface

Désormais,  l'utilisateur doit pouvoir placer les pièces souhaitées pour son niveau. 
L'explication complète de l'interface sera faite dans une autre partie. Ici nous nous contenterons de seulement expliquer les parties essentielles pour le placement des pièces.

*explications des méthodes de la classe interface liées au placement*

## III/ L'algorithme de résolution

### Les recherches techniques

Comme expliqué dans l'introduction, le choix d'un algorithme de type **backtracing** nous semblait pertinent. Mais c'était la seule notions que nous connaissions. Nous avons ainsi commencé à faire des recherches plus techniques afin de mieux comprendre les concepts mathématiques et informatiques associés au projet.

#### Polyominos
En premier lieu, les pièces du jeu IQ Puzzle Pro sont mathématiquement appelés des "Polyominos". C'est une forme crée par des carrés connectés où chaque carré est adjacent à au moins un autre
[Source](https://fr.wikipedia.org/wiki/Polyomino)  

![screen nos polyominos]()
*Figure 3 : Les polyominos du jeu IQ Puzzler Pro*  

#### Problème de couverture exacte
Ensuite, notre projet est à un **problème de couverture exacte**. Ce type de problème consiste à couvrir intégralement un ensemble donné (le tableau du jeu) à l’aide de sous-ensembles spécifiques (les polyominos), sans qu’aucun ne se chevauche. 
Ce problème est un problème **NP-complet**, c'est à dire qu’il est difficile à résoudre de manière optimale en raison de sa complexité temporelle. Trouver une solution rapide pour des instances de grande taille devient rapidement impraticable.

En effet, on pourrait simplifier la complexité temporelle de notre problème tel que :
**\(O(b^d)\)**
où :
**\(b\)** est le facteur de branchement, c'est-à-dire le nombre moyen de choix possibles à chaque étape (ici, les pièces à placer avec leurs variantes).
et
**\(d\)** est la profondeur maximale de l’arbre de recherche (ici, le nombre de pièces à placer).

[Source](https://fr.wikipedia.org/wiki/Probl%C3%A8me_de_la_couverture_exacte)

![screen nos polyominos solvés]()
*Figure 4 : Exemple de couverture des polyominos*  

#### Point de départ : Algorithme X de Donald Knuth



#### c) explications de l'algo 
<i>(partie théorie soulignée de code)</i>

#### d) ajout de l'"exploration de zones vides"

#### e) ajout d'heuristiques

- Plusieurs heurestiques se présentent à nous, par rapport à la taille des pièces, leur compacité, si elles possèdes 'trous' par exemple une pièce en U : ':.:' où l'on peut placer une pièce que le U entourera.

|Heuristique|Priorité|
|:--|:---|
|ascender            |Petites pièces.|
|descender           |Grandes pièces.|
|compactness	     |Pièces compactes.|
|compactness_inverse |Pièces non compactes (grandes disparités largeur/hauteur)|
|perimeter	         |Petits périmètres.|
|perimeter_inverse   |Grands périmètres.|
|holes	             |Pièces avec peu de trous internes.|
|holes_inverse       |Pièces avec plus de trous internes.|



#### f) ajout multi-threading pour résolution boostée comme le cervô de Traïan



### IV/Interface

L'interface est une interface TKinter Basique, une grille (plateau) affichée dynamiquement et dont chaque cases possède des fonctions, des boutons appelant des fonctions et une TextBox pour afficher les résultats de l'algorithme dont le temps d'éxécution.

#### a) Classes indépendantes explications

#### b) bridge vers interface

#### c) interface

### V/ Benchmarks pour flex nos stats

### VI/Pour aller plus loin

Pour voir si l'algorithme fonctionnait même avec d'autres pièces et d'autres tailles de plateau, on a premièrement découpé manuellement un plateau `6x12` pour faire 14 pièces de formes différentes. Une fois cela fait on a utilisé l'éditeur de pièces <u>editor.py</u>. Et après avoir ajouté les pièces dans le tableau `pieces_definitions` le programme marchait déjà

![quadrillage 6x12](https://hackmd.io/_uploads/rJ1t7DNNkl.png)

#### 1) Grilles et Pièces non conventionnelles

**Test avec algo polyomnio et taille 400x5000 ?**

#### a) contexte explication
<i>test avec grille différentes et pièces différentes</i>

#### b) challenge de grille customizable + algo découpe pièces aléaoires

#### c) on est des GOATS et on peut tout résoudre

#### d) Drop the Mike.

### VII/Projet Annexes

#### a) Tests Réseau neuronal

L'un des objectifs abandonnés était d'avoir un réseau neuronnal qui pourrait jouer tout seul, le principe était de lui donner une pièce à placer (ou plutôt une variante) ainsi que le plateau `5x11` et d'attendre en sortie le tableau avec la pièce placée.
Cette ambition vaine du fait de la <i>complexité</i> du projet et de l'entraînement nécessaire pour que le réseau neuronal puisse placer les pièces aux bons endroits, sans qu'il n'y ait de modification du plateau initial ni de faux positifs : 2 pièces superposées

Plusieurs logiciels étaient disponibles mais nécessitaient une license, ou n'était disponible que trop peu de temps (essai gratuit).

Le problème avec les réseaux neuronnaux est qu'il est assez difficile de construire le réseau de la bonne manière, de sorte à pouvoir lui transmettre des données et une couche finale qui donne un résultat exploitable par un intermédiaire (si l'on voulait exploiter le réseau en temps réel une fois entraîné).
Vient aussi le problème de l'entraînement, il aurait fallu beaucoup de données sûres, et un temps d'entraînement assez faible pour pouvoir tester ses performances et modifier le réseau en temps restraint. Ce projet a été abandonné dans les quelques semaines après le début du projet, et nous ne l'avons pas abordé à nouveau depuis.

#### b) Portabilité CUDA

`Cuda` est un langage de programmation lancé en 2007 par `NVIDIA` permettant de faire des calculs sur sa carte graphique.

L'objectif était de porter l'algorithme `Python` en un algorithme `C/C++` `CUDA`.
Effectivement, les programmes qui n'utilisent pas d'interfaces/logiciels intermédiaires (ex: Unity, Blender, OpenGL etc) ne fonctionnent que sur le `CPU`, ce qui convient à quasiment toutes les utilisations basiques.

Mais ici il a aussi été question d'améliorer les performances jusqu'à diminuer le temps de calcul par 10 (exemple avec l'UV PC40, qui nous fait programmer en CUDA et nous fait comparer les vitesses de calculs de multiplication de matrices notamment).


Pour résoudre ce problème, il existe une version `Python` de CUDA
Nonobstant le potentiel remplacement de la carte graphique cramée à cause du projet, et de la potentielle taille de la grille non plus en `5x11`, mais bien en `55x121` (eh oui faut bien s'amuser) et des pièces qui ne seraient plus contraintes dans des matrices `4x4` mais pourrait adopter des dimensions moins conventionnelles (ex: `42x69`).