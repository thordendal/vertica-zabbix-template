#!/usr/bin/python
import datetime
import sys
from optparse import OptionParser
import vertica_python
from vertica_python import connect


### Arguments
parser = OptionParser()
parser.add_option("-i", "--host", dest="host",
                help="Vertica host name / ip")
parser.add_option("-u", "--username", dest="username",
                help="Vertica DB username")
parser.add_option("-p", "--password", dest="password",
                help="Vertica DB password")
parser.add_option("-m", "--metric", dest="metric",
                help="Vertica DB metric")
parser.add_option("-d", "--database", dest="database",
                help="Vertica DB")

(options, args) = parser.parse_args()

if (options.host == None):
    parser.error("-i host is required")
if (options.username == None):
    parser.error("-u username is required")
if (options.password == None):
    parser.error("-p password is required")
if (options.metric == None):
    parser.error("-m metric is required")
if (options.database == None):
    parser.error("-d database is required")
###


### metric list
metrics = {
    "db_size_on_disk":{"type":"int", "sql":"SELECT SUM(used_bytes) FROM PROJECTION_STORAGE"},
    "db_size_raw":{"type":"int", "sql":"SELECT database_size_bytes FROM v_catalog.license_audits ORDER  BY audit_start_timestamp DESC LIMIT 1;"},
    "connections":{"type":"int", "sql":"SELECT count(*) FROM SESSIONS;"},
    "active_connections":{"type":"int", "sql":"select count(*) from sessions where current_statement <> '' and session_id <> current_session();"},
    "node_count":{"type":"int", "sql":"select count(*) from nodes;"},
    "node_down_count":{"type":"int", "sql":"select count(*) from nodes where node_state not ilike 'UP';"},
    "active_events_count":{"type":"int", "sql":"SELECT COUNT(*) FROM active_events_mon WHERE EVENT_SEVERITY NOT IN ('Informational','Debug','Notice','Warning');"},
    "share_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='S';"},
    "insert_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='I';"},
    "shared_insert_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='SI';"},
    "exclusive_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='X';"},
    "tuple_mover_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='T';"},
    "usage_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='U';"},
    "owner_lock_count":{"type":"int", "sql":"SELECT COUNT(*) FROM LOCKS WHERE LOCK_MODE='O';"},
    "version":{"type":"string", "sql":"SELECT version();"},
    "deleted_row_count":{"type":"int", "sql":"select sum(deleted_row_count) from v_monitor.delete_vectors;"},
    "deleted_vector_count":{"type":"int", "sql":"select count(*) from v_monitor.delete_vectors;"},
    "last_backup_time":{"type":"float", "sql":"select EXTRACT(EPOCH FROM backup_timestamp)::INT from database_backups_mon union select 0 order by 1 desc limit 1;"},
    "ahm_time":{"type":"int", "sql":"select EXTRACT(EPOCH FROM time)::INT from system join vs_epochs on epoch_number = ahm_epoch;"},
    "ros_count":{"type":"int", "sql":"select max(ros_count) from v_monitor.projection_storage;"},
    "cpu_usage":{"type":"float", "sql":"SELECT average_cpu_usage_percent FROM cpu_usage_mon ORDER BY end_time DESC LIMIT 1;"}
}
### 

### connection
conn_info = {'host': options.host,
             'port': 5433,
             'read_timeout': 20,
             'user': options.username,
             'password': options.password,
             'database': options.database}
#in case of a failure we need to catch the error and return nothing to zabbix
try:

        # simple connection, with manual close
        connection = vertica_python.connect(**conn_info)
        cur = connection.cursor()

        # find the right metric
        for k,vh in metrics.items():

                if (k == options.metric):

                        cur.execute(metrics[k]["sql"])
                        row = cur.fetchone()
                        if row: 
                                print(row[0])
                        cur.close()
                        break

        # close the connection
        connection.close()
except: # catch *all* exceptions
        print('')
