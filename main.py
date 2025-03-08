import numpy as np
import time
import random
import string
from datetime import datetime

def getCommitHash():
    characters = string.ascii_letters + string.digits  # Includes both uppercase and lowercase letters, and digits
    random_string = ''.join(random.choice(characters) for i in range(6)) # mock random commit hash
    return random_string

# manually tune latency/failure rate based on previous values, so alerts have a cascading effect
# default values are 499ms latency and 1% failure rate
def simulateMetrics(latency=499, failure_rate=1):
    latency = np.random.poisson(latency, 1)
    failure_rate = np.random.poisson(failure_rate, 1)

    return latency[0], failure_rate[0]

# set alert level based on latency and failure rate
def setAlertLevel(latency, failure_rate):
    alert_level = -1
    if latency > 500 or failure_rate > 2:
        alert_level = 2
    elif latency > 1000 or failure_rate > 5:
        alert_level = 1
    elif latency > 2000 or failure_rate > 10:
        alert_level = 0

    return alert_level

# handle alert notifications
# alert_level: alert level
# time_of_alert: intial time alert was triggered, so it knows when to send notifications
# log: add notifications to logs if needed
# alert_timestamps: map alert to timestamps of unresolved alerts, so which alerts to resolve
# alert: alert identifier
def handleNotifications(alert_level, time_of_alert, log, alert_timestamps, alert):
    # maps alert level to interval in which to send alerts in hours
    alert_interval = {
        0: 2,
        1: 12,
        2: 48,
    }

    interval = alert_interval[alert_level]

    # send alert every interval hours, except the first one
    if (round(time.time()) - time_of_alert) % (interval*60*60) == 0 and (round(time.time()) - time_of_alert) != 0:
        cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
        alert_notification = f"[{cur_time}] ALERT: Resending P{alert_level} alert (Still unresolved)"
        print(alert_notification)
        # add to log
        log[round(time.time())] = alert_notification
        alert_timestamps[alert].apppend(round(time.time()))
    
    # email team address at interval hours
    if (round(time.time()) - time_of_alert) == interval*60*60:
        cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
        email_notification = f"[{cur_time}] Sending email to team address for P{alert_level} alert"
        print(email_notification)

    # send email to skip-level boss at interval*5 hours
    if (round(time.time()) - time_of_alert) == interval*5*60*60:
        cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
        email_notification = f"[{cur_time}] Sending email to skip-level boss for P{alert_level} alert"
        print(email_notification)

# mock fixing alerts after a certain time
def alertResolution(alert_level, time_of_alert):
    # maps alert level to interval in which to send alerts in hours
    alert_interval = {
        0: 2,
        1: 12,
        2: 48,
    }

    interval = alert_interval[alert_level]
    
    # start working on fix at a random time within 5 intervals with commits
    if ((round(time.time()) - time_of_alert)) == (interval*round(random.uniform(0, 5), 2)*60*60):
        commit = getCommitHash()
        cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
        commit_notification = f"[{cur_time}] INFO: Commit {commit} submitted"
        print(commit_notification)

    
def main():
    active_alert_log = {} # logs active alerts
    system_status_log = {} # logs system status
    alert_timestamps = {} # maps alert to timestamps of unresolved alerts. Allows us to remove resolved alerts from the log
    alert_level = -1 # no alert initially
    current_alert = False
    # initial values for latency and failure rate
    latency, failure_rate = simulateMetrics()
    now = round(time.time())
    while True:
        # check if the least recent logs are older than 90 days, delete if so
        for key in list(active_alert_log.keys()):
            if (round(time.time()) - key)/(60*60*24) > 90:
                del active_alert_log[key]

        for key in list(system_status_log.keys()):
            if (round(time.time()) - key)/(60*60*24) > 90:
                del system_status_log[key]
            
        # every 5 minutes, simulate metrics
        if ((round(time.time()) - now)) % (5*60) == 0:  
            latency, failure_rate = simulateMetrics(latency, failure_rate)
            # no alert right now, so we can just set it to the new alert level
            if current_alert == False:
                alert_level = setAlertLevel(latency, failure_rate)
            else: 
                # we already have an alert, so we can only escalate the alert level
                # if metric returns to normal, we can disable the current alert
                new_alert_level = setAlertLevel(latency, failure_rate)
                if new_alert_level == -1: # no alert anymore
                    cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
                    alert_notification = f"[{cur_time}] INFO: Latency and Failure Rate normalized. Resolving P{alert_level} alert."
                    print(alert_notification)
                    alert_level = new_alert_level
                    current_alert = False
                    # remove resolved alert from logs
                    for timestamp in alert_timestamps[alert]:
                        del active_alert_log[timestamp]
                    del alert_timestamps[alert]
                else: # still alert
                    alert_level = max(alert_level, setAlertLevel(latency, failure_rate)) # prevent downlevel
            
            # log system status every 5 minutes
            cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
            system_status_log[round(time.time())] = f"[{cur_time}] INFO: Current System Status: Latency: {latency}ms, Failure Rate: {failure_rate}%, Alert Level: P{alert_level}"
            # if there's a new alert
            if alert_level != -1 and current_alert == False:
                current_alert = True
                cur_time = datetime.fromtimestamp(round(time.time())).strftime("%A, %B %d, %Y %H:%M:%S")
                alert_notification = f"[{cur_time}] Latency: {latency}ms, Failure Rate: {failure_rate}%, -> P{alert_level} Alert Triggered!"
                print(alert_notification)
                time_of_alert = round(time.time())
                active_alert_log[time_of_alert] = alert_notification
                alert = f"{latency}, {failure_rate}, {alert_level}" # alert identifier, pretty much unique since it's combination of metrics
                alert_timestamps[alert]= [time_of_alert]

        if alert_level != -1: # if there's an alert, we handle notifications, and try to resolve it
            handleNotifications(alert_level, time_of_alert, active_alert_log, alert_timestamps, alert)
            alertResolution(alert_level, time_of_alert)
        time.sleep(1)

if __name__ == "__main__":
    main()
