""" TODO """

# tää ois main mis handlattais costien laskut
# mieti viel pitäiskö tääl vai network olla dictit jne, nyt latettu networkiin


class CustomCostCalculator:
    # TODO: here or in network?
    custom_cost_dictionaries: list[dict]

    # todo: pitää populatee toi custom cost dictionaries lista dicteil, pitää myös laittaa nimet ja sensivitityt oikein ehkä jotenkin list zip?
    def __init__(self):
        pass

    def get_custom_cost_dictionary(self, gdf_edges):
        pass

    def calculate_custom_costs_per_edge(self, gdf_edges):
        pass

    # some random notes / ideas
    # TODO: tee joku mis katotaan tää mitä niill tehdään yamlista

    # def apply_formula(gdf, formula):
    #     # Safely evaluate the formula on the GeoDataFrame
    #     gdf['normalized_value'] = gdf.eval(formula)
    #     return gdf

    # formula: "(db_lo + db_hi) / 2"  # Mean of db_lo and db_hi
