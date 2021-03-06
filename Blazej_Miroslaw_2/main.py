from flask import Flask, request, abort
from apis import covid, google_maps

app = Flask(__name__)


def display_covid_data(data: covid.CovidData) -> str:
    return (
        f"Cases: {data.cases}, deaths: {data.deaths}, recovered: {data.recovered},"
        f" mortality: {data.mortality * 100:.2f}%, recoverability: {data.recoverability * 100:.2f}%"
    )


def get_html(data_to_display: dict) -> str:
    unordered_list_content = "".join(
        f"<li><em>{header}</em>: {data}</li>"
        for header, data in data_to_display.items()
    )
    countries = sorted(covid.get_countries())
    countries_options = "".join(
        f'<option value="{country}">{country}</option>' for country in countries
    )
    selectors = sorted(covid.SELECTORS.keys())
    selectors_options = "".join(
        f'<option value="{selector}">{selector}</option>' for selector in selectors
    )
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
            <div>Country: <select name="country"><option value="">-----</option>{countries_options}</select></div>
            <div>Selector: <select name="selector"><option value="">-----</option>{selectors_options}</select></div>
            <div>Min cases: <input name="min_cases" /></div>
            <div>Address: <input name="address" /></div>
            <div>Geo coords: <input name="lat" /><input name="lng" /></div>
            <div><input type="submit" /></div>
        </form>
    </body>
    </html>
"""


@app.route("/", methods=["GET", "POST"])
def main():
    world_data_from_all_endpoint = covid.get_world_data_from_all_endpoint()
    world_data_from_countries_endpoint = covid.get_world_data_from_countries_endpoint()
    matches = world_data_from_all_endpoint == world_data_from_countries_endpoint
    if request.method == "POST":
        context = {
            "/all": display_covid_data(world_data_from_all_endpoint),
            "/countries": display_covid_data(world_data_from_countries_endpoint),
            "matches": matches,
        }

        countries = []
        selected_country = request.form.get("country")
        if selected_country:
            countries.append(selected_country)

        address = request.form.get("address")
        if address:
            geocoded_country = google_maps.get_country_by_geocode(address)
            if geocoded_country:
                countries.append(geocoded_country)

        lat_str, lng_str = request.form.get("lat"), request.form.get("lng")
        if lat_str and lng_str:
            try:
                lat, lng = float(lat_str), float(lng_str)
            except ValueError:
                abort(400)

            reverse_geocoded_country = google_maps.get_country_by_reverse_geocode(
                lat, lng
            )
            if reverse_geocoded_country:
                countries.append(reverse_geocoded_country)

        for country in countries:
            world_data_from_country = covid.get_data_in_country(country)
            if world_data_from_country is not None:
                context[country] = display_covid_data(world_data_from_country)

        selector_name = request.form.get("selector")
        if selector_name:
            selector = covid.SELECTORS.get(selector_name)
            if selector is None:
                abort(400)

            min_cases = 0
            min_cases_str = request.form.get("min_cases")
            try:
                min_cases = int(min_cases_str) if min_cases_str else 0
            except ValueError:
                abort(400)
            (
                selector_country_name,
                selector_country_data,
            ) = covid.get_country_by_selector(selector, min_cases)
            context[
                f"max({selector_name})"
            ] = f"<b>{selector_country_name}</b>, {display_covid_data(selector_country_data)}"

        return get_html(context)
    else:  # request_method == 'GET'
        return get_html({})


if __name__ == "__main__":
    app.run()
