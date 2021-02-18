[![preview](https://raw.githubusercontent.com/phillipdupuis/dtale-desktop-media/master/images/light_mode_screenshot.png)](https://github.com/phillipdupuis/dtale-desktop)

---
An interface for saving python scripts as permanent D-Tale launch points.

[![PyPI version](https://badge.fury.io/py/dtaledesktop.svg)](https://badge.fury.io/py/dtaledesktop)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---
### Getting started

#### Installation
```bash
$ pip install dtaledesktop
```

#### Running it from the command line:
```bash
$ dtaledesktop
```

#### Running it from a python script:
```
import dtale_desktop

dtale_desktop.run()
```

---
### Motivation

dtaledesktop simplifies the process of fetching data, cleaning/transforming it, and then performing exploratory data analysis. With dtaledesktop, that entire process is condensed into a single click.

It does this by providing a dashboard GUI, and any python code which returns a pandas DataFrame can be saved to the dashboard as a widget. Users can then execute that code and explore the DataFrame in [dtale](https://github.com/man-group/dtale) or [pandas-profiling](https://github.com/pandas-profiling/pandas-profiling) by simply clicking one of the widget buttons. The code associated with that widget can also be edited directly from the dashboard, and upon doing so the dashboard is updated in real-time.

Here's a simple example of using this workflow:
1. launch `dtaledesktop` from a terminal. The dashboard automatically opens up in your web browser.
2. click the 'Add Data Source' button, fill out the form like so, and click save:
![preview](https://raw.githubusercontent.com/phillipdupuis/dtale-desktop-media/master/images/walkthrough_step_1_add_source.png)
3. and bam! You now have a new 'Stocks' section on your dashboard. It will be there every time you launch dtaledesktop, and the python code can be edited directly from the dashboard:
![preview](https://raw.githubusercontent.com/phillipdupuis/dtale-desktop-media/master/images/walkthrough_step_2_view_section.png)

If at some point you decide you want to watch Apple too, all you need to do is click the "Settings" button and add "AAPL" to the list of stock symbols. It will immediately appear in the dashboard below TSLA.

---
### How it works

The front end is written with react, using a mixture of ant-design and styled-components.

The back end is written in python, and it actually consists of TWO apps which listen on separate ports. The main one is an asynchronous FastAPI application, and it responsible for communicating with the dashboard, interacting with the file system, and executing user-defined code for fetching/transforming data. It is able to do this by saving the submitted code as persistent files and then using importlib.util to build and then import the resulting modules. The second app is for running dtale instances, and it is a synchronous flask application.

---
### Developers/Contributing

First, you'll want to clone the repo and install the python dependencies:
```bash
$ git clone https://github.com/phillipdupuis/dtale-desktop.git
$ cd dtale-desktop
$ python setup.py develop
```

Then you'll need to install the javascript dependencies and build the react app:
```bash
$ cd dtale_desktop/frontend
$ npm install
$ npm run build
```

And now you should be able to launch it like so:
```bash
$ python dtale_desktop/app.py
```

If you want to modify the front-end, do the following:
1. Launch the python app in the normal way
2. Change the "proxy" setting in `frontend/package.json` to point at the host/port the python app is running on.
3. `npm start` to launch the react app. It will run on a different port, but will proxy unknown requests to the python app.

---
### Settings

#### Disabling features:
|Environment Variable|Description|
|:----------|:-----------|
|DTALEDESKTOP_DISABLE_ADD_DATA_SOURCES|"true" if the "Add Data Source" button should not be shown.|
|DTALEDESKTOP_DISABLE_EDIT_DATA_SOURCES|"true" if editing existing data sources should not be allowed.|
|DTALEDESKTOP_DISABLE_EDIT_LAYOUT|"true" if users should not be allowed to edit what sources are visible or what order they're in.|
|DTALEDESKTOP_DISABLE_PROFILE_REPORTS|"true" if the "Profile" option (which builds a pandas_profiling report) should not be shown. This is resource-intensive and currently a bit buggy.|
|DTALEDESKTOP_DISABLE_OPEN_BROWSER|"true" if browser should not open upon startup|
|DTALEDESKTOP_DISABLE_DTALE_CELL_EDITS|"true" if editing cells in dtale should be disabled.|

#### Routing requests:
|Environment Variable|Description|
|:----------|:-----------|
|DTALEDESKTOP_HOST|host it will run on|
|DTALEDESKTOP_PORT|port the main application will use|
|DTALEDESKTOP_DTALE_PORT|port the dtale application will use|
|DTALEDESKTOP_ROOT_URL|allows you to override how urls are built, which can be useful if you're running it as a service (ie not locally)|
|DTALEDESKTOP_DTALE_ROOT_URL|added in order to support running dtaledesktop in k8s - by using different domain names for the main app and the dtale app, the ingress controller can use that (domain name) to determine which port requests should be sent to.|
|DTALEDESKTOP_ENABLE_WEBSOCKET_CONNECTIONS|"true" if real-time updates should be pushed to clients via websocket connection. This is only useful/necessary if you are running it as a service and multiple users can access it simultaneously.|

#### Loaders/file storage:
|Environment Variable|Description|
|:----------|:-----------|
|DTALEDESKTOP_ROOT_DIR|the location where all persistent data (loaders, cached data, etc.) will be stored. By default this is ~/.dtaledesktop|
|DTALEDESKTOP_ADDITIONAL_LOADERS_DIRS|comma-separated list of directory paths that should be scanned for data sources upon startup|
|DTALEDESKTOP_EXCLUDE_DEFAULT_LOADERS|"true" if the default loaders should not be included in the list of data sources. These are the loaders which look for json, csv, and excel files in your home directory.|
---
