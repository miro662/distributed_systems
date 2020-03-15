import flask

from apis import covid

app = flask.Flask(__name__)


def display_covid_data(data: covid.CovidData) -> str:
    return f'Cases: {data.cases}, deaths: {data.deaths}, recovered: {data.recovered},' \
           f' mortality: {data.mortality * 100:.2f}%, recoverability: {data.recoverability * 100:.2f}%'


def get_html(data_to_display: dict) -> str:
    unordered_list_content = ''.join(
        f'<li><em>{header}</em>: {data}</li>' for header, data in data_to_display.items()
    )
    countries = sorted(covid.get_countries())
    countries_options = ''.join(f'<option value="{country}">{country}</option>' for country in countries)
    return f"""<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>COVID-19 Tracker</title>
    </head>
    <body>
        <h1>COVID-19 Tracker</h1>
        <ul>
            {unordered_list_content}
        </ul>
        <form action="/" method="post">
            Country: <select name="country">{countries_options}</select> <input type="submit" />
        </form>
    </body>
    </html>
"""


@app.route('/', methods=['GET', 'POST'])
def main():
    request = flask.request
    world_data_from_all_endpoint = covid.get_world_data_from_all_endpoint()
    world_data_from_countries_endpoint = covid.get_world_data_from_countries_endpoint()
    matches = world_data_from_all_endpoint == world_data_from_countries_endpoint
    if request.method == 'POST':
        selected_country = request.form.get('country')
        if selected_country:
            world_data_from_country = covid.get_data_in_country(selected_country)
            if world_data_from_country is None:
                flask.abort(404)
            return get_html({
                '/all': display_covid_data(world_data_from_all_endpoint),
                '/countries': display_covid_data(world_data_from_countries_endpoint),
                'matches': matches,
                selected_country: display_covid_data(world_data_from_country)
            })
        else:
            flask.abort(400)
    else: # request_method == 'GET'
        return get_html({
            '/all': display_covid_data(world_data_from_all_endpoint),
            '/countries': display_covid_data(world_data_from_countries_endpoint),
            'matches': matches
        })


if __name__ == '__main__':
    app.run()
