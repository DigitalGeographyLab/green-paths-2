DEV README
==========

There are many thing that could have been made better in this project. Here are some of them:

- not using poetry and conda together (should probably use only conda)
- many of the codes are not properly testd
- many of the codes are also written quite fast and not in a optimal matter (sorry possible further developers)
- the documentation could be made more comprehensive
- The API/GUI was not (fully) designed from the beginning, where the main aim was to create a scientific/mass calculation tool.
- the API is swiftly written "on top" of the "scientific/mass calculation" implementation. So it is not at all optimal and has many flaws...
- the sqlite3 is defenitely not designed for this kind of use (multiple users) and can cause significant problems with db locks etc...