# eduMRIsim

eduMRIsim is an educational MRI simulator software application. It is currently being devoloped as part of a design PhD project (start date February 2023) by Stephanie Gonzalez at Eindhoven Technical University under the supervision of Marcel Breeuwer and Alexander Raaijmakers. 

# Installation

Follow these instructions to run main.py locally. 

## Prerequisites
### Python 3.11 or higher installed*
*Earlier versions of Python may also be sufficient but this has not yet been tested. 

Make sure you have Python installed on your system. You can download and install Python from the [official Python website](https://www.python.org/downloads/). 

To check if Python is installed on your system, you can use the command line or terminal. Here's how you can do it on different operating systems:

#### Windows
   - Open Command Prompt (Windows) or Terminal (macOS/Linux).
   - Type the following command:
     ```
     python --version
     ```
   - Press `Enter`.
   - If Python is installed, it will display the version number. If it's not installed, you'll see an error message.




### Pip package manager installed
 Pip usually comes pre-installed with Python. You can verify if Pip is installed using the command line or terminal. If it is not installed, you can download it from [here](https://pypi.org/project/pip/). 

   - Open Command Prompt (Windows) or Terminal (macOS/Linux).
   - Type the following command:
     ```
     pip --version
     ```
   - Press `Enter`.
   - If pip is installed, it will display the version number. If it's not installed, you'll see an error message.

## Step 1: Clone or download this repository to your local machine. 

### Clone (requires Git)
You can do this by copying the repository's URL and using git clone in your terminal/command prompt to clone the repository. 
- Open Command Prompt (Windows) or Terminal (macOS/Linux).
- Change the current working directory to the location where you want the cloned directory using the `cd` (change directory) command
``` 
    cd path/to/location
```
- Type the following command:
```
    git clone https://github.com/eduMRIsim/eduMRIsim_v0.git
```

### Download (without Git)
If you don't have Git installed, you can download the repository as a ZIP file:

- Go to the repository's GitHub page.
- Click the "Code" button and select "Download ZIP".
- Extract the downloaded ZIP file to a location on your computer.


## Step 2: Navigate to the repository directory

Once you have cloned or downloaded the repository, navigate into the eduMRIsim_v0 folder using the `cd` (change directory) command in your command prompt/terminal.
    ```
    cd eduMRIsim_v0
    ```

## Step 3: Create and activate a virtual environment (optional but recommended):
It's recommended to use a virtual environment to isolate your project's dependencies from other projects. This step is optional but highly recommended to avoid conflicts between different projects' dependencies.

### Windows
   - Run the following command to create a virtual environment named "myvenv":
     ```
     python -m venv myvenv
     ```

   - To activate the virtual environment, run:
     ```
     myvenv\Scripts\activate
     ```

### macOS and Linux
   - Run the following command to create a virtual environment named "myvenv":
     ```
     python3 -m venv myvenv
     ```
   - To activate the virtual environment, run:
     ```
     source myvenv/bin/activate
     ```

## Step 4: Install dependencies:
Before running main.py, you need to install the project dependencies listed in the requirements.txt file. This file contains a list of Python packages required for running the application.

The following command installs all the required packages:
```
    pip install -r requirements.txt
```

## Step 5: Run "main.py"
Now you're ready to run the main.py script. Make sure you are still in the repository directory where main.py is located and your virtual environment is activated (if you created one).

This command executes the `main.py` script which opens the application.
```
    python main.py
```


# Troubleshooting

## Python isn't added to your system's PATH environment variable 
This is required for you to be able to run Python commands from any directory on your system. Look [here](https://realpython.com/add-python-to-path/) for further instructions.

# Acknowledgements
The icons used in this project are from [Eva Icons](https://akveo.github.io/eva-icons/#/), a pack of beautifully crafted open-source icons. You can find more about them at [akveo.github.io/eva-icons](https://akveo.github.io/eva-icons/#/).

