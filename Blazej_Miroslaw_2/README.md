# COVID-19 Tracker
## Used APIs:
* coronavirus-19-api - coronavirus data
* Google Maps API - geocoding, reverse geocoding
## Configuration
1) Use pipenv to install dependencies
2) You need to create `apis/keys.py` file with google maps API key:
    ```python
    GOOGLE_MAPS_API_KEY = "<your key>"
    ```
3) Run `main.py` to run test server
3) Use `run_in_gunicorn.sh` to run Gunicorn server with this app
5) Postman collection is included, set up `GOOGLE_API_KEY` if you want to use Google Maps API requests 