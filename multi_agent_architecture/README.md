# 🔥Establish multi-agent connection based on CARLA and Socket.IO

> [!IMPORTANT]
> Software config: CARLA 0.9.13 Ubuntu 20.04


## 1. 💽Install socket.io
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

## 2. 🚀Run socket server  ```server_socket.js```
```
node server_socket.js
```

## 3.🚀 Run ```manual_control_with_websocket.py``` on the CARLA host and client
HOST_IP also needs to be modified in **manual_control_with_websocket.py line 187**
```
# host
cd ~/carla
./CarlaUE4.sh -carla-rpc-port=2000 -carla-server -carla-rpc-bind=<HOST_IP> (default: 192.168.1.1)
python3 manual_control_with_websocket.py

# client
python3 manual_control_with_websocket.py --host <HOST_IP>(default: 192.168.1.1) --port 2000

```

## 4.🚀 Run ```website.html``` to get the real-time img and info.
![website](../assets/website_multiagent.png)


## 🔥Example of Multi-agent Architecture

| Multi-agent Architecture |Human-in-the-loop Example based on VR|
| :---: | :---: |
|<video src="https://github.com/user-attachments/assets/a0a0c98c-8c14-421c-ba32-36fcae86e27a" controls width="100%"></video>|<video src="https://github.com/user-attachments/assets/6dda29f7-b14b-48ea-8945-f158833291f3" controls width="100%"></video>|


## 📚 Other resources
You can use ```Town10_BEV_Capture.py``` to capture the BEV image of any map in CARLA
