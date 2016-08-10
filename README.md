# Template App Vertica

This repo contains Zabbix template and zabbix-agent configuration for simple Vertica monitoring.  
TODO: Cluster nodes discovery, separate performance monitoring for every node.

## Setting up

On your Vertica server:
```bash
sudo apt-get install python-pip
pip install --pre pytz
pip install vertica-python
```

Create Vertica user `zabbix` with password `SECRET`, create role `monitoring`, then grant `monitoring` to `zabbix` and set it default for user.
Note that password you set here also must be written into [`userparameter_vertica.conf`](userparameter_vertica.conf).
```sql
CREATE ROLE monitoring;
CREATE USER zabbix IDENTIFIED BY 'SECRET';
GRANT monitoring TO zabbix;
ALTER USER zabbix DEFAULT ROLE monitoring;
```
Then connect to your database:
```sql
\c mydatabase
```

Grant neccessary privileges to `monitoring`:
```sql
CREATE VIEW active_events_mon AS SELECT * FROM active_events;
CREATE VIEW cpu_usage_mon AS SELECT * FROM cpu_usage_mon;
CREATE VIEW database_backups_mon AS SELECT * FROM v_monitor.database_backups;
GRANT SELECT ON activee_events_mon TO monitoring;
GRANT SELECT ON cpu_usage_mon TO monitoring;
GRANT SELECT ON database_backups_mon TO monitoring;
```

Put [`vertica_stats.py`](scripts/vertica_stats.py) to directory where zabbix-agent can execute it, e.g. `/home/zabbix/scripts`, ang chmod+chown it:
```bash
chown zabbix:zabbix vertica_stats.py
chmod 755 vertica_stats.py`.
```

Then put [`userparameter_vertica.conf`](userparameter_vertica.conf) to your `zabbix_agentd.d` directory, e.g. `/etc/zabbix/zabbix_agentd.d/` and restart your zabbix-agent.
