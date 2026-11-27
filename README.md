# CISC 327 Group 52

# Project: Inventory Management

## Prerequesites
This project will run just fine using only docker, however for local development you should also install python.

To get setup:
1. Clone the repository: `git clone https://github.com/zhouzhang2006/CISC-327---Group-52.git`
2. Go into the directory where the source code is: `cd CISC-327---Group-52/inventory-management`
3. Run `pip install -r requirements.txt` for local development

## Running with docker
```sh
docker build -t cisc327-a4
docker run --rm -p 5000:5000 cisc327-a4
```
Runs on port 5000 by default.
Ctrl + C to stop.

Note: No data is persisted after stopping as no storage implementation exists.

## Running E2E tests
Follow the instructions to run the docker container then:
Run `python -m pytest tests/e2e -v --headed`
