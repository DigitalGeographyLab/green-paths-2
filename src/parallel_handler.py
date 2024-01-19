"""Used to run functions in parallel"""


# roope todo -> laita logiikkaa tänne, mis voi valita millä ajetaan parallelisointi
# pitäskö tää olla luokka?


# roope todo -> pitäskö olla filu missä ajetaan joko vaan perus funktio, tai sit käyttäen eri parallelisointeja?
# meneekö ihan liian hifistelyksi?

## PARALLEEEEEEL
# result_gdf = apply_parallel(
#     network_gdf, create_buffers_for_edges, num_processes=1, meters=20
# )
# LOG.info(len(result_gdf))

# DASK
# network_gdf_buffered = dask_operation_runner(
#     network_gdf,
#     lambda df: create_buffers_for_edges(network_gdf, meters=20),
# )
# LOG.info(len(network_gdf_buffered))
