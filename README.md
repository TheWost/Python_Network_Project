# Python TCP socket server & server example

Very very simple, multi device TCP socket application built in Python for real-time network communiaction

## Prerequisites

- **Python 3.x** installed

## Configuration

**Server Host** `0.0.0.0`
**Port** `8000`

## Installation

Clone the repository:

```bash
git clone https://github.com/TheWost/Python_Network_Project.git
cd Python_Network_Project
```

Install the required dependencies:

```bash
python -m pip install .
```

### Dependencies

- `prompt-toolkit` — Interactive terminal input
- `colorama` — Colored terminal messages

## How to run

### New menu

1. You can on windows run `run.bat` and on linux `run.sh`.

2. Now you'd have to configure

#### If you are server

- Set configuration in server_config to your liking inside server object.
  - `0.0.0.0` so everyone can connect
  - `127.0.0.1` so everyone from your computer can connect

#### If you are client

- Inside your `server_config.json` put in client `host: Your server IPV4`

1. Then choose whoever you want to be

### Old method

#### If you are server

1. Set configuration in server_config to your liking inside server object.
    - `0.0.0.0` so everyone can connect
    - `127.0.0.1` so everyone from your computer can connect

2. On machine you want to host server in terminal run:

```bash
python -m server.main
```

(This terminal won't be usable while server is running)

#### If you are client

1. Inside your `server_config.json` put in client `host: Your server IPV4`
2. On any local machine run:

```bash
python -m client.main
```

1. Done! you are connected to that server

This is my first repo. So please don't be mean
