# Q&A Troubleshooting

```{note}
If no relevant info found, open a issue in GP2 github, or contact the developer(s)
```

Q: Error says that JAVA_HOME is not set
---
A: Set JAVA_HOME environmental variable to point to where Java is installed

***

Q: I'm getting error saying: sqlite3.OperationalError: no such table: segment_store
---    
A: Remember to run preprocessing before running routing or analysing!

A: If running all -command, always run once without -uc flag! 

***

Q: Getting error FileNotFoundError: [Errno 2] JVM DLL not found: ...
---
A: have you activated the conda env in console by: conda activate dgl_gp2

***

Q: Getting error of some user configuration parameter is invalid
---
A: double check the data type and the meaning of each user configuration value

***

Q: Getting error saying: Cannot convert value to Java int
---
A: The exposure value needs to be able to be converted to Java Integer. If a data is e.g. "27,7982291667" try rounding it smaller and using dot (".") as the decimal separator, not comma (",")!


