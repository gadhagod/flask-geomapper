import flask
import boto3
import io
from json import loads, dumps
import flask
from random import randint
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
from json import loads
from os import remove, getenv
from requests import get
from typing import Union, Callable, List

class flask_geomapper(object):
    """
    flask_geomapper base class.
    """

    def __init__(
        self, 
        app: flask.Flask, 
        count_trigger: Callable=None, 
        exclude_routes: List[str]=[], 
        exclude_status_codes: List[int]=[], 
        ip_api_key: Union[str, None]=None, 
        debug=False
    ):
        """
        Base class for flask_geomapper. Initializes the extension.

        Params: 
            * app: Instance of app
                * type: `flask.Flask`
            * count_trigger: Location loggin trigger
                * type: `typing.Callable`
                * default: `None`, translating to `:param app:.after_request`
            * exclude_routes: Routes to be ignored in mapping
                * type: List of strs
                * default: `[]` (empty list)
            * exclude_status_codes: Status to be ignored in mapping (when type `flask.Response` is first param of param `count_trigger`)
                * type: List of ints
                * default `[]` (empty list)
            * ip_api_key: API key for "https://ip-api.com"
                * type: str
                * default: None (free tier, 45 reqs per min)
        """
        plt.rcParams["figure.figsize"] = (5, 5)
        plt.switch_backend("Agg")

        self.clear_history()
        self.exclude_routes = exclude_routes
        self.exclude_status_codes = exclude_status_codes
        self.base_url = "http://ip-api.com/json" if not ip_api_key else "http://pro-ip-api.com/json"
        self.ip_api_key = ip_api_key
        self.debug = debug
        
        def update_history(response: Union[flask.Response, None]=None) -> Union[flask.Response, None]:
            if flask.request.environ["PATH_INFO"] not in self.exclude_routes and (response.status_code not in self.exclude_status_codes if response else True):
                ip = flask.request.headers.get("X-Forwarded-For", flask.request.remote_addr) if not self.debug else get("https://api64.ipify.org/").text
                location_data = get(f"{self.base_url}/{ip}?key={self.ip_api_key}").json()

                if location_data["status"] == "fail":
                    if location_data["message"] == "no API key supplied, order one at https://signup.ip-api.com/": raise Exception("API key expired or invalid")
                    if location_data["message"] == "reserved range": raise Exception("`127.0.0.1` was the request ip. Set the debug parameter to true when initializing flask_locations to accept this.")

                current_long = location_data["lon"]
                current_lat = location_data["lat"]

                self.history["Longitude"].append(current_long)
                self.history["Latitude"].append(current_lat)
                self.history["ip"].append(ip)

            return response

        (count_trigger or app.after_request)(update_history)

    def get_img(
        self, 
        world_map_data: dict={"color": "white", "edgecolor": "black"},
        map_plot_point: dict={"color": "red", "markersize": 5},
        geopandas_dataset: str="naturalearth_lowres"
    ) -> io.BytesIO:
        """
        Gets the image of map of requests.

        Params:
            * world_map_data: Configuration for map of world
                * type: dict
                * default: `{"color": "white", "edgecolor": "black"}`
                * docs: https://geopandas.readthedocs.io/en/latest/docs/reference/api/geopandas.GeoDataFrame.plot.html
            * map_plot_point: Configuration for map dot
                * type: dict
                * default: `{"color": "red", "markersize": 5}`
                * docs: https://geopandas.readthedocs.io/en/latest/docs/reference/api/geopandas.GeoDataFrame.plot.html
            * geopandas_dataset: Map dataset.
                * type: str
                * default: `"naturalearth_lowres"`
                * docs: https://geopandas.org/docs/reference/api/geopandas.datasets.get_path.html

        Returns: Image object.
            * type: `io.BytesIO`
            * docs: https://docs.python.org/3/library/io.html#binary-i-o

        Examples:
            * save image: `get_img().save()`
            * flask send file: `flask.send_file(get_img(), mimetype="image/png")
        """
        dataframe = pd.DataFrame(self.history)
        gdf = geopandas.GeoDataFrame(dataframe, geometry=geopandas.points_from_xy(dataframe.Longitude, dataframe.Latitude))
        world = geopandas.read_file(geopandas.datasets.get_path(geopandas_dataset))
        ax = world.plot(**world_map_data)
        gdf.plot(ax=ax, **map_plot_point)

        img_data = io.BytesIO()
        plt.savefig(img_data, format="png")
        img_data.seek(0)

        img_data.save = lambda file_name: open(file_name, "wb").write(img_data.getbuffer())

        return img_data

    def clear_history(self) -> dict: 
        """
        Clears all stored locations.

        Returns: Location history.
            * type: dict
        """
        self.history: dict = {"Longitude": [], "Latitude": [], "ip": []}
        return self.history

    def pop_first_location(self) -> dict: 
        """
        Removes the first stored location.

        Returns: Location history.
            * type: dict
        """
        self.history["Longitude"], self.history["Latitude"], self.history["ip"] = self.history["Longitude"][1:], self.history["Latitude"][1:], self.history["ip"][1:]
        return self.history

    def add_locations(self, locations: list, lon_key: str="longitude", lat_key: str="latitude", ip_key: Union[str, None]=None) -> dict: 
        """
        Manually adds locations.

        Parmeters:
            * locations: A list of dicts, each containing longitude, latitude, and optionally an IP
                * type: list of dicts
            * lon_key: The dict key of items in param `locations` that contain longitude.
                * type: str
                * default: `"longitude"`
            * lat_key: The dict key of items in param `locations` that contain latitude.
                * type: str
                * default: `"latitude"`
            * ip_key: The dict key of items in param `locations` that contain the IP.
                * type: str
                * default: `None`

        Returns: Location history.
            * type: dict

        Example:
            * add single location: `add_locations([{"longitude": "100.5", "latitude": "50.5"}])

        """
        for i in locations:
            self.history["Longitude"].append(i[lon_key])
            self.history["Latitude"].append(i[lat_key])
            self.history["ip"].append(i[ip_key] if ip_key else None)

        return self.history

    def shape_to_docs(self, lon_key: str="longitude", lat_key: str="latitude", ip_key: Union[str, bool]="ip") -> list:
        """
        Converts all stored locations into a document database-compatible format.

        Parameters:
            * locations: A list of dicts, each containing longitude, latitude, and optionally an IP
                * type: list of dicts
            * lon_key: The dict key of items in param `locations` that contain longitude.
                * type: str
                * default: `"longitude"`
            * lat_key: The dict key of items in param `locations` that contain latitude.
                * type: str
                * default: `"latitude"`
            * ip_key: The dict key of items in param `locations` that contain the IP.
                * type: str
                * default: "ip"

        Returns: all locations
            * type: dict
        """
        docs = []
        for i in range(len(self.history["ip"])):
            doc = {
                lon_key: self.history["Longitude"][i],
                lat_key: self.history["Latitude"][i],
            }
            if ip_key: doc[ip_key] = self.history["ip"][i]
            docs.append(doc)

        return docs