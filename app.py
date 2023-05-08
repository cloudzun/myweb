import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

def get_location(ip_address=None):
    try:
        url = f'http://ip-api.com/json/{ip_address}' if ip_address else 'http://ip-api.com/json/'
        response = requests.get(url)
        location_data = response.json()
        if location_data['status'] == 'success':
            return {
                'location': f"{location_data['country']}, {location_data['regionName']}, {location_data['city']}",
                'latitude': location_data['lat'],
                'longitude': location_data['lon']
            }
        else:
            return {'location': '未知', 'latitude': None, 'longitude': None}
    except:
        return {'location': '未知', 'latitude': None, 'longitude': None}

@app.route('/')
def get_hostname():
    hostname = os.environ.get('HOST_HOSTNAME', '未知')
    server_location = get_location()
    visitor_ip = request.remote_addr
    visitor_location = get_location(visitor_ip)
    return render_template_string('''
    <!DOCTYPE html>
    <html>
        <head>
            <title>服务器信息</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                #map {width: 75vw; height: 75vh;}
            </style>
        </head>
        <body>
            <h3>服务器名称: {{ hostname }}</h3>
            <h3>服务器位置: {{ server_location.location }}</h3>
            <h3>访问者位置: {{ visitor_location.location }}</h3>
            <div id="map"></div>
            <script>
                var map = L.map('map').fitBounds([
                    [{{ server_location.latitude }}, {{ server_location.longitude }}],
                    [{{ visitor_location.latitude }}, {{ visitor_location.longitude }}]
                ]);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                var serverMarker = L.marker([{{ server_location.latitude }}, {{ server_location.longitude }}]).addTo(map);
                serverMarker.bindPopup("服务器位置: {{ server_location.location }}").openPopup();

                var visitorMarker = L.marker([{{ visitor_location.latitude }}, {{ visitor_location.longitude }}]).addTo(map);
                visitorMarker.bindPopup("访问者位置: {{ visitor_location.location }}");

                var latlngs = [
                    [{{ server_location.latitude }}, {{ server_location.longitude }}],
                    [{{ visitor_location.latitude }}, {{ visitor_location.longitude }}]
                ];
                var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
            </script>
        </body>
    </html>
    ''', hostname=hostname, server_location=server_location, visitor_ip=visitor_ip, visitor_location=visitor_location)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
