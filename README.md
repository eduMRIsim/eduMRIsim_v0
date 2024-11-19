# Welcome to eduMRIsim!

eduMRIsim is an educational MRI simulator software application. It is currently being devoloped as part of a design PhD project (start date February 2023) by Stephanie Gonzalez at Eindhoven Technical University under the supervision of Marcel Breeuwer and Alexander Raaijmakers. 
![eduMRIsim_screenshot](https://github.com/user-attachments/assets/d10727a6-fc21-4a23-a16b-c7b984eef4d5)


# Table of Contents
   - [Installation](#installation)
   - [Troubleshooting](#troubleshooting)
   - [Getting started with eduMRIsim](#getting-started-how-to-run-an-examination)

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

# Getting started: how to run an examination

## Click on "New Examination"
Once application has started running, press the "New Examination" button to set-up an examination. 
![Screenshot 2024-07-16 151217](https://github.com/user-attachments/assets/5d521c7f-9b3c-434a-8264-a55affc751c3)

## Set-up examination
Set-up examination by selecting a model and entering an examination name. Then press "OK". 
![Screenshot 2024-07-16 151257](https://github.com/user-attachments/assets/272d9178-9425-48fe-858d-793e9d1de1a8)

## Click on "Add Scan Item"
Press "Add Scan Item" button to be shown the repository of scan items with predefined scan parameters. These are scan items that can be added to the examination's scanlist. 
![Screenshot 2024-07-16 151318](https://github.com/user-attachments/assets/79d2fafb-642c-4217-b509-ead9e1d1f42f)

## Add scan items to scanlist
Scan items can be added to the scanlist by dragging and dropping from the repository to the scanlist (white box above "Add Scan Item" button). 
![Screenshot 2024-07-16 151338](https://github.com/user-attachments/assets/504f2121-93df-4637-93b6-6c829b352a8a)

![Screenshot 2024-07-16 151355](https://github.com/user-attachments/assets/f7f4e296-9e99-4150-95ac-a75ae4d69c88)

## Edit scan parameters
Double-click any scan item in the scanlist to view and, if desired, edit scan parameters. Press "Save" after making any desired edits to the scan parameters. Press "Reset" to restore parameters to the scan item's original values. Press "Cancel" to discard edits. 
![Screenshot 2024-07-16 151403](https://github.com/user-attachments/assets/c423c550-0cfb-457c-8e4f-7e5ecd72f15b)

## Scan
Select any item from the scanlist you wish to scan (by double-clicking). If the item is in the "ready-to-scan" state indicated by the black checkmark icon, you can press "Scan". 
![Screenshot 2024-07-16 151416](https://github.com/user-attachments/assets/c191741d-aaea-4d55-9809-8a2dcf1e04c5)

The result of the simulated scan will appear in the lower right corner. Use your mouse scroll button to scroll through the slices. Hold down the mouse scroll button to adjust window width and level settings. 
![Screenshot 2024-07-16 151428](https://github.com/user-attachments/assets/bda92d18-fe51-4760-af47-50ae0b02931e)

## View images
Drag and drop any scan item in the "scan-complete" state (indicated by the circled checmark icon) to any of the three windows in the scan planning area to view. Here the result of different simulations can be viewed side-by-side. 
![Screenshot 2024-07-16 154105](https://github.com/user-attachments/assets/28c392a5-a08e-4aa3-873f-bf47b6e59d71)

## End examination
To stop the examination and start a new one, click the "Stop" button. 
