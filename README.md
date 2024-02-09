# Installation and Setup Guide for the Flask Project

This document provides detailed instructions on how to download, install, and run the Flask project hosted on GitHub. Follow these steps to set up the project environment and start the application.

## Prerequisites

Before proceeding with the installation, ensure you have the following installed on your system:

- **Python**: The project requires Python. It's recommended to use Python 3.6 or newer. You can download Python from [the official website](https://www.python.org/downloads/).

- **pip**: The Python package installer, which should come installed with Python versions 3.4 and above.

- **virtualenv**: Recommended for creating isolated Python environments. Install it via pip if you haven't already:

  ```
  pip install virtualenv
  ```

## Step 1: Download the Project

First, clone the repository from GitHub to your local machine. Open a terminal or command prompt and run the following command:

```
git clone https://github.com/burnsie000/crm.git
cd crm
```

## Step 2: Create a Virtual Environment

After cloning the project, navigate into the project directory and create a virtual environment. This environment is where you'll install the project's dependencies.

```
virtualenv venv
```

## Step 3: Activate the Virtual Environment

Activate the virtual environment to isolate your project's dependencies. The activation command differs depending on your operating system.

- On Windows:

  ```
  venv\Scripts\activate
  ```

- On macOS and Linux:

  ```
  source venv/bin/activate
  ```

## Step 4: Install Dependencies

With the virtual environment activated, install the project dependencies using pip:

```
pip install -r requirements.txt
```

This command reads the `requirements.txt` file in your project directory (assuming one exists) and installs all the listed packages.

## Step 5: Run the Flask Application

Finally, start the Flask application. Ensure you are still in the project directory and the virtual environment is activated.

```
export FLASK_APP=yourapplication.py
export FLASK_ENV=development
flask run
```

Replace `yourapplication.py` with the name of your main Python file if it's different.

The `FLASK_ENV=development` setting enables debug mode, which helps during development by providing detailed error messages and enabling live reloading.

## Conclusion

Your Flask application should now be running locally on your machine. You can access it by navigating to `http://127.0.0.1:5000/` in your web browser. For further customization and development, refer to the Flask documentation and the project's README file.
