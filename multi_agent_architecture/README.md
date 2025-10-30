# Tutorial to establish the multi-agent connection based on CARLA and Socket.IO

> [!IMPORTANT]
> Software config: CARLA 0.9.13 Ubuntu 20.04


## 1. Install socket.io
```
# install socket.io 
npm init -y
npm install socket.io
pip install python-socketio
pip install websocket-client

# install plugin for the website
npm install express
express -V
```

## 2. Run socket server
```
node server_socket.js
```

## 3. Run manual_control_with_websocket.py on the CARLA host and client

## 4. Run website.html to get the real-time img and info.
![website](../img/website_multiagent.png)
