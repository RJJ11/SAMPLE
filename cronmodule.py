from EventsAPI import getEventsBasedonTimeLeft
import logging
import datetime


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)
LOG.info("Entered the Cron")
getEventsBasedonTimeLeft()#fill with current time later

