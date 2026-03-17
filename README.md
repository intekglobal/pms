# pms

## Get started

### Requirements

Install the latest official version of `Python` ([you can download it from here](https://www.python.org/downloads/)),
or at least make sure you have `Python 3` installed. That should be sufficient to
contribute to the project, but it is recommended to keep your `Python` installation
up to date.

### Virtual environment

It is recommended to work on a virtual environment in order to isolate your packages;
this is a helpful guide to get you started:
[Virtual Environments — FastAPI](https://fastapi.tiangolo.com/virtual-environments)

### Install packages

Once you have a virtual environment created and activated, install the required packages:

```bash
python3 -m pip install -r requirements.txt
```

It is also recommended to upgrade your installed version of `pip` before installing
your packages:

```bash
python3 -m pip install --upgrade pip
```

### Run the project

To start the application and validate everything was properly configured execute the following command:

```bash
python3 -m fastapi dev main.py
```

This will start a development server in your localhost listening to port 8000.

If, for whatever reason, this is not useful for you, you can specify which port to listen to in the following way:

```bash
python3 -m fastapi dev main.py --port 9000
```
