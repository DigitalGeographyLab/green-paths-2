""" roope todo """

# tää ois main mis handlattais costien laskut
# mieti viel pitäiskö tääl vai network olla dictit jne, nyt latettu networkiin


class CustomCostCalculator:
    # roope todo -> tääl vai networkis?
    custom_cost_dictionaries: list[dict]

    # todo: pitää populatee toi custom cost dictionaries lista dicteil, pitää myös laittaa nimet ja sensivitityt oikein ehkä jotenkin list zip?
    def __init__(self):
        pass

    def get_custom_cost_dictionary(self, gdf_edges):
        pass

    def calculate_custom_costs_per_edge(self, gdf_edges):
        pass
