# CLI USER INTERFACE

Green Paths 2 is operated via CLI (terminal/cmd). User can run modules separately or all together.

All of the arguments have to be run with prefix of:

```
inv gp2 -a <COMMAND>
```

```{attention}
Replace the **<COMMAND>** with the actual command and possible arguments.
```

**Supported commands**

Command line interface commands. Some of the commands need, and some accept arguments. These arguments can be e.g., a list of db table names for clear_db_cache , a file path for the OSM segmenter, or a use cache flag for all pipelines. See detailed descriptions from the software documentation.

| Command             | Explanation                                       |
|---------------------|---------------------------------------------------|
| `all`               | Run all pipelines.                                |
| `preprocessing`     | Run preprocessing pipeline separately.            |
| `routing`           | Run routing pipeline separately. Needs cache.     |
| `analysing`         | Run analysing pipeline separately. Needs cache.   |
| `segment_osm_network` | Segment an OSM PBF from a file path.            |
| `validate`          | Validate user configuration YAML file.            |
| `describe`          | Describe user data sources.                       |
| `clear_db_cache`    | Clear db (cache) tables by names.                 |


**Supported arguments for commands**

The arguments commands support. Use either short or long argument flag, not both.



**all**
- **-uc, --use_exposure_cache**
  - If flag is given, skip preprocessing pipeline and use cached exposure store data if found from db. If this flag is used, and no data found from db, will force preprocessing pipeline.
