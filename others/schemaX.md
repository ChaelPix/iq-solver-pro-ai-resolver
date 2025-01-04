### Algorithme X de Knuth : Backtracking optimisé

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. Construction matrice de contraintes</p>
        <table border="1">
            <tr><td bgcolor="#E0FFFF">• Une colonne par case à remplir (C1-CN)</td></tr>
            <tr><td bgcolor="#E0FFFF">• Une colonne par pièce (PA,PB,...)</td></tr>
            <tr><td>• Une ligne = un placement possible</td></tr>
            <tr><td>• 1 = utilise cette case/pièce, 0 = non</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>2. Processus de résolution</p>
        <table border="1">
            <tr><th>Étape</th><th>Action</th></tr>
            <tr bgcolor="#FFE4E1">
                <td>a. Choix colonne</td>
                <td>MRV : prend celle avec le moins de "1"</td>
            </tr>
            <tr bgcolor="#E0FFFF">
                <td>b. Réduction</td>
                <td>• Supprime colonnes couvertes<br/>• Retire lignes conflictuelles</td>
            </tr>
            <tr bgcolor="#90EE90">
                <td>c. Récursion</td>
                <td>Continue sur matrice réduite</td>
            </tr>
            <tr>
                <td>d. Backtrack</td>
                <td>Si échec → essaie ligne suivante</td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>3. Exemple simple</p>
        <table border="1">
            <tr><th>Initial</th><th>→</th><th>Après MRV</th><th>→</th><th>Réduite</th></tr>
            <tr>
                <td>
                    111000<br/>
                    011100<br/>
                    100110
                </td>
                <td>→</td>
                <td bgcolor="#FFE4E1">
                    111000<br/>
                    100110
                </td>
                <td>→</td>
                <td bgcolor="#E0FFFF">
                    110
                </td>
            </tr>
        </table>
    </div>
</div>

*Avantages vs backtracking classique :*
1. MRV réduit l'arbre de recherche
2. Suppression lignes/colonnes évite tests inutiles
3. Matrice encode toutes les contraintes








### État complet de l'algorithme X - Exemple avec grille 2×2

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. État initial</p>
        <table border="1">
            <tr>
                <th>Plateau</th>
                <th>Pièces disponibles</th>
            </tr>
            <tr>
                <td>
                    <table>
                        <tr><td>-1</td><td>-1</td></tr>
                        <tr><td>-1</td><td>-1</td></tr>
                    </table>
                </td>
                <td>
                    <table>
                        <tr>
                            <td>Pièce A:<br/>
                                █ █<br/>
                                Taille: 2</td>
                        </tr>
                        <tr>
                            <td>Pièce B:<br/>
                                █<br/>
                                █<br/>
                                Taille: 2</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>2. Génération des variantes (Piece.generer_variantes)</p>
        <table border="1">
            <tr><th>Pièce A</th><th>Pièce B</th></tr>
            <tr>
                <td>
                    Variante 1: █ █<br/>
                    Variante 2: █<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;█
                </td>
                <td>
                    Variante 1: █<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;█<br/>
                    Variante 2: █ █
                </td>
            </tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. Matrice de contraintes finale</p>
        <table border="1">
            <tr><th>Placement</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr><td>A-V1(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>A-V2(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B-V1(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B-V2(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
        </table>
    </div>
    →
    <div>
        <p>4. Solution trouvée</p>
        <table border="1">
            <tr>
                <td>Plateau final</td>
                <td>Pièces placées</td>
            </tr>
            <tr>
                <td>
                    <table>
                        <tr><td bgcolor="red">A</td><td bgcolor="red">A</td></tr>
                        <tr><td bgcolor="blue">B</td><td bgcolor="blue">B</td></tr>
                    </table>
                </td>
                <td>
                    A: pos(0,0), var1<br/>
                    B: pos(1,0), var1
                </td>
            </tr>
        </table>
    </div>
</div>


### MRV (Minimum Remaining Values) - Sélection optimisée

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. Matrice initiale</p>
        <table border="1">
            <tr><th>Pos.</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>A(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
        </table>
    </div>
    →
    <div>
        <p>2. Comptage des 1 par colonne</p>
        <table border="1">
            <tr><th>Colonne</th><th>Nb de 1</th><th>Signification</th></tr>
            <tr bgcolor="#90EE90"><td>C1</td><td>2</td><td>2 pièces peuvent couvrir C1</td></tr>
            <tr><td>C2</td><td>2</td><td>2 pièces peuvent couvrir C2</td></tr>
            <tr bgcolor="#FFB6C1"><td>C3</td><td>2</td><td>2 pièces peuvent couvrir C3</td></tr>
            <tr bgcolor="#FFB6C1"><td>C4</td><td>0</td><td>Aucune pièce ne peut couvrir C4!</td></tr>
            <tr><td>PA</td><td>2</td><td>2 positions pour pièce A</td></tr>
            <tr><td>PB</td><td>1</td><td>1 position pour pièce B</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. Choix MRV</p>
        <table border="1">
            <tr><th>Stratégie</th><th>Impact</th></tr>
            <tr bgcolor="#90EE90">
                <td>Choisir colonne avec moins d'options</td>
                <td>Réduit l'arbre de recherche</td>
            </tr>
            <tr bgcolor="#FFE4E1">
                <td>Évite colonnes avec trop d'options</td>
                <td>Moins de backtracking</td>
            </tr>
        </table>
    </div>
</div>

*Principe MRV :*
- Compte les 1 dans chaque colonne
- Choisit la colonne avec le moins de 1 (mais > 0)
- Raisonnement : "Commencer par les contraintes les plus difficiles à satisfaire"

### Algorithme X de Knuth - Processus complet

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. État initial</p>
        <table border="1">
            <tr><th>Pos.</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr bgcolor="#FFE4E1"><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>A(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
        </table>
    </div>
    →
    <div>
        <p>2. MRV choisit C1 (2 "1")</p>
        <table border="1">
            <tr><th>Pos.</th><th bgcolor="#90EE90">C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr bgcolor="#FFE4E1"><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. Choix A(0,0)</p>
        <table border="1">
            <tr><th>Action</th><th>Effet</th></tr>
            <tr><td>Supprime C1,C2</td><td>Cases utilisées</td></tr>
            <tr><td>Supprime PA</td><td>Pièce utilisée</td></tr>
            <tr><td>Supprime lignes avec C1,C2</td><td>Conflits</td></tr>
        </table>
    </div>
    →
    <div>
        <p>4. Matrice réduite</p>
        <table border="1">
            <tr><th>Pos.</th><th>C3</th><th>C4</th><th>PB</th></tr>
            <tr bgcolor="#E0FFFF"><td>B(1,0)</td><td>1</td><td>1</td><td>1</td></tr>
        </table>
        <p>→ Continue récursivement</p>
    </div>
</div>

*Algorithme X :*
1. Si matrice vide → Solution trouvée
2. Sinon:
   - Choix colonne (MRV)
   - Pour chaque ligne avec 1 dans cette colonne:
     * Place la pièce (ajoute à solution)
     * Réduit la matrice
     * Appel récursif
     * Si échec → retire la pièce (backtrack)

### Construction et utilisation de la matrice - Processus complet

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. Pour chaque pièce, on liste TOUS les placements</p>
        <table border="1">
            <tr>
                <td>Pièce A</td>
                <td>
                    <table>
                        <tr><td>Position</td><td>Cases couvertes</td></tr>
                        <tr><td>(0,0)</td><td>C1,C2</td></tr>
                        <tr><td>(0,1)</td><td>C2,C3</td></tr>
                        <tr><td>(1,0)</td><td>C3,C4</td></tr>
                    </table>
                </td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>2. Matrice fusionnée (TRÈS grande!)</p>
        <table border="1">
            <tr><th>Pos.</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr bgcolor="#FFE4E1"><td>...</td><td colspan="6">Des centaines de lignes pour grande grille!</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. MRV : Minimum Remaining Values</p>
        <table border="1">
            <tr bgcolor="#90EE90">
                <td>Choisit la colonne avec le moins de "1"</td>
            </tr>
            <tr>
                <td>Exemple: si C3 n'a que 2 "1", on la choisit</td>
            </tr>
            <tr bgcolor="#FFB6C1">
                <td>⚠️ Plus la grille est grande, plus il y a de colonnes à compter!</td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>4. Problèmes sur grandes grilles</p>
        <table border="1">
            <tr><th>Taille</th><th>Impact</th></tr>
            <tr><td>5×11</td><td>~1000 lignes</td></tr>
            <tr><td>10×10</td><td>~10000 lignes</td></tr>
            <tr bgcolor="#FFB6C1"><td>16×16</td><td>~100000 lignes!</td></tr>
        </table>
    </div>
</div>

*Impact sur les performances :*
- Matrice énorme à stocker
- MRV doit scanner toute la matrice
- Beaucoup de lignes à supprimer/gérer


### Construction et utilisation d'une matrice de contraintes complète

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. Plateau 2×2 avec 2 pièces</p>
        <table border="1">
            <tr>
                <td>C1</td><td>C2</td>
                <td rowspan="3">Pièces:<br/>
                A:██<br/>
                B:█<br/>
                &nbsp;&nbsp;█</td>
            </tr>
            <tr>
                <td>C3</td><td>C4</td>
            </tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>2. Construction matrice finale</p>
        <table border="1">
            <tr bgcolor="#E6E6FA"><th>Placement</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>PA</th><th>PB</th></tr>
            <tr bgcolor="#FFE4E1"><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr bgcolor="#FFE4E1"><td>A(1,0)</td><td>0</td><td>0</td><td>1</td><td>1</td><td>1</td><td>0</td></tr>
            <tr bgcolor="#E0FFFF"><td>B┗(0,0)</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr bgcolor="#E0FFFF"><td>B┏(0,0)</td><td>1</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr bgcolor="#E0FFFF"><td>B┓(0,1)</td><td>0</td><td>1</td><td>0</td><td>1</td><td>0</td><td>1</td></tr>
        </table>
    </div>
    →
    <div>
        <p>3. Après choix de A(0,0)</p>
        <table border="1">
            <tr><th>Placement</th><th>C3</th><th>C4</th><th>PB</th></tr>
            <tr bgcolor="#E0FFFF"><td>B┓(0,1)</td><td>0</td><td>1</td><td>1</td></tr>
        </table>
        <p>Lignes supprimées car :<br/>
        - Utilise C1/C2 (déjà prises)<br/>
        - Ou utilise PA (pièce utilisée)</p>
    </div>
</div>

*Fonctionnement :*
1. `ConstraintMatrixBuilder` crée UNE SEULE matrice finale
2. Chaque ligne = un placement possible
3. Colonnes = cases (C1-C4) + pièces (PA,PB)
4. 1 dans une colonne = "utilise cette case/pièce"

**Construction complète de la matrice de contraintes**

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. Pièce A et tous ses placements possibles</p>
        <table border="1">
            <tr>
                <td>
                    Forme: ██<br/>
                    Positions possibles:<br/>
                    - (0,0): couvre [C1,C2]<br/>
                    - (0,1): couvre [C2,C3]<br/>
                    - (1,0): couvre [C4,C5]<br/>
                    - (1,1): couvre [C5,C6]
                </td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>2. Matrice complète pour pièce A</p>
        <table border="1">
            <tr><th>Place</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th><th>C6</th><th>PA</th></tr>
            <tr><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>A(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>A(1,0)</td><td>0</td><td>0</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td></tr>
            <tr><td>A(1,1)</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td><td>1</td><td>1</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. Pièce B et ses rotations</p>
        <table border="1">
            <tr>
                <td>
                    Forme: █<br/>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;█<br/>
                    Rotations:<br/>
                    - Normal ┗<br/>
                    - 90° ┏<br/>
                    - 180° ┓<br/>
                    - 270° ┛
                </td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>4. Matrice complète (toutes positions × rotations)</p>
        <table border="1">
            <tr><th>Place</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th><th>C6</th><th>PB</th></tr>
            <tr><td>B┗(0,0)</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td><td>1</td></tr>
            <tr><td>B┏(0,0)</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B┓(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td><td>1</td></tr>
            <tr><td>B┛(0,1)</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td><td>1</td></tr>
        </table>
    </div>
</div>

*Explication :*
- Chaque pièce génère plusieurs lignes (une par position × rotation possible)
- La matrice complète contient TOUTES les possibilités
- Pour notre exemple 2×3 avec 2 pièces, on a :
  * Pièce A : 4 positions possibles
  * Pièce B : 4 positions × 4 rotations = 16 lignes
  * Total : environ 20 lignes dans la matrice réelle

**Construction et utilisation de la matrice de contraintes**

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>1. État initial</p>
        <table>
            <tr><th>Plateau 2×3</th><th>Pièces</th></tr>
            <tr>
                <td>
                    <table>
                        <tr><td>-1</td><td>-1</td><td>-1</td></tr>
                        <tr><td>-1</td><td>-1</td><td>-1</td></tr>
                    </table>
                </td>
                <td>
                    A: ██<br/>
                    B: █<br/>
                    &nbsp;&nbsp;&nbsp;█
                </td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>2. Construction matrice</p>
        <table>
            <tr><th>Place</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th><th>C6</th><th>PA</th><th>PB</th></tr>
            <tr><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>A(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
        </table>
    </div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>3. Sélection MRV (C1)</p>
        <table>
            <tr><th>Col</th><th>Compte</th></tr>
            <tr bgcolor="#90EE90"><td>C1</td><td>2</td></tr>
            <tr><td>C2</td><td>3</td></tr>
            <tr><td>C6</td><td>4</td></tr>
        </table>
    </div>
    →
    <div>
        <p>4. Choix ligne A(0,0)</p>
        <table>
            <tr><th>Place</th><th bgcolor="#FFB6C1">C1</th><th>C2</th><th>C3</th><th>PA</th></tr>
            <tr bgcolor="#90EE90"><td>A(0,0)</td><td>1</td><td>1</td><td>0</td><td>1</td></tr>
            <tr><td>B(0,0)</td><td>1</td><td>0</td><td>0</td><td>0</td></tr>
        </table>
    </div>
    →
    <div>
        <p>5. Matrice réduite</p>
        <table>
            <tr><th>Place</th><th>C3</th><th>C4</th><th>PB</th></tr>
            <tr><td>B(1,0)</td><td>1</td><td>1</td><td>1</td></tr>
        </table>
    </div>
</div>

*Explication :*
1. On part du plateau vide et des pièces disponibles
2. Création matrice : une colonne par case (C1-C6) + une par pièce (PA,PB)
3. MRV choisit la colonne avec le moins d'options (ici C1)
4. On sélectionne une ligne couvrant C1 (ici A(0,0))
5. On supprime les colonnes couvertes et les lignes conflictuelles