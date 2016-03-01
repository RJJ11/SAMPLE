from EventsAPI_v1 import getEventsBasedonTimeLeft,changeStatusCompletedEvents
import logging
import datetime


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)
LOG.info("Entered the Cron")
getEventsBasedonTimeLeft()#fill with current time later

LOG.info("Dealing with already completed events")
changeStatusCompletedEvents()