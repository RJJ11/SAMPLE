from V1.Models_v1 import Event
from V1.CollegesAPI_v1 import copyToCollegeFeed
from V1.Models_v1 import CollegeFeed, Post
import time
__author__ = 'rohit'
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


def collegeFeedHelper(request,callFlag,newPost="abcd"):
   print "Entered the Like Posts Section"
   temp = request.clubId
   flagclub =0 #To see which parameter is called and set cache accordingly
   personId = ndb.Key('Profile',int(request.pid))
   flag =0
   pageLimit = 10
   skipCount=0
   upperBound=pageLimit
   print request.pageNumber



   try:
    skipCount = (int(request.pageNumber)-1)*pageLimit
    upperBound = int(request.pageNumber)*pageLimit

   except:
      print "Didnt give pageNumber-Default to 1"

   if request.date != None:
    date = datetime.strptime(getattr(request,"date"),"%Y-%m-%d").date()
    flag = 1
   #print "TYPE-DATE", type(date)
   if (temp==None):
       collegeId = ndb.Key('CollegeDb',int(request.collegeId))
       #data = ""
       data = memcache.get('collegeFeed'+request.collegeId)
       if data and callFlag==1: #called from the API
           print "CALLING FROM MEMCACHE BITCHES"
           tempFeed = data
           for x in tempFeed.items:
               if hasattr(x,"likers"):
                    print "FOUND LIKES IN" , x.title
                    if request.pid in x.likersList:
                        x.hasLiked = "Y"
                    else:
                        x.hasLiked = "N"

                    x.likersList=[]
               if hasattr(x,"attendees"):
                   if request.pid in x.attendeeList:
                        x.isAttending = "Y"
                   else:
                        x.isAttending = "N"
                   x.attendeeList=[]

               """if x.feedType == "Post":
                   delattr(x,"isAttending")

               if x.feedType == "Event":
                   delattr(x,"hasLiked")
               """

           return tempFeed
       else:
           posts = Post.query(Post.collegeId==collegeId).order(-Post.timestamp)
           events = Event.query(Event.collegeId==collegeId).order(-Event.timestamp)
       print "TEMP IS NONE"

   else:
       clubId = ndb.Key('Club',int(request.clubId))
       #data = ""
       data = memcache.get('clubFeed'+request.clubId)
       if data and callFlag==1: #called from the API
           print "CALLING FROM MEMCACHE BITCHES"
           tempFeed = data
           for x in tempFeed.items:
               if hasattr(x,"likers"):
                    print "FOUND LIKES IN" , x.title
                    if x.likersList:
                        print "Reached here"
                        if request.pid in x.likersList:
                            x.hasLiked = "Y"
                        else:
                            x.hasLiked = "N"

                        x.likersList=[]
                        print "moving on"
               if hasattr(x,"attendees"):
                   print "Attendee List ->"
                   print x.attendeeList
                   if x.attendeeList:
                       if request.pid in x.attendeeList:
                            x.isAttending = "Y"
                       else:
                            x.isAttending = "N"
                       x.attendeeList=[]

               """if x.feedType == "Post":
                   delattr(x,"isAttending")

               if x.feedType == "Event":
                   delattr(x,"hasLiked")
               """
           return tempFeed
       else:
        posts = Post.query(Post.club_id==clubId).order(-Post.timestamp)
        events = Event.query(Event.club_id==clubId).order(-Event.timestamp)
        flagclub=1      #INDICATING THAT A CALL HAS BEEN MADE WITH CLUB AND NOT COLLEGE ID

   print events
   #CollegeFeed(items=[copyEventToForm(x) for x in posts])
   #CollegeFeed(items=[copyEventToForm(x) for x in events])
   #pylist = [copyToCollegeFeed(x) for x in events]
   pylist=[]
   for x in events:
       print "TImestamp",type(x.timestamp.strftime("%Y-%m-%d"))
       if flag==1:
        if x.timestamp.strftime("%Y-%m-%d") == str(date):
            pylist.append(copyToCollegeFeed(personId,x))
       else:
           pylist.append(copyToCollegeFeed(personId,x))
   print "SO FAR",pylist
   pylist2 = []
   for x in posts:
       print "NOW IN POSTS"
       print x
       print "TImestamp",type(x.timestamp.strftime("%Y-%m-%d"))
       if flag==1:
        if x.timestamp.strftime("%Y-%m-%d") == str(date):
            pylist2.append(copyToCollegeFeed(personId,x))
       else:
           pylist2.append(copyToCollegeFeed(personId,x))

   # ADDING THE NEW POST/EVENT THAT DOESN'T GET ADDED DUE TO LATENCY ISSUES

   if newPost == "abcd":
       print "NEW POST IS NONE"
   else:
       print newPost
       print "NOT NULL"
       #freshPost = newPost.get()
       pylist2.append(copyToCollegeFeed(personId,newPost))


   print pylist2
   #pylist2 = [copyToCollegeFeed(x) for x in posts]
   pylist+=pylist2
   #pylist.append(copyToCollegeFeed(x) for x in events)
   pylist.sort(key=lambda x: x.timestamp, reverse=True)
   #print pylist[1].timestamp
   #print pylist
   #CollegeFeed(items=pylist)
   #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
   #return CollegeFeed(items=pylist)

   finalList = []
   for i in xrange(skipCount,upperBound):
       if(i>=len(pylist)):
        break
       finalList.append(pylist[i])

   cf = CollegeFeed()
   cf.items = finalList
   cf.completed=str(0)
   if(upperBound>=len(pylist)):
            cf.completed=str(1)
   #print pylist[1].timestamp
   #print pylist
   #return cf
   CollegeFeed(items=finalList)
   if flagclub:
       memData = CollegeFeed()
       memData.items = pylist
       memData.completed = str(1)
       #memcache.add(key="clubFeed"+request.clubId, value=memData, time=3600)
       if callFlag: #This implies that it has been called from the endpoints api and should therefore return a response
        memcache.add(key="clubFeed"+request.clubId, value=memData, time=3600)
        return collegeFeedHelper(request,callFlag)
       else:    #Called from the cron job which is updating the cache
           memcache.delete("clubFeed"+request.clubId)
           #time.sleep(10)
           memcache.add(key="clubFeed"+request.clubId, value=memData, time=3600)
           return
   else:
       memData = CollegeFeed()
       memData.items = pylist
       memData.completed = str(1)
       #memcache.add(key="collegeFeed"+request.collegeId, value=memData, time=3600)
       if callFlag:
        memcache.add(key="collegeFeed"+request.collegeId, value=memData, time=3600)
        return collegeFeedHelper(request,callFlag)
       else:
           memcache.delete("collegeFeed"+request.collegeId)
           #time.sleep(10)
           memcache.add(key="collegeFeed"+request.collegeId, value=memData, time=3600)
           return


