# SketchupOulu

The website is the product of a joint project between Department of Computer Sciences and Engineering, University of Oulu and Urban Planning division, Oulu city. The aim of the website is to create a collaborative environment where motivated citizens can contribute to the development of Oulu city. Using the service, not only you can communicate directly with officials city planners, you can also design the city yourself and then send the blueprint for reviewing.

Live version of the website can be found at http://vm0106.virtues.fi/

## Requirement

Python 3.4

## Installation

- Install required library

```
pip install -r requirements.txt
```

- Rename config.template.py to config.py then change database, email and captcha settings inside the file. 

- Install database

```
python install.py
```

- Insert required database records at /database/sketchup_oulu.sql

- Run

```
python run.py
```

By default, the website run local at http://localhost:5000

