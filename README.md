[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3129/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# Veiligheidsrendement Dashboard #

This is the repository of the dashboard connecting to the VeiligheidsrendementTool. The dashboard is developed in Dash and Plotly.



# Installation of the dashboard #

The dashboard currently runs locally on your own machine. To install and use the dashboard, follow the steps below:

1. Clone the repository to your local machine in a directory of your choice.
    ```bash
    cd C:\repos
    git clone https://github.com/Deltares/VrtoolDashboard.git
    ```

2. Navigate to your 'VrtoolDashboard' directory and create a virtual environment (make sure you already have anaconda installed).
    ```bash
    cd C:\repos\VrtoolDashboard
    conda env create -f .config\environment.yml
    conda activate vrtool_dash
    poetry install
    ```
If the installation of all the packages is not successful and error messages are appearing, run ```poetry install``` again.
   
3. The dashboard is now installed and ready to use. To run the dashboard, run the following command:

   ```bash
   python -m src.index
   ```

The dashboard should pop up in your default browser. If not, navigate to http address displayed in the terminal.
Once the dashboard is already installed, only the third step is required to start the dashboard again (provided that the virtual environment is activated, if not rerun ```conda activate vrtool_dash```).





