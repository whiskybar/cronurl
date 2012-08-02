import sys
import time
import signal
import argparse
import os.path
import eventlet
from eventlet.timeout import Timeout
from eventlet.green import urllib2
from email.mime.text import MIMEText
from eventlet.green import subprocess
import MySQLdb
import logging
import logging.handlers
from crontab import CronTab


def scheduled_urls():
    connection = MySQLdb.connect(read_default_file=os.path.expanduser('~/.my.cnf'), db='hosting')
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cron')
    for row in cursor:
        entry = CronTab('%(min)s %(hour)s %(day)s %(month)s %(dayofweek)s' % row)
        if entry.next() < 60:
            yield 'http://%(domain)s%(script)s' % row, row['lifetime'], row['mailto']
    connection.close()

def email(mailto, subject, body):
    message = MIMEText(body)
    message['From'] = 'cron@tele3.cz'
    message['To'] = mailto or 'jbar@tele3.cz'
    message['Subject'] = subject
    process = subprocess.Popen(['/usr/sbin/sendmail', '-t'], stdin=subprocess.subprocess_orig.PIPE)
    process.communicate(message.as_string())


def check_url(url, timeout, mailto):
    result = None
    with Timeout(timeout, False):
        try:
            result = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            logging.error('%s returned %s', url, e.code)
        except urllib2.URLError, e:
            logging.error('%s failed: %s', url, e.reason)
        except Exception, e:
            logging.error('%s fatal: %s', url, e)
    logging.debug('%s hit', url)
    if result is None:
        logging.warning('%s timed out after %d seconds', url, timeout)
        email(mailto, '[CRON] %s timed out' % url, '%s timed out after %d seconds' % (url, timeout))
    else:
        email(mailto, '[CRON] %s' % url, result)
               
def parse_arguments():
    parser = argparse.ArgumentParser(description='Start a cronurl daemon')
    parser.add_argument('-d', '--debug', default=False, action='store_true', help='debug mode on')
    return parser.parse_args()
    
def shutdown(signal, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    options = parse_arguments()
    if options.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(format='%(asctime)s %(message)s', level=level)
    rh = logging.handlers.TimedRotatingFileHandler(
        filename='/var/log/hosting/cronurl.log',
        when='midnight',
    )
    rh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    rootLogger = logging.getLogger('')
    rootLogger.removeHandler(rootLogger.handlers[0])
    rootLogger.setLevel(logging.DEBUG)
    rootLogger.addHandler(rh)

    while True:
        now = time.time()
        next_minute = int(now) / 60 * 60 - now + 61
        for url, timeout, mailto in scheduled_urls():
            eventlet.spawn_after(next_minute, check_url, url, timeout, mailto)
        eventlet.sleep(next_minute + 1)

if __name__ == '__main__':
    main()

