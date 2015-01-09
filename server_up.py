# coding: utf-8
from os import popen, system, startfile
from time import sleep

import requests
from pyquery import PyQuery


# web listing active servers
SERVER_STATUS_URL = 'http://refactor.jp/chivalry/?country=AR'
# if this text is present, the server is up
SERVER_NAME = 'Argentina | Round Table | chivarg.com'
# if this text is present, the web list is working
WEB_CONTROL_TEXT = 'Servers in'
# windows task name of the server
TASK_NAME = 'UDKLogging.exe'
# path to the server bat file to start it
SERVER_SCRIPT = r'C:\Documents and Settings\mejorserver\Desktop\chivalry\roun_table\start_server.bat'

# time intervals, in seconds
# every how much check for visibility?
CHECK_INTERVAL = 60
# how much does the server takes to start and appear on the lists
SERVER_START_DELAY = 300
# how much does the server takes to stop
SERVER_STOP_DELAY = 30


# possible server visibility values
VISIBLE = 'visible'
INVISIBLE = 'invisible'
UNKNOWN = 'unknown'


def server_visible():
    """Is the server visible in the servers list?"""
    print 'Checking server visibility...'
    try:
        response = requests.get(SERVER_STATUS_URL)
        if WEB_CONTROL_TEXT not in response:
            # can't be sure the web is working, the page is returning something
            # not expected
            visibility = UNKNOWN
        elif TASK_NAME not in response:
            # server not in list, is invisible
            visibility = INVISIBLE
        else:
            # server in list, but is it responding?
            list_row = PyQuery(response)('a.contains("%s")' % SERVER_NAME).parents('tr')
            if 'noResponse' in list_row.attr('class'):
                # the site says the server is not responding
                visibility = INVISIBLE
            else:
                # server visible! yay for uptime :)
                visibility = VISIBLE

    except Exception as err:
        # web not accessible, can't be sure of server status
        print err
        visibility = UNKNOWN

    print 'Result:', visibility
    return visibility

def server_running():
    """Is the server process running in windows?"""
    print 'Checking server running...'
    tasks = popen('tasklist').readlines()
    running = TASK_NAME in tasks
    print 'Result:', running
    return running


def stop_server():
    """Kill the server process in windows."""
    print 'Stopping server...'
    system('taskkill /im ' + TASK_NAME)
    sleep(SERVER_STOP_DELAY)
    print 'Done'


def start_server():
    """Start the server process in windows."""
    print 'Starting server...'
    startfile(SERVER_SCRIPT)
    sleep(SERVER_START_DELAY)
    print 'Done'


def check_loop():
    while True:
        running = server_running()
        if running:
            # server running, is it visible?
            visibility = server_visible()
            if visibility == INVISIBLE:
                # stop it, will be restarted in next check
                stop_server()
            elif visibility == VISIBLE:
                # everything fine, wait for next check
                sleep(CHECK_INTERVAL)
            elif visibility == UNKNOWN:
                # don't know if visible, try again inmediatly
                pass
        else:
            # server not running, start it and wait for it to appear on lists
            # before doing another check
            start_server()


check_loop()
