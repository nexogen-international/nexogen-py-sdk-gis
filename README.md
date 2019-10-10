# Prerequisites

This code snippet was tested on Anaconda 3.6 on Windows, but it should work on any Python 3.3+ distribution supporting virtualenv.

# Installation

```
pip install pipenv
pipenv install
```

# Creating a .env file

You need to create a .env file or assign the right value to both NEXOGEN_GIS_API_URL and NEXOGEN_GIS_API_KEY environment variables.
Your .env file should look like this:

```
# API endpoint
NEXOGEN_GIS_API_URL=... # API endpoint URL without protocol
NEXOGEN_GIS_API_KEY=... # API key
```

# Running test scripts

```
pipenv run python tests/nexogen/aiohttp/batch.py
pipenv run python tests/nexogen/gis/batch_geocoding.py
pipenv run python tests/nexogen/gis/batch_routing.py
```