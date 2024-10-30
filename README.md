# demo-iot-platform
This is a small project to demonstrate an IoT platform. The platform consists of a device simulation backend, a REST API, and a frontend application. The device simulation backend simulates the operation of multiple devices which can be managed by a REST API and live data can be viewed using websockets. Currently it supports creating new devices of switch (light switching, appliances, AC, etc.) types and sensor (temperature, humidity, light, PIR motion, etc.) types which are all customisable by the user. 

The end goal is to have a frontend application that the user will be able to create and manage devices, view live/historical data, and control the devices. The data created by the user will be stored in a local SQLite database which is created on first run time. Because this is just a demo application, it is not recommended to use it in any production environment.

## Dependencies
- Python >= 3.8
- Docker
- Docker Compose

## How to run
### Installation
1. Clone the repository
2. Run `make install` to install the dependencies
### Running the application
1. Run options:
    - To run the application locally, run `make run`
    - To run the application locally with a pre-made database, run `make run-default`
    - To run the application in a Docker container, run `make run-docker`
    - To run the application in a Docker container with a pre-made database, run `make run-docker-default`
2. You can access the API of the application at `http://localhost:5555/docs`
3. You can see all live data produced by the devices by running `make run-ws-test` which will wait until it sees a local connection to the websocket server and then print the data received.
### Cleaning up
1. To clean up the application, run `make clean`. This will:
    - Remove the database file
    - Remove the Docker container and images
    - Remove the Python virtual environment

## To-Do
- [x] Device simulation backend
- [x] REST API
- [x] Websockets for live data
- [x] Database and integration
- [x] Dockerize the application
- [ ] Unit tests for backend
- [ ] Config files
- [ ] Frontend application
- [ ] Unit tests for frontend application
- [ ] Integration tests
- [ ] CI/CD pipeline
