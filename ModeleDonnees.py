import json

# -----------------------------------------------------------------------------
# --- class ModeleDonnees
# -----------------------------------------------------------------------------

class ModeleDonnees:
    def __init__(self, chemin_produits):
        self.chemin_produits = chemin_produits
        self.produits = self.charger_produits()
        self.positions = []  # Liste des produits placés avec coordonnées
        self.positions_valides = [
            (4, 0), (15, 0), (16, 0), (17, 0), (18, 0), (19, 0), (20, 0), (21, 0),
            (3, 1), (4, 1), (5, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (23, 1), (24, 1), (25, 1), (26, 1), (27, 1), (28, 1), (29, 1), (30, 1), (31, 1), (32, 1), (33, 1), (34, 1), (23, 1), (24, 1), (25, 1), (26, 1), (27, 1), (28, 1),
            (2, 2), (3, 2), (4, 2), (5,2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (13, 2), (14, 2), (35, 2), (36, 2), (37, 2), (38, 2), (39, 2), (40, 2), (41, 2), (42, 2), (43, 2), (44, 2), (45, 2), (46, 2), (47, 2), (48, 2), (49, 2), (50, 2), (51, 2), (52, 2), (53, 2), (54, 2), (55, 2), (56, 2), (57, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (35, 3), (36, 3), (37, 3), (38, 3), (39, 3), (40, 3), (41, 3), (42, 3), (43, 3), (44, 3), (45, 3), (46, 3), (47, 3), (48, 3), (49, 3), (50, 3), (51, 3), (52, 3), (53, 3), (54, 3), (55, 3), (56, 3), (57, 3),
            (1, 4), (2, 4), (3, 4), 
            (1, 5), (2, 5), (8, 5), (9, 5), (10, 5), (12, 5), (13, 5), (14, 5), (16, 5), (17, 5), (18, 5), (20, 5), (21, 5), (22, 5), (24, 5), (25, 5), (26, 5), (28, 5), (29, 5), (30, 5), (32, 5), (33, 5), (34, 5), (35, 5), (36, 5), (37, 5), (39, 5), (41, 5), (42, 5), (43, 5), (48, 5), (49, 5), (50, 5), (51, 5), (52, 5), (53, 5), (54, 5), (55, 5), (56, 5), (57, 5), (60, 5),
        ]

    def charger_produits(self):
        with open(self.chemin_produits, 'r', encoding='utf-8') as f:
            return json.load(f)

    def ajouter_position(self, produit, x, y):
        self.positions.append({
            'produit': produit,
            'x': x,
            'y': y
        })

    def supprimer_position(self, produit):
        self.positions = [p for p in self.positions if p['produit'] != produit]

    def exporter_positions(self, chemin='produits_positions.json'):
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=4, ensure_ascii=False)

    def get_categories(self):
        return list(self.produits.keys())

    def get_produits_par_categorie(self, categorie):
        return self.produits.get(categorie, [])

    def get_produits_coordonne(self, x, y):
        return [p['produit'] for p in self.positions if p['x'] == x and p['y'] == y]

    def supprimer_produit_coordonne(self, produit, x, y):
        self.positions = [
            p for p in self.positions
            if not (p['produit'] == produit and p['x'] == x and p['y'] == y)
        ]

    def vider_case(self, x, y):
        self.positions = [p for p in self.positions if not (p['x'] == x and p['y'] == y)]