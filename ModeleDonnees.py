import json

# -----------------------------------------------------------------------------
# --- class ModeleDonnees
# -----------------------------------------------------------------------------

class ModeleDonnees:
    def __init__(self, chemin_produits):
        self.chemin_produits = chemin_produits
        self.produits = self.charger_produits()
        self.positions = []  # Liste des produits placés avec coordonnées

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