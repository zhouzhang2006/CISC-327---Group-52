# CISC 327 Group 52

# Project: Inventory Management

## Prerequesites
This project will run just fine using only docker, however for local development you should also install python and run `pip install -r inventory-management/requirements.txt`.

## Running
```docker build -t cisc327-a4
docker run --rm -p 5000:5000 cisc327-a4
```
Runs on port 5000 by default.
Ctrl + C to stop.

Note: No data is persisted after stopping as no storage implementation exists.

## Running E2E tests
Follow the instructions to run the docker container then:
1. Enter the inventory-management directory: `cd inventory-management`
2. Run `python -m pytest tests/e2e -v --headed`
