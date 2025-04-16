# Database Meter Readings Upload - F2 Chemicals

## Database Setup

This script requires there to be two tables in the database named powermeterreadings and powerdatafiles where powermeterreadings initally consists of just one field named 'time' with the data type TIMESTAMP.
The script will update this table as needed.
The powerdatafiles table consists of one field 'fieldname' with the data type VARCHAR(255).

After running the script, the powermeterreadings table will contain a field for each meter where the field name is the meter name and each cell is the meter reading of the meter at the timestamp of the record.
The powerdatafiles table will contain the name of every file that has been uploaded.

## Usage

Use the config.py file to connect the python script to the database by updating the variables to the database values.
In the config.py file you also need to update the 'foldername' variable with the path to the folder containing the files from the point of the current working directory.

Once the config.py file is set up, run the script with python main.py (or python3 main.py depending on your version of python).
The script will run through all of the files in the folder, check if it has already been updated to the database using the powerdatafiles table, and if not upload its contents to the powermeterreadings table and it's name to the powerdatafiles table.
Every time a new device/meter is uploaded a new field is created in the database where the field name is the name of the meter.
