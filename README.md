# GreenMove Logistics — POC Python (Dossier 4)

## 1. Contenu
- `geo_engine.py` : Bounding Box + Ray Casting pour déterminer si un point GPS est dans le polygone ZFE.
- `safety_engine.py` : lecture du CSV et détection d'un freinage lorsque `acc_y < -2.5 m/s²`.
- `main.py` : lance les deux modules.
- `data/` : jeux de données de l'énoncé.
- `output/daily_score.json` : fichier produit par le module Safety.

## 2. Lancer dans Anaconda
1. Décompresser le dossier `greenmove_poc`.
2. Ouvrir **Anaconda Navigator**, puis lancer **JupyterLab** ou **Spyder**.
3. Dans JupyterLab : ouvrir le dossier `greenmove_poc`, puis ouvrir un terminal (File > New > Terminal).
4. Dans le terminal, se placer dans le dossier du projet :
   `cd chemin/vers/greenmove_poc`
5. Exécuter :
   `python main.py`
6. Vérifier les messages `[ALERT ZFE]` et `[ALERT SAFETY]`.
7. Ouvrir `output/daily_score.json` pour vérifier le résultat du module Safety.

Aucune dépendance externe n'est nécessaire : le projet utilise la bibliothèque standard Python.

## 3. Résultats attendus avec les données fournies
- GPS 1 et 2 : OUT.
- GPS 3, 4 et 5 : IN selon le polygone et le test géométrique.
- Le CSV contient un freinage violent à `acc_y = -3.45 m/s²` (timestamp `1678880005`).
- Le JSON final doit contenir un événement `HARSH_BRAKING`.

## 4. Explication des algorithmes
### Module Geo
La Bounding Box calcule les latitudes et longitudes minimales et maximales du polygone. Si le point est en dehors de ce rectangle, il est forcément hors de la ZFE : le calcul s'arrête.
Si le point passe ce préfiltre, le Ray Casting trace conceptuellement un rayon horizontal. Le nombre d'intersections avec les côtés du polygone détermine si le point est dedans (nombre impair) ou dehors (nombre pair). Les points sur la bordure sont ici considérés comme dedans, par prudence.

### Module Safety
L'énoncé précise que l'axe Y est longitudinal et qu'un freinage correspond à une valeur négative. Le programme vérifie les valeurs numériques, ignore les lignes invalides et compare `acc_y` au seuil de `-2.5 m/s²`. Il ne fait pas de moyenne glissante, car elle risquerait de lisser et de faire disparaître le pic bref fourni dans le jeu de données. L'événement est enregistré dans `daily_score.json`.

## 5. Points de vigilance / limites du POC
- Les données GPS sont un petit jeu de test, pas une cartographie européenne réelle.
- Le POC utilise des coordonnées latitude/longitude directement. Pour un produit industriel, il faudrait traiter les projections, la précision GPS, les zones frontalières et les mises à jour cartographiques.
- Le CSV d'exemple contient un point par seconde, alors que l'annexe 1 annonce une tablette capable de produire 100 points par seconde. Le POC démontre la logique, mais il faudra tester les performances et la gestion d'un flux à 100 Hz.
- Le seuil `-2.5 m/s²` vient de l'annexe 3. Il ne faut pas le confondre avec `2.5 G` mentionné dans la consigne du module : les unités diffèrent fortement. Pour ce jeu de données, l'annexe 3 donne le seuil opérationnel à appliquer.
- Un vrai système télématique doit calibrer les axes du capteur selon le montage du véhicule, distinguer freinage, virage, choc et état de la route, et prévoir une validation métier avant tout usage assurantiel.

## 6. Tests rapides
Depuis le terminal, exécuter :
- `python geo_engine.py`
- `python safety_engine.py`
- `python main.py`

Pour tester une exception, faire une copie du CSV et remplacer une valeur numérique par `abc` : la ligne doit être ignorée sans arrêter le programme.
