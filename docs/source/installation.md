# INSTALLATION

```{note}
See the OS specific instructions for the installation.
```

## Windows

Prerequisites:
- Java (openjdk 22.0.1 or higher)
    - Note: For University of Helsinki users, install Amazon Corretto from the SOftware Center 
- Setting JAVA_HOME environmental variable (if not set during installation)
- Miniconda or Anaconda
- Microsoft Visual Build Tools C++ 14.0 or greater

Useful links:

[Install JavaJDK](https://www.oracle.com/java/technologies/javase/jdk22-archive-downloads.html)

[Install miniconda/anaconda](https://docs.conda.io/en/latest/miniconda.html) if not installed.
The installation has python included.

```{hint}
If problems with conda not found occur, add Conda manually to the PATH or use the conda prompt.

```

[Install Microsoft Visual Build Tools C++ 14.0 or greater](https://visualstudio.microsoft.com/visual-cpp-build-tools/) if running older version.
From Visual Studio Installer select the tab "Individual components" and from there select at least:
- MSVC v143 - VS 2022 C++ x64/x86 build tools (latest)
- Windows 10 SDK (10.0.19041.0) 
- C++ CMake tools for Windows
Note: Tested on 17th October 2025


After installing the prerequisites, install Green Paths 2 to conda environment:
- Navigate to the Green Paths 2 root folder
- (optional) If active conda env, deactivete by running:
        conda deactivate
- Run the following command in the terminal:
        install_green_paths_2.bat
- After successfull installation, activate the conda environment by running:
        conda activate green_paths_2
- Now you can start using Green Paths 2 by running the CLI commands in the terminal.

```{hint}
Remember to activate the conda environment after installation!
```

<hr>

## Mac / Linux

Prerequisites:
- Miniconda or Anaconda

[Install miniconda/anaconda](https://docs.conda.io/en/latest/miniconda.html) if not installed.
The installation has python included.

After installing the prerequisites, install Green Paths 2 to conda environment:
- Navigate to the Green Paths 2 root folder
- (optional) If active conda env, deactivete by running:
        conda deactivate
- Run the following command in the terminal:
        ./install_green_paths_2.sh
- After successfull installation, activate the conda environment by running:
        conda activate green_paths_2
- Now you can start using Green Paths 2 by running the CLI commands in the terminal.

```{hint}
Remember to activate the conda environment after installation!
```

