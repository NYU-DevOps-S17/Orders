# Bluemix Python Web application

[![Build Status](https://travis-ci.org/NYU-DevOps-S17/Orders.svg?branch=master)](https://travis-ci.org/NYU-DevOps-S17/Orders)
[![codecov](https://codecov.io/gh/NYU-DevOps-S17/Orders/branch/master/graph/badge.svg)](https://codecov.io/gh/NYU-DevOps-S17/Orders)

This repository if for Team Bravo Orders Project.

Follow the steps below to get the code up and running locally.

## Prerequisite : Vagrant and VirtualBox

## Get the code
From a terminal navigate to a location where you want this application code to be downloaded to and issue:
```bash
    $ git clone git@github.com:NYU-DevOps-S17/Orders.git
    $ cd Orders
    $ vagrant up
    $ vagrant ssh
    $ cd /vagrant
```
This will place you into an Ubuntu VM all set to run the code.

You can run the code to test it out in your browser with the following command:

    $ python run.py

You should be able to see it at: http://localhost:5000/

Swagger doc page: http://localhost:5000/apidocs/index.html

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

    $ vagrant halt

## BlueMix deployment

Once there is an update on the master branch, BlueMix will auto build/deploy the latest working copy.

    BlueMix URL: https://nyu-devops-orders.mybluemix.net/
    BlueMix Swagger doc page: https://nyu-devops-orders.mybluemix.net/apidocs/index.html?url=/v1/spec
    BlueMix docker container deploy: https://nyu-lab-docker-kj.mybluemix.net/

## BDD / TDD tests command when running locally

Use the following commands to test BDD and TDD results.
```bash
    BDD: $ behave
    TDD: $ nosetests
```

## Structure of application

**Procfile** - Contains the command to run when you application starts on Bluemix. 

**requirements.txt** - Contains the external python packages that are required by the application. 

**runtime.txt** - Controls which python runtime to use. In this case we want to use 2.7.9.

**README.md** - this readme.

**manifest.yml** - Controls how the app will be deployed in Bluemix and specifies memory and other services like Redis that are needed to be bound to it.

**app folder** - The folder where the python application script stored.

**old-files folder** - The folder containing old lab code.

**features folder** - The folder containing BDD tests feature file and steps.

**tests folder** - The folder containing TDD tests py files.
