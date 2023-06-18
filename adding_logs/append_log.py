import syslog

syslog.syslog('Sending a log message throuh syslog_module!')


import logging
from systemd import journal

log = logging.getLogger('demo')
log.addHandler(journal.JournaldLogHandler())
log.setLevel(logging.INFO)
log.info("sent to journal")