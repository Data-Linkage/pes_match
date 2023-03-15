# ONS Record Linkage Pipeline Example Scripts
A set of Python scripts to demonstrate deterministic and probabilistic data linkage, using synthetic census and post-enumeration survey (PES) data.

For additional information consider reading:
* [Expectation maximisation algorithm](https://courses.cs.washington.edu/courses/cse590q/04au/papers/WinklerEM.pdf) developed by Fellegi-Sunter
* [ONS data linkage working paper](https://www.ons.gov.uk/methodology/methodologicalpublications/generalmethodology/onsworkingpaperseries/developingstandardtoolsfordatalinkagefebruary2021)

## Setup instructions

### Installing Python and an IDE
We recommend using the IDE Spyder which is available through the anaconda navigator. This can be installed [here](https://www.anaconda.com/products/distribution) and further instructions on installing Spyder can be found [here](https://docs.spyder-ide.org/current/installation.html).


### Using this code
Once Python is installed, download this repository and navigate to `/setup/` in the command prompt (using the command `cd` on a Windows OS machine).
In the `setup/` directory, executing the command `pip install -r requirements.txt` will install/update the required packages for this repository.
Files can then be executed in command line using `python file_name.py` or within Spyder using the inbuilt run function (or press F5). If an error similar to "lib is not found", set the working directory to the `pipeline/` repository.


## Directories and files of note

Descriptions of project directories and other significant files:
* `CROW/` - contains the code and config files for the [Clerical Resolution Online Widget](https://github.com/Data-Linkage/Clerical_Resolution_Online_Widget)
* `Data/` - the required mock data to operate the scripts at a basic level
* `lib/` - contains helper functions and configurable parameters
* `pipeline/` - scripts forming the example record linkage pipeline
* `setup/` - required packages and versions with instructions on terminal installation via `pip` 
* `training/` - code to demonstrate key data linkage operations including expectation maximisation
 


