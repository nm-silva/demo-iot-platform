# demo-iot-platform
This is a small project to demonstrate an IoT platform. The platform consists of a device simulation backend, a REST API, and a frontend application. The device simulation backend simulates the operation of multiple devices which can be managed by a REST API and live data can be viewed using websockets. Currently it supports creating new devices of switch (light switching, appliances, AC, etc.) types and sensor (temperature, humidity, light, PIR motion, etc.) types which are all customisable by the user. 

The end goal is to have a frontend application that the user will be able to create and manage devices, view live/historical data, and control the devices. The data created by the user will be stored in a local SQLite database which is created on first run time. Because this is just a demo application, it is not recommended to use it in any production environment.

## To-Do
- [x] Device simulation backend
- [x] REST API
- [x] Websockets for live data
- [ ] Database and integration
- [ ] Unit tests for backend
- [ ] Frontend application
- [ ] Unit tests for frontend application
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] Dockerize the application

## Dependencies
- Python >= 3.8
- Docker
- Docker Compose
