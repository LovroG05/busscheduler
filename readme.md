
# Busscheduler API

API for calculating slovenian bus routes using easistent and ap-ljubljana.si

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt 
```

## Run
```bash
python main.py
```

## Requests
### api_get_lines_to
http GET request for getting bus lines for going TO school

ROUTE:
```txt
/api/v1/getlinestoschool
```
PARAMETERS:
```txt
start_station: int
end_station: int
date: str, format: %Y-%m-%d (2021-09-21)
time_margin: int //time between lesson start and bus arrival
early_time_margin: int //earliest time margin
```

### api_get_lines_from
http GET request for getting bus lines for going FROM school

ROUTE:
```txt
/api/v1/getlinesfromschool
```
PARAMETERS:
```txt
start_station: int
end_station: int
date: str, format: %Y-%m-%d (2021-09-21)
latest_arrival_required: bool ("true", "false")
latest_arrival: str, format: %H:%M
early_time_margin: int //time between lessons end and bus departure
```

### api_get_stations
http GET request to get json of stations and station id's

ROUTE:
```txt
/api/v1/getstations
```
