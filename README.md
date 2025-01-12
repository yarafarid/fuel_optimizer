# Django Project  

## Overview  
This is a Django-based web application designed to optimize the route cost given a start and end destinations

## Features  
- Fuel Optimizer

## Installation  

### Prerequisites  
- Python 3.x  
- pip (Python package manager)  
- Virtualenv (recommended but optional)  

### Clone the Repository  
```bash  
git clone https://github.com/yarafarid/fuel_optimizer
cd fuel_optimizer
```

### Activate virtual env  
python -m venv env
source env/bin/activate

## Install Dependencies

The project dependencies are listed in the requirements.txt file. Install them using pip:
```bash
pip install -r requirements.txt
```


## Database Setup

Run the following commands to set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Add API keys in .env file
* Get opencagedata api key from https://opencagedata.com/guides/how-to-create-a-new-api-key

* Get openrouteservice api key from https://api.openrouteservice.org

* Get geoapify api key from https://www.geoapify.com/geocoding-api/

Create your .env file and write the api keys as following:
```bash
OPENCAGE_API_KEY=<OPENCAGE_API_KEY>
OPENROUTESERVICE_API_KEY=<OPENROUTESERVICE_API_KEY>
GEOAPIFY_API_KEY=<GEOAPIFY_API_KEY>
```

# Running the Project

Start the development server using the following command:
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/ in your browser to access the application.


