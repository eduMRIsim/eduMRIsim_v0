# eduMRIsim

eduMRIsim is an educational MRI simulator software application. It is currently being devoloped as part of a design PhD project (start date February 2023) by Stephanie Gonzalez at Eindhoven Technical University under the supervision of Marcel Breeuwer and Alexander Raaijmakers. 

# Installation

Follow these instructions to run main.py locally. 

## Prerequisites
### Python 3.11 or higher installed
 Make sure you have Python installed on your system. You can download and install Python from the [official Python website](https://www.python.org/downloads/). 

To check if Python is installed on your system, you can use the command line or terminal. Here's how you can do it on different operating systems:

#### Windows
   - Type the following command:
     ```(cmd)
     python --version
     ```
   - Press `Enter`.
   - If Python is installed, it will display the version number. If it's not installed, you'll see an error message.


#### macOS and Linux
   - Open Terminal.
   - Type the following command:
     ```
     python --version
     ```
   - Press `Enter`.
   - If Python is installed, it will display the version number.



### Pip package manager installed
 Pip usually comes pre-installed with Python. You can verify if Pip is installed using the command line or terminal. If it is not installed, you can download it from [here](https://pypi.org/project/pip/). 

 #### Windows
   - Open Command Prompt.
   - Type the following command:
     ```(cmd)
     pip --version
     ```
   - Press `Enter`.
   - If pip is installed, it will display the version number. If it's not installed, you'll see an error message.



#### macOS and Linux
   - Open Terminal.
   - Type the following command:
     ```
     pip --version
     ```
   - Press `Enter`.
   - If pip is installed, it will display the version number.



## Step 1: Clone or download this repository to your local machine. 

### Clone
You can do this by copying the repository's URL and using git clone in your terminal/command prompt to clone the repository. 

#### Windows
    - Open Command Prompt 
    - Type the following command:
    ```
        git clone https://github.com/eduMRIsim/eduMRIsim_v0.git
    ```


## Step 2: Navigate to the repository directory

## Step 3: Create and activate a virtual environment (optional but recommended):
python -m venv myvenv 
source myvenv/bin/activate 

## Step 4: Install dependencies:
pip install -r requirements.txt 

## Step 5: Run "main.py"
python main.py 

# Troubleshooting

## Python isn't added to your system's PATH environment variable 
This is required for you to be able to run Python commands from any directory on your system. Look [here](https://realpython.com/add-python-to-path/) for further instructions.