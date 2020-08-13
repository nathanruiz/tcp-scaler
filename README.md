# TCP scaler #
This is a simple TCP proxy that starts an AWS EC2 instance when any number of
clients exist, and then forward them to a backend instance when available.

## Build ##
These instructions have been tested on Debian 10.

Installed the required packages:
```
apt-get install python3 python3-venv netcat
```

Set up a virtualenv environment:
```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
```

Build the wheel:
```
pip install wheel
python setup.py bdist_wheel
```

## Installing ##
Copy the wheel to the desired system, and run the following to install:
```
apt-get install python3 python3-pip
pip3 install <wheel>
```

The `tcp-scaler` and `tcp-scaler-forwarder` commands will now be available.

## Systemd service ##
Use the following to set up tcp-scaler as a service (tested under Debian 10):

```bash
PORT=<frontend-port>
INSTANCE_ID=<instance-id>
BACKEND_PORT=<backend-port>
REGION=<aws-region>

cat > /lib/systemd/system/tcp-scaler-forwarder-${INSTANCE_ID}-${BACKEND_PORT}.socket <<EOF
[Unit]
Description=TCP forwarder component of tcp-scaler

[Socket]
ListenStream=0.0.0.0:${PORT}
Accept=yes

[Install]
WantedBy=sockets.target
EOF

cat > /lib/systemd/system/tcp-scaler-forwarder-${INSTANCE_ID}-${BACKEND_PORT}@.service <<EOF
[Unit]
Description=TCP forwarder component of tcp-scaler
Requires=tcp-scaler-forwarder-${INSTANCE_ID}-${BACKEND_PORT}.socket

[Service]
Type=simple
Environment="AWS_DEFAULT_REGION=${REGION}"
ExecStart=-tcp-scaler-forwarder -v ${INSTANCE_ID} /tmp/tcp-scaler-${INSTANCE_ID}-${BACKEND_PORT} ${BACKEND_PORT}
StandardInput=socket
StandardError=journal
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > /lib/systemd/system/tcp-scaler-${INSTANCE_ID}-${BACKEND_PORT}.service <<EOF
[Unit]
Description=Instance manager for tcp-scaler

[Service]
Type=simple
Environment="AWS_DEFAULT_REGION=${REGION}"
ExecStart=tcp-scaler -v ${INSTANCE_ID} /tmp/tcp-scaler-${INSTANCE_ID}-${BACKEND_PORT}

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start tcp-scaler-${INSTANCE_ID}-${BACKEND_PORT}.service
systemctl start tcp-scaler-forwarder-${INSTANCE_ID}-${BACKEND_PORT}.socket
```
