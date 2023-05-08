import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

def get_location():
    try:
        response = requests.get('http://ip-api.com/json/')
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
    location = get_location()
    visitor_ip = request.remote_addr
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
            <h3>当前服务器的计算机名是: {{ hostname }}</h3>
            <h3>服务器位置: {{ location.location }}</h3>
            <h3>访问者地址: {{ visitor_ip }}</h3>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{{ location.latitude }}, {{ location.longitude }}], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);
                L.marker([{{ location.latitude }}, {{ location.longitude }}]).addTo(map);
            </script>
        </body>
    </html>
    ''', hostname=hostname, location=location, visitor_ip=visitor_ip)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
