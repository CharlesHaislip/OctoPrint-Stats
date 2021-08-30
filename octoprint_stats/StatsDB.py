import octoprint.plugin
import octoprint.events
from octoprint.server import printer

from flask import jsonify, make_response
import os.path
import os
import datetime
import calendar
import sqlite3
from tinydb import TinyDB, Query, where
import pandas as pd
import shutil

'''
    Should probably transition this back over to an SQL based solution.
    If the database migration fails (migrate_v1), then the database can never be read until the user MANUALLY
    edits the file to remove the second JSON that apears in the JSON. As TinyDB relies on JSON.loads() internally,
    as can be seen from the stack trace, this causes the plugin to bge unable to read the database or write to it.
    Game plan: 
    First:
        Call migrate_v1 if needed. If it fails, undo the damage by looking for the following stirng: u'}{'. This 
        is garaunteed to be part of the problem. Use the file reader class prpared in JSON_READER and create a file
        writer class that will read and write the files character by character. Essentially, we will keep track of the
        last character (u'}') and the current character (u'{'). If it matches the termination string, we will stop
        writing. All of this is to increase performance and decrease memory cost. 
    Second:
        use tinydb to read the new  (or old) json file, and attempt to convert it to a database file compatible
        with sqlite. Again, we need to do this because a) sql is easier to manage than a json 'database', and b)
        we are trying to avoid the bug described in the 'preamble' above.
'''

class StatsDB:
    def __init__(self, plugin):
        original_db=plugin._settings.global_get_basefolder("logs") + "/octoprint_stats.db"
        new_db = plugin.get_plugin_data_folder()  + "/octoprint_stats.db"
        original_json=plugin._settings.global_get_basefolder("logs") + "/octoprint_stats.json"
        new_json = plugin.get_plugin_data_folder()  + "/octoprint_stats.json"
        old_backup = original_db + ".bak"
        new_db_backup = new_db + ".bak"

        # Move old file to the data folder instead of the Octoprint
        # Log folder, as was originally designed
        if os.path.exists(original_db):
            shutil.move(original_db, new_db)
        # /if os.path.exists(original_db)
        if os.path.exists(original_json):
            shutil.move(original_json, new_json)
        # /if os.path.exists(original_json)
        if (os.path.exists(old_backup)):
            shutil.move(old_backup, new_db_backup)
        # /if (os.path.exists(old_backup))

        self.DB_NAME_V1 = new_db
        self.DB_NAME = new_json

        if os.path.exists(self.DB_NAME_V1) == True:
            self.migrate_v1()
        # /if os.path.exists(self.DB_NAME_V1)
    # /def __init__(self, plugin)

    def migrate_v1(self):
        conn = sqlite3.connect(self.DB_NAME_V1)
        db = conn.cursor()

        dbnew = TinyDB(self.DB_NAME)
        events = dbnew.table('events')

        # Migrate connected
        sql = "SELECT event_time, port, baudrate FROM connected"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            port = row[1]
            baudrate = row[2]

            eventData = {'event_type': 'CONNECTED',
                         'data': {
                            'event_time': event_time.__str__(),
                             'port': port,
                             'baudrate': baudrate
                            }
                         }

            events.insert(eventData)
        # /for row in rows

        # Migrate disconnected
        sql = "SELECT event_time FROM disconnected"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]

            eventData = {'event_type': 'DISCONNECTED',
                         'data': {'event_time': event_time.__str__()}}

            events.insert(eventData)
        # /for row in rows

        # Migrate upload
        sql = "SELECT event_time, file, target FROM upload"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            target = row[2]

            eventData = {'event_type': 'UPLOAD',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'target': target
                            }
                         }

            events.insert(eventData)
        # /for row in rows

        # Migrate print_started
        sql = "SELECT event_time, file, origin, bed_target, tool0_target, tool1_target FROM print_started"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]
            bed_target = row[3]
            tool0_target = row[4]
            tool1_target = row[5]

            eventData = {'event_type': 'PRINT_STARTED',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'target': target
                            }
                         }

            events.insert(eventData)
        # /for row in rows

        # Migrate print_done
        sql = "SELECT event_time, file, ptime, origin, bed_actual, tool0_actual, tool1_actual, tool0_volume, tool1_volume, tool0_length, tool1_length FROM print_done"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            ptime = row[2]
            origin = row[3]
            bed_actual = row[4]
            tool0_actual = row[5]
            tool1_actual = row[6]
            tool0_volume = row[7]
            tool1_volume = row[8]
            tool0_length = row[9]
            tool1_length = row[10]

            eventData = {'event_type': 'PRINT_DONE',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'ptime': ptime,
                             'origin': origin,
                             'bed_actual': bed_actual,
                             'tool0_actual': tool0_actual,
                             'tool1_actual': tool1_actual,
                             'tool0_volume': tool0_volume,
                             'tool1_volume': tool1_volume,
                             'tool0_length': tool0_length,
                             'tool1_length': tool1_length
                            }
                        }

            events.insert(eventData)
        #/for row in rows

        # Migrate print_failed
        sql = "SELECT event_time, file, origin FROM print_failed"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_FAILED',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'origin': origin
                            }
                        }

            events.insert(eventData)
        # /for row in rows

        # Migrate print_cancelled
        sql = "SELECT event_time, file, origin FROM print_cancelled"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_CANCELLED',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'origin': origin
                            }
                        }

            events.insert(eventData)
        # /for row in rows

        # Migrate print_paused
        sql = "SELECT event_time, file, origin FROM print_paused"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_PAUSED',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'origin': origin
                            }
                        }

            events.insert(eventData)
        # /for row in rows

        # Migrate print_resumed
        sql = "SELECT event_time, file, origin FROM print_resumed"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            file = row[1]
            origin = row[2]

            eventData = {'event_type': 'PRINT_RESUMED',
                         'data': {
                             'event_time': event_time.__str__(),
                             'file': file,
                             'origin': origin
                            }
                        }

            events.insert(eventData)
        # /for row in rows

        # Migrate error
        sql = "SELECT event_time, perror FROM error"
        db.execute(sql)
        rows = db.fetchall()
        for row in rows:
            event_time = row[0]
            perror = row[1]

            eventData = {'event_type': 'ERROR',
                         'data': {
                             'event_time': event_time.__str__(),
                             'error': perror
                            }
                        }

            events.insert(eventData)
        # /for row in rows

        os.rename(self.DB_NAME_V1, self.DB_NAME_V1 + ".bak")
    # /def migrate_v1(self)

    def execute(self, data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        doc.insert(data)
    # /def execute(self, data, document)

    def query(self, search_data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        return doc.search(search_data)
    # /def query(self, search_data, document)

    def count(self, search_data, document):
        # DB
        db = TinyDB(self.DB_NAME)
        doc = db.table(document)
        return doc.count(search_data)
    # /def count(self, search_data, document)

    def getData(self, data):
        resData = []

        for row in data:
            resData.append(row["data"])
        # /for row in data

        return resData
    # /def getData(self, data)
# /class StatsDB