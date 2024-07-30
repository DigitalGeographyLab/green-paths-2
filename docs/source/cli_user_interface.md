# CLI USER INTERFACE

Green Paths 2 is operated via CLI (terminal/cmd). User can run modules separately or all together. The arguments are run with "invoke" and parameter -a (for argument) . 
Personally I prefer to handle Green Paths 2.0 user configuration and cli user interface from VSCode (Visualstudio Code), as everything is in the same place.

**Running arguments:**
```
inv gp2 -a <COMMAND>
```
**example**
```
inv gp2 -a "all"
```
```{attention}
Replace the **<COMMAND>** with the actual command.
```

**Using arguements for command. Command and argument need to be wrapped in quation marks:**
```
inv gp2 -a "<COMMAND> <ARGUMENT>"
```
**example**
```
inv gp2 -a "all -uc"
```
```{attention}
Replace the **<ARGUMENT>** with the actual argument, and wrap command and argument to quation marks.
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


```{tip}
The preprocessing should most likely run separately only once. Then the routing and analysing modules can be run by using command: inv gp2 -a "all -uc"!
```

**Supported arguments for commands**

The arguments commands support. Use either short or long argument flag, not both.

**all**
- **-uc, --use_exposure_cache**
  - If flag is given, skip preprocessing pipeline and use cached exposure store data if found from db. If this flag is used, and no data found from db, will force preprocessing pipeline.

**segment_osm_network**
- **-fp, --filepath**
  - Filepath to the OSM network PBF targeted

- **-n, --name**
  - Name for the new segmented file without file extension.

**describe**
- **-sf, --save_to_file**
  - Boolean flag. If given, saves the result to file in cache dir.

**clear_db_cache**
- **-t, --table_names**
  - Specify one or more table names. To clear all tables, call without -t flag. Example: -t travel_times. Tables to clear are: output_results, routing_results, segment_store and travel_times


