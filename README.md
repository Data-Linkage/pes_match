# PES MATCH

Python package and example pipeline for matching census and post-enumeration survey (PES) data.
For simplicity, only deterministic and clerical matching methods are provided.

For additional information consider reading:
* [ONS data linkage working paper](https://www.ons.gov.uk/methodology/methodologicalpublications/generalmethodology/onsworkingpaperseries/developingstandardtoolsfordatalinkagefebruary2021)
* [Census 2021 to Census Coverage Survey matching methods, England & Wales](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/methodologies/linkagemethodsforcensus2021inenglandandwales)

## Setup instructions

Once Python is installed, download this repository and execute the command `pip install -e .` or `make install` to install/update the package and its dependencies.

## Using this code

The aim of this repository is to provide a set of functions for cleaning and then matching census and PES data. The package gives matchers the tools to automatically match records
at the chosen level of geography and then resolve conflicts/difficult cases using the Clerical Resolution Online Widget (CROW). Associative matching can also be implemented to
assist in finding all possible matches between census and PES households. Once all methods have been applied at a single level of geography, matches can be combined and
residuals collected for the next stage of matching.

An example of a typical matching pipeline is provided in the `pipeline/` repository, however users may wish to apply matching methods in their own chosen order.
Files can be executed in the command line using `python file_name.py` or within an IDE using the inbuilt run function.

## Pipeline running order
* Step 1: Run scripts in `pipeline/processing/` to clean raw files
* Step 2: Update matchkeys in `pipeline/X_Stage_X/` before running the scripts in order. 2 stages are included but more can be created if needed
* Step 3 (Optional): Run clerical search (`pipeline/Clerical_Search/`) to find the remaining matches within chosen level of geography e.g., enumeration area (EA)

## When is CROW required?
CROW is required for clerical matching (to manually resolve non-unique matches) after running the following scripts:
* `pipeline/1_Stage_1/01_stage_1_person.py`
* `pipeline/2_Stage_2/01_stage_2_person.py`

## Directories and files of note

Descriptions of project directories and other significant files:
* `src/pes_match/` - the core package in the project.
    * `src/pes_match/cleaning.py` - functions to clean and prepare census / PES data for matching
    * `src/pes_match/cluster.py` - function to cluster together non-unique matches between census / PES data
    * `src/pes_match/crow.py` - functions to prepare datasets for CROW and read in outputs from CROW
    * `src/pes_match/matching.py` - functions to match census and PES data together
    * `src/pes_match/parameters.py` - parameters that can be updated before or during matching
* `pipeline/` - example pipeline that can be used as a starting point for matching census and PES data. Matchkeys can be updated within the scripts
* `CROW/` -  contains the code and config files for the [Clerical Resolution Online Widget](https://github.com/Data-Linkage/Clerical_Resolution_Online_Widget)
* `Data/` - contains mock data and stores cleaned data, clerical inputs/outputs, checkpoint files and final outputs
* `tests/` - tests for the code under `src/pes_match/`
* `docs/` - [package documentation](https://data-linkage.github.io/pes_match/) that is built and hosted as HTML by GitHub Actions based on the `main` branch code. See [documentation for sphinx for updating or building docs manually](https://www.sphinx-doc.org/en/master/)
  * `docs/CONTRIBUTING.md` - general guidance for contributing to the project
  * `docs/CODE_OF_CONDUCT.md` - code of conduct
* `.github/workflows` - configs for GitHub Actions
