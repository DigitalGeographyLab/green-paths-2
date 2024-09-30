# API readme / notes

The API/GUI was not (fully) designed from the beginning, where the main aim was to create a scientific/mass calculation tool.
Consider the API/online GUI very experimental without having much optimal code nor support for concurrent request etc.

Many choices are restricted to the fact that there was very limited time to make the API
so it had to be build "on top" of the existing "science / mass calculations" implementation hence many not optimal decisions

Note: if the segment_store db table is emptied and the large HMA OSM PBF network is used, the startup of the server
might take really long like 12-24h (?). So if getting errors in Frontend GUI, check that the Uvicorn has "startup completed" or something similar print in logs. Otherwise could be returning CORS error etc.

# memo / issues

-   the sqlite3 is defenitely not designed for this kind of use (multiple users) and can cause significant problems with db locks etc...
-   the configurations are quite repetetive with just minimal changes, this could be done lot better
-   the fact that currently the origin and destination csv are the same for all request could potentially give wrong routes if used simultaneously
    this should not be too critical as the user amounts should be minimal
-   the building network takes really long (e.g. the updating AQI every hour or so). This was not designed to be updated so frequently.
    Now it is happening in celery/redis (background process) so it should not block the "main theads"
-   no tests written for the API which is really bad, but no time for this.
-   the fact that all requests are using the same tables is bad, should probably not use the db in the first place
    this is just because there was no time to do another implementation without the db that the scientific version uses
