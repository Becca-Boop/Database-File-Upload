# 1.03

import re
import os
import psycopg2
from datetime import datetime
import config


def main():
    cwd = os.getcwd()
    logpath = f"{cwd}/log.txt"
    if os.path.exists(logpath):
        log = open(logpath, "a")
    else:
        log = open(logpath, "w")

    log.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")  # write start time to log
    
    database, user, password, host, port, foldername = config.config()
    try:
        conn = psycopg2.connect(database = database, user = user, password = password, host = host, port = port)
        cur = conn.cursor()
    except psycopg2.Error as e:
        log.write("Error Opening database:\n")
        log.write(str(e))
        log.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        log.close()
        exit(e)

    log.write("Opened database successfully\n")

    path = f"{cwd}/{foldername}"

    pattern = re.compile("[0-9]+_mb_[0-9]+.*")  # matches to file format

    validfiles = []

    if not os.path.isdir(path):
        log.write(f"Cannot find folder {foldername}")
        log.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        log.close()
        conn.close()
        exit(f"Cannot find folder {foldername}")

    # checks if file has already been uploaded
    for file in os.listdir(path):
        match = pattern.match(file)
        if match:
            cur.execute(f"SELECT EXISTS(SELECT 1 FROM PowerDataFiles WHERE filename='{file}')")
            if cur.fetchone()[0]:
                pass
            else:
                validfiles.append(file)
                
    if not validfiles:
        print("No files to be uploaded")
        log.write("No files to be uploaded\n")


    for file in validfiles:

        f = open(f"{path}/{file}", "r")

        device = ""
        count = 1

        # add the file name to the table PowerDataFiles so doesn't get uploaded more than once
        cur.execute(f"INSERT INTO PowerDataFiles (filename) \
                        VALUES ('{file}')")

        try:
            for line in f:
                if count == 2:  # line 2 contains the name of the meter
                    x = line.split(",")
                    device = x[4][1:-1]
                    device = device.replace(" ", "")
                    device = "METER" + device
                    conn.commit()
                    # adds a field to the database for the meter if it's not already in the database
                    try:
                        cur.execute(f'ALTER TABLE PowerMeterReadings \
                                ADD "{device}" BIGINT')
                    except psycopg2.Error:
                        conn.rollback()
                        
                    count += 1
                    continue
                elif count < 8:  # the first 7 lines excluding line 2 are not relevent, so ignores
                    count += 1
                    continue
                line = line.strip('\n')

                x = re.split("\"", line)

                # removes unwanted elements in the list
                while '' in x:
                    x.remove('')

                while ' ' in x:
                    x.remove(' ')

                while ',' in x:
                    x.remove(',')

                timeStamp = x[2]
                meterReading = x[3]

                timeStamp = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')  # turns the timestamp into the correct format for uploading

                # checks if the timestamp already exists in the database, updates it if it does, and creates it if it doesn't
                cur.execute(f"SELECT EXISTS(SELECT 1 FROM PowerMeterReadings WHERE time='{timeStamp}')")
                if cur.fetchone()[0]:
                    cur.execute(
                        f'UPDATE PowerMeterReadings SET "{device}" = %s WHERE time = %s',
                        (meterReading, timeStamp)
                    )
                else:
                    cur.execute(
                        f'INSERT INTO PowerMeterReadings (time, "{device}") VALUES (%s, %s)',
                        (timeStamp, meterReading)
                    )
                count += 1

            log.write(f"File {file} has been uploaded\n")
        except e:
            log.write(f"{e}\n")
            log.write(f"File {file} failed to upload\n")

        f.close()
        
        conn.commit()

    conn.close()

    log.write("Closed database successfully\n")

    log.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n\n")  # write end time to log
    log.close()



if __name__ == '__main__':
    main()