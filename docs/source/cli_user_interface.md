# CLI USER INTERFACE

Green Paths 2 is operated via CLI (terminal/cmd). User can run modules separately or all together. The arguments are run with "invoke" and parameter -a (for argument) . 
Personally I prefer to handle Green Paths 2.0 user configuration and cli user interface from VSCode (Visualstudio Code), as everything is in the same place.

## Running arguments
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

<hr>

## Using command arguments. Command and argument need to be wrapped in quation marks
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

<hr>

## Using general arguments
These arguments are not targeting any command, so they come before the command, e.g. the config argument.
```
inv gp2 -a "<ARGUMENT><COMMAND>"
```
**example**
```
inv gp2 -a "-c custom/user_config/path.yaml all"
```
```{attention}
Only general arguments are added before the command!
```

## Supported commands

Command line interface commands. Some of the commands need, and some accept arguments. These arguments can be e.g., a list of db table names for clear_db , a file path for the OSM segmenter, or a use cache flag for all pipelines. See detailed descriptions down below.

| Command             | Explanation                                       |
|---------------------|---------------------------------------------------|
| `all`               | Run all pipelines.                                |
| `preprocessing`     | Run preprocessing pipeline separately.            |
| `routing`           | Run routing pipeline separately. Needs cache.     |
| `analysing`         | Run analysing pipeline separately. Needs cache.   |
| `segment_osm_network` | Segment an OSM PBF from a file path.            |
| `validate`          | Validate user configuration YAML file.            |
| `describe`          | Describe user data sources.                       |
| `clear_db`          | Clear db tables (by names).                         |


```{tip}
The preprocessing should most likely run separately only once. Then the routing and analysing modules can be run by using command: inv gp2 -a "all -uc"!
```

## General Arguments

```{tip}
Use either short or long argument flag, not both. e.g. either -uc or --use-cache!
```
- **-c, --config**
  *string*
  - Custom path to user configuration file. This can be used for all commands but: clear_db and segment_osm_network.
  - example: inv gp2 -a "-c /path/to/user_config.yaml all"

```{attention}
Only general arguments are added before the command!
```

<hr>

## Command Arguments


**all**

  - **-uc, --use_exposure_cache** 
    *boolean*
    - If flag is given, skip preprocessing pipeline and use cached exposure store data if found from db. If this flag is used, and no data found from db, will force preprocessing pipeline.
    - example: inv gp2 -a "all -uc"

<div class="separator_line"></div>

**segment_osm_network**

  - **-fp, --filepath**
    *string*
    - Filepath to the OSM network PBF targeted
    - example: inv gp2 -a "segment_osm_network -fp path/to/file.osm.pbf"

<div class="separator_line"></div>

  - **-n, --name**
    *string*
    - Name for the new segmented file without file extension.
    - example: inv gp2 -a "segment_osm_network -fp path/to/file.osm.pbf -n new_name_for_segmented_file"

<div class="separator_line"></div>

**describe**

  *boolean*
  - **-sf, --save_to_file**
    - If given, saves the result to file in cache dir.
    - example: inv gp2 -a "describe -sf"

<div class="separator_line"></div>

**clear_db**

  - **-t, --table_names**
    *string (list)*
    - Specify one or more table names. To clear all tables, call without -t flag. Example: -t travel_times. Tables to clear are: output_results, routing_results, segment_store and travel_times
    - example: inv gp2 -a "clear_db -t travel_times routing_results"



