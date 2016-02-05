from datetime import datetime
import endpoints
import datetime as dt
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from datetime import datetime,date,time
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from gae_python_gcm.gcm import GCMMessage, GCMConnection
from Models_v1 import Profile

def messageProp(batch,data):
       postList = []
       if(batch!=None):
          print data
          print batch
          print "Entered batchRequest"
          profileList = Profile.query(Profile.batch == batch)
       else:
          print data
          print "Entered normal"
          profileList = Profile.query()   

       for profile in profileList :
           if(profile.gcmId):
              postList.append(profile.gcmId) 

       print postList
       gcm_message = GCMMessage(postList, data)
       gcm_conn = GCMConnection()
       gcm_conn.notify_device(gcm_message)
