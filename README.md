# Prerequisites

This code snippet was tested on Anaconda 3.6 on Windows, but it should work on any Python 3.3+ distribution supporting virtualenv.

# Installation

```
pip install pipenv
pipenv install
```

# Running test scripts

```
pipenv run python tests/nexogen/aiohttp/batch.py
pipenv run python tests/nexogen/gis/batch_geocoding.py
pipenv run python tests/nexogen/gis/batch_routing.py
```