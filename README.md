
# 构建映像

app.py

```python
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
            <h3>访问者地址: {{ visitor_location.location }}</h3>
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

```

上述代码是一个使用Python的Flask框架创建的简单Web应用程序。下面是代码的分段解释：

1. 导入所需的库：

```python
import os
import requests
from flask import Flask, render_template_string, request
```

这里，我们导入`os`库来获取环境变量，`requests`库来进行HTTP请求（获取IP地址的地理位置信息），以及从`flask`库导入`Flask`、`render_template_string`和`request`模块。

2. 创建Flask应用实例：

```python
app = Flask(__name__)
```

这里创建了一个Flask应用实例，用于定义和运行Web应用程序。

3. 定义`get_location`函数：

这个函数接收一个可选的IP地址参数。如果提供了IP地址，函数将查询该IP地址的地理位置信息；如果未提供，将查询服务器的地理位置信息。函数返回一个包含地理位置信息（国家、地区、城市）、纬度和经度的字典。

4. 定义根路由（`/`）的处理函数`get_hostname`：

这个函数首先获取宿主机的计算机名。接下来，它获取服务器和访问者的地理位置信息。然后，使用`render_template_string`函数渲染一个HTML模板，将所有这些信息传递给模板。

5. HTML模板：

模板包含一个地图，它使用Leaflet库创建。地图上显示了服务器和访问者的位置，以及它们之间的连线。

模板还显示了服务器名称、服务器位置和访问者位置。

6. 运行Flask应用：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

这个部分检查当前模块是否是主模块。如果是，它将启动Flask应用，监听所有网络接口（`0.0.0.0`）的80端口。这样，应用程序将在Web上公开。

requirements.txt

```text
Flask==2.1.1
requests==2.26.0
```


Dockerfile

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]

```

这是一个Dockerfile，用于创建一个包含Python 3.9-slim基础镜像的Docker容器。这个容器的目的是运行前面提到的Flask Web应用程序。以下是Dockerfile中每行代码的解释：

1. `FROM python:3.9-slim`

   这行代码指定基础镜像为Python 3.9-slim，一个轻量级的Python 3.9镜像。

2. `WORKDIR /app`

   这行代码将容器内的工作目录设置为`/app`。后续的`COPY`和`RUN`命令都将在此目录下执行。

3. `COPY requirements.txt requirements.txt`

   这行代码将构建上下文中的`requirements.txt`文件复制到容器内的工作目录。这个文件应该包含Flask应用所需的Python库及其版本。

4. `RUN pip install -r requirements.txt`

   这行代码使用`pip`安装`requirements.txt`中列出的Python库。这些库是运行Flask应用所需的依赖。

5. `COPY app.py .`

   这行代码将构建上下文中的`app.py`文件复制到容器内的工作目录。这个文件包含Flask应用的代码。

6. `CMD ["python", "app.py"]`

   这行代码指定容器的默认命令为`python app.py`。当容器启动时，它将运行这个命令，启动Flask应用。
   

构建映像

```bash
docker build -t myapp .
```


运行容器
```bash
docker run -d -p 80:80 -e HOST_HOSTNAME=$(hostname) --name myapp myapp
```


# 直接使用现有映像

```bash
docker run -d -p 80:80 -e HOST_HOSTNAME=$(hostname) --name myapp chengzh/myapp
```



# Cloud-init

```yaml
#cloud-config
package_upgrade: true

packages:
  - docker.io
  - curl

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - docker pull chengzh/myapp
  - docker run -d -p 80:80 -e HOST_HOSTNAME=$(hostname) --name myapp chengzh/myapp
```


