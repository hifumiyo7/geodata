# GeoData Project

## Overview

GeoData is a simple REST API to store data in separate Redis database, provided in docker compose.

## Features

- Gathering information from separate API.
- Tests.

## Installation

To install the project, clone the repository:

```bash
git clone https://github.com/hifumiyo/geodata.git
cd geodata
```

This assumes you have docker on your computer.

## Usage

To use the project, run the dockerized version with ready Redis database:

```bash
docker compose up
```

## Testing

To run testing, please do following steps:

1. Enter the repository.
   1. In order to simplify later problems, you can use venv
2. Install both the dependencies and the dev dependencies:

```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

3.  Run using pytest

```bash
python -m pytest
```

## Additional functionalities possible to be added

1. Refactor the functions to simplify all the checks that proper information is in the call.
2. Create simplest e2e tests. This in first step could be just a Postman collection, sending the data, receiving the response, and checking the separate endpoints in order to ensure that there is no data returning on non-existent keys.
3. Current code assumes to check IP first, URL second. If there is a valid URL after wrong IP, it will fail.
4. Current code works based on full URL addresses, but because of ip-api it looks up based on netloc (which is enough). This will not work with short URLs.
5. Usage of ip-api as lookup site limits this to 45 requests (45 new keys) per minute.
6. Data dump is now included in docker file, in normal functioning it would not be, as it is just used to pre-load data to Redis.

## Endpoints

### POST `/address`

This endpoint adds an address (URL or IP) to Redis database, and returns what was added to user.

#### How to use

As input, please use JSON with field "ip" or "address" to add a new endpoint

#### Returns

JSON with information about geolocalization infromation of address

### GET `/address/<address>`

This endpoint gives information about previously searched endpoints and returns it as JSON.

### GET `/address`

This endpoint returns all data in database.

### GET `/address/addresses`

This endpoint gives information about all keys in Redis/ all adresses saved.

### DELETE `/address/<adress>`

This endpoint deletes an address from database.

### PUT `/address/<adress>`

This endpoint creates new information about record in database, creating it if it didn't exist, based on body in request.

### PATCH `/address/<adress>`

This endpoint updates a record in database with a JSON included in request body.

## Contact

For any questions or suggestions, please contact luczkiewiczjan@gmail.com .
