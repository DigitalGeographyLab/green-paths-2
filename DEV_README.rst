DEV README
==========

TO RUN TESTS (in root):
        poetry run pytest
-----------------------
TO BUILD DOCS (in root):

- Always edit the files under folder "ipynb_docs_for_readthedocs"

! NOTICE: you might need to conda-forge install some of the dependencies, e.g. sphinx and sphinx_rtd_theme
! NOTICE: if adding a new "section" remember to add it to the "index.rst" file, so that it is included in the documentation
! NOTICE: in order for the docs to be updated to readthedocs, you need to push the changes to github, and in readthedocs webpage in green-paths-2 -project, you need to "rebuild" the project.

        ./build_readthedocs.sh

-----------------------

THE DISCLAIMER / FURTHER DEVELOPMENT SECTION:

There are many thing that could have been made better in this project. Here are some of them:

- not using poetry and conda together (should probably use only conda)
- many of the codes are not properly testd
- many of the codes are also written quite fast and not in a optimal matter (sorry possible further developers)
- the documentation could be made more comprehensive
- The API/GUI was not (fully) designed from the beginning, where the main aim was to create a scientific/mass calculation tool.
- the API is swiftly written "on top" of the "scientific/mass calculation" implementation. So it is not at all optimal and has many flaws...
- the sqlite3 is defenitely not designed for this kind of use (multiple users) and can cause significant problems with db locks etc...