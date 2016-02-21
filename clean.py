import os
import shutil
import json
import datetime

from app import app, db, app_dir
import app.users.models
from app.sketchup.models import Scenario, BuildingModel
import app.journal.models

# delete unused model file
models = BuildingModel.query.all()
model_files = []
for model in models:
    model_files.append(model.data_file)
scenarios = Scenario.query.all()
for scenario in scenarios:
    information = json.dumps(scenario.addition_information)
    for key in information:
        if key[:6] == 'model_':
            if (information[key]['directory'] + '.zip') not in model_files:
                model_files.append(information[key]['directory'] + '.zip')

model_dir = os.path.join(app_dir, 'static/models/building_models')
files = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
deleted_files = []
for file in files:
    filename_parts = file.split('.')
    current_filename = filename_parts[0]
    for i in range(1, len(filename_parts)-1):
        current_filename += '.' + filename_parts[i]
    extension = filename_parts[len(filename_parts)-1].lower()
    if file not in model_files: #delete file
        deleted_files.append(file)
        os.remove(os.path.join(model_dir, file))
        if extension == 'zip': #also delete folder
            try:
                shutil.rmtree(os.path.join(model_dir, current_filename))
            except:
                pass



print('Delete files:')
for file in deleted_files:
    print(file)