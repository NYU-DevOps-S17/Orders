from flask import Flask
from flasgger import Swagger

# Create the Flask aoo
app = Flask(__name__)

# Load Configurations
app.config.from_object('config')

# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "Orders Resource",
            "description": "This is a the Orders resource.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)

import server
import models
import custom_exceptions
