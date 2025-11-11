# 🧱 Jeu inspiré de "Geometry Dash" — Projet Pygame NSI

Un jeu inspiré de **Geometry Dash**, codé en Python avec **Pygame**.  
Le joueur contrôle un cube qui saute pour éviter les pics dans un monde qui défile automatiquement.

---

## 🎮 Présentation du projet

l'Organisation du projet :
- `main.py` → boucle principale du jeu
- `level.py` → gère le niveau complet (fond, plateformes, pics, joueur)
- `player.py` → logique et physique du joueur
- `objects.py` → définition des objets du décor
- `levels/level1.json` → carte du niveau sous forme ASCII
- `assets/` → images du cube, du fond, des blocs et des pics

---

## 🧩 Structure du code

### `main.py`
Lance le jeu :
- crée la fenêtre Pygame (`1000x600`),
- charge un niveau (`Level("levels/level1.json")`),
- gère la boucle du jeu (événements, update, affichage).

> Quand on appuie sur **Espace**, le joueur saute.

---

### `level.py`
Contient la classe `Level` :
- lit le fichier JSON du niveau,
- crée les **plateformes** et **pics** selon les caractères :
  - `=` → sol
  - `P` → plateforme flottante
  - `S` → pic
- fait défiler les objets vers la gauche (`scroll_speed`),
- gère les collisions et le **reset** du niveau si le joueur touche un pic.

Le fond (`background.png`) est **étiré automatiquement** pour toujours remplir la fenêtre.

---

### `player.py`
Classe `Player` :
- applique la **gravité** et la **physique du saut**,
- détecte les collisions avec les plateformes pour rester debout,
- empêche de sauter en plein vol.

> Le joueur est représenté par un cube qui saute et tombe sous l’effet de la gravité.

---

### `objects.py`
Deux classes simples :
- `Platform` → un bloc solide sur lequel le joueur peut marcher,
- `Spike` → un pic qui réinitialise le niveau en cas de collision.

---

### `level1.json`
Fichier pour charger le niveau avec des caractères ( la manière la plus optimisée et surtout la plus intuitive, l'idée à été suggeré par IA, on le fera peut être avec un fichier **CSV** dans le futur) :

```json
{
  "tile_size": 75,
  "layout": [
    "                                            ",
    "                                            ",
    "                                            ",
    "                                            ",
    "           S  S                             ",
    "          PPPPP                             ",
    "       PSS                   S           SSS",
    "============================================"
  ]
}