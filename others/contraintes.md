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
        <p>3. Pièce B en L et ses rotations</p>
        <table border="1">
            <tr>
                <td>
                    Forme en L:<br/>
                    █<br/>
                        █ █<br/>
                    Rotations:<br/>
                    - Normal ┗ <br/>
                    - 90° ┏<br/>
                    - 180° ┓<br/>
                    - 270° ┛ <br/>
                </td>
            </tr>
        </table>
    </div>
    →
    <div>
        <p>4. Matrice complète pour pièce L</p>
        <table border="1">
            <tr><th>Place</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th><th>C6</th><th>PB</th></tr>
            <tr><td>B┗(0,0)</td><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td></tr>
            <tr><td>B┗(0,1)</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td><td>1</td></tr>
            <tr><td>B┏(0,1)</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B┛(0,1)</td><td>0</td><td>1</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td></tr>
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




<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
    <div>
        <p>4. Matrice complète (toutes positions × rotations)</p>
        <table border="1">
            <tr><th>Place</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th><th>C6</th><th>PB</th></tr>
            <tr><td>B┗(0,0)</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B┏(0,0)</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B┓(0,1)</td><td>0</td><td>1</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td></tr>
            <tr><td>B┛(0,1)</td><td>0</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>1</td></tr>
        </table>
    </div>
</div>