from flask import Flask

from apis import covid

app = Flask(__name__)


def display_covid_data(data: covid.CovidData) -> str:
    return f'Cases: {data.cases}, deaths: {data.deaths}, recovered: {data.recovered}'


@app.route('/')
def main():
    world_data_from_all_endpoint = covid.get_world_data_from_all_endpoint()
    world_data_from_countries_endpoint = covid.get_world_data_from_countries_endpoint()
    matches = world_data_from_all_endpoint == world_data_from_countries_endpoint
    return f"""<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>COVID-19 Tracker</title>
    </head>
    <body>
        <h1>COVID-19 Tracker</h1>
        <ul>
            <li>/all</pre>: {display_covid_data(world_data_from_all_endpoint)}</li>
            <li>/countries</pre>: {display_covid_data(world_data_from_countries_endpoint)}</li>
            <li>matches: {matches}</li>
        </ul>
    </body>
</html>
"""


if __name__ == '__main__':
    app.run()
