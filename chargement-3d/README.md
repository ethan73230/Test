# Plan de chargement 3D

Outil web autonome (aucun serveur requis) qui génère un plan de chargement 3D
optimisé pour un camion, à partir d'une liste de palettes.

## Utilisation

Ouvrez `index.html` dans un navigateur (double-clic ou `python3 -m http.server`
depuis ce dossier), puis :

1. Déposez un fichier Excel (`.xlsx`, `.xlsm`, `.xls`, `.csv`) ou Ruby (`.rb`),
   ou saisissez les palettes manuellement dans le tableau.
2. Choisissez la longueur du camion (13,60 m, 10 m, 8 m, ou une valeur
   personnalisée), ainsi que la largeur/hauteur intérieures si besoin.
3. Cliquez sur **Générer le plan**.
4. Faites pivoter/zoomer la vue 3D à la souris. Chaque palette affiche sa
   référence.
5. **Télécharger l'image** exporte un PNG de la vue actuelle. **Imprimer**
   ouvre une version imprimable avec l'image et le tableau des positions.

## Format du fichier Excel

La première ligne doit contenir des en-têtes. Les intitulés suivants (accents
et casse ignorés) sont reconnus automatiquement :

| Champ      | En-têtes acceptés                                            |
|------------|---------------------------------------------------------------|
| Référence  | ref, référence, reference, nom, name, sku, désignation, code  |
| Longueur   | longueur, length, l                                            |
| Largeur    | largeur, width                                                  |
| Hauteur    | hauteur, height, h                                              |
| Quantité   | qte, qté, quantite, quantité, qty, quantity, nombre, nb        |

Les dimensions sont supposées en **centimètres**. Ajoutez `(m)` ou `(mm)` dans
l'intitulé de la colonne pour indiquer une autre unité (ex : `Longueur (m)`).

## Fichiers Ruby (SketchUp)

Un script Ruby est du code exécutable arbitraire : cet outil ne l'exécute pas
et ne peut pas interpréter n'importe quelle logique. Il applique une
extraction heuristique qui reconnaît uniquement des blocs de type :

```ruby
{ name: "P1", length: 120, width: 80, height: 100, qty: 4 }
```

(clés `name`/`ref`, `length`/`longueur`, `width`/`largeur`, `height`/`hauteur`,
`qty`/`quantite`, en notation `clé: valeur` ou `clé => valeur`). Si votre
script SketchUp est structuré différemment, l'extraction peut échouer ou être
incomplète : le tableau des palettes reste toujours modifiable manuellement
pour corriger ou compléter les données avant de générer le plan.

## Algorithme de chargement

L'algorithme est un algorithme glouton ("shelf packing") : les palettes de
même empreinte (longueur x largeur) sont d'abord empilées verticalement selon
la hauteur disponible du camion, puis les colonnes obtenues sont rangées en
lignes le long de la longueur du camion, en remplissant la largeur disponible
avant de passer à la ligne suivante. Ce n'est pas un optimiseur exact (le
problème de bin-packing 3D est NP-difficile), mais il donne un plan dense et
lisible en temps réel. Les palettes qui ne peuvent pas être placées (camion
trop court/étroit) sont signalées dans un message d'avertissement.

## Dépendances

Toutes les bibliothèques sont chargées via CDN, aucune installation n'est
nécessaire :
- [Three.js](https://threejs.org/) (rendu 3D + `OrbitControls`)
- [SheetJS (xlsx)](https://sheetjs.com/) (lecture des fichiers Excel/CSV)
