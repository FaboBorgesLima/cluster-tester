# Server benchmarking tool

This is a server benchmarking tool that allows you to test the performance of your server by simulating various workloads and measuring response times, throughput, and other performance metrics.

## Quickstart

start virtual environment:

````bash
python3 -m venv .venv
```

source venv:
```bash
source .venv/bin/activate
```

install dependencies:

```bash
pip install -r requirements.txt
````

install the application on your server:
[application](./app)

activate the virtual environment:

```bash
source .venv/bin/activate
```

configure the application:

```bash
cp db/config_example.json db/config.json
nano db/config.json
```

run help:

```bash
python3 src/ --help
```
