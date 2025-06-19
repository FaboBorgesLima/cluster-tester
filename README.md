# Server benchmarking tool

start virtual environment:

````bash
python3 -m venv .venv
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

run main.py:

```bash
python3 src/main.py
```
