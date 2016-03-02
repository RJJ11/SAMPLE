from V1.Models_v1 import Event, SlamDunkScoreBoard
from V1.CollegesAPI_v1 import copyToCollegeFeed
from V1.Models_v1 import CollegeFeed, Post
import time as t
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
from datetime import datetime
from Models_v1 import Profile,Club,Notifications,Club_Creation,Club,MessageResponse
from CollegesAPI_v1 import createCollege
from ClubAPI_v1 import createClub,createClubAfterApproval,approveClub
from EventsAPI_v1 import eventEntry
from PostsAPI_v1 import postEntry


def messageProp(batch,collegeId,data):
       postList = []
       print ("collegeId",collegeId)
       if collegeId == None or collegeId =="":
          college = None
       else:   
          collegeId = ndb.Key('CollegeDb',int(collegeId))
          college = collegeId.get()
       if batch == None or batch == "":
          batch = None

       
       if(college !=None and batch!=None): 
         print "CASE 1"
         print data
         print batch
         print college
         profileList = Profile.query(ndb.AND(Profile.batch == batch,Profile.collegeId == collegeId))  
       elif (college == None and batch == None):
         print "Case 2"
         print data
         print batch
         print college
         print "Entered normal"
         profileList = Profile.query() 
       elif (college != None and batch == None):
         print data
         print batch
         print college
         print "Case 3"
         profileList = Profile.query(Profile.collegeId == collegeId)
       else: 
         print data
         print batch
         print college
         print "Case 4"
         profileList = Profile.query(Profile.batch == batch)
       

       print "Reached"
       print profileList
       for profile in profileList :
           if(profile.gcmId):
              postList.append(profile.gcmId)

       print postList
       gcm_message = GCMMessage(postList, data)
       gcm_conn = GCMConnection()
       gcm_conn.notify_device(gcm_message)


def collegeFeedHelper(request,callFlag,newPost="abcd",editFlag="N"):
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
               if (x.feedType=="Post"):
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
           finalList = []
           for i in xrange(skipCount,upperBound):
               if(i>=len(tempFeed.items)):
                break
               print "TEMPFEED ", tempFeed.items[i]
               finalList.append(tempFeed.items[i])

           cf = CollegeFeed()
           cf.items = finalList
           cf.completed=str(0)
           if(upperBound>=len(tempFeed.items)):
                    cf.completed=str(1)


           return cf
       elif data:
           print "Updating the cache"
           tempFeed = data.items
           pylist2=[]
           tempFeed.append(copyToCollegeFeed(personId,newPost))
           tempFeed.sort(key=lambda x: x.timestamp, reverse=True)

           memData = CollegeFeed()
           memData.items = tempFeed
           memData.completed = str(1)
           memcache.delete("collegeFeed"+request.collegeId)
           memcache.flush_all()
           #time.sleep(10)
           memcache.set(key="collegeFeed"+request.collegeId, value=memData, time=86400)
           return
           #return tempFeed
       else:
           posts = Post.query(Post.collegeId==collegeId).order(-Post.timestamp)
           events = Event.query(Event.collegeId==collegeId).order(-Event.start_time)

       print "TEMP IS NONE"

   else:
       clubId = ndb.Key('Club',int(request.clubId))
       #data = ""
       data = memcache.get('clubFeed'+request.clubId)
       if data and callFlag==1: #called from the API
           print "CALLING FROM MEMCACHE BITCHES"
           tempFeed = data
           for x in tempFeed.items:
               if (x.feedType=="Post"):
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

           finalList = []
           for i in xrange(skipCount,upperBound):
               if(i>=len(tempFeed.items)):
                break
               print "TEMPFEED ", tempFeed.items[i]
               finalList.append(tempFeed.items[i])

           cf = CollegeFeed()
           cf.items = finalList
           cf.completed=str(0)
           if(upperBound>=len(tempFeed.items)):
                    cf.completed=str(1)


           return cf

       elif data:
           print "Updating the cache"
           tempFeed = data.items
           pylist2=[]
           tempFeed.append(copyToCollegeFeed(personId,newPost))
           tempFeed.sort(key=lambda x: x.timestamp, reverse=True)

           memData = CollegeFeed()
           memData.items = tempFeed
           memData.completed = str(1)
           memcache.delete("clubFeed"+request.clubId)
           memcache.flush_all()
           #time.sleep(10)
           memcache.set(key="clubFeed"+request.clubId, value=memData, time=86400)
           return
       else:
        posts = Post.query(Post.club_id==clubId).order(-Post.timestamp)
        events = Event.query(Event.club_id==clubId).order(-Event.start_time)
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

   if newPost == "abcd" and editFlag == "N" :
       print "NEW POST IS NONE"

   elif editFlag == "Y":
       print "Editing"

   else:
       print newPost
       print "NOT NULL"
       print "PYLIST-2 BEFORE "
       print pylist2
       print "BOO"
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
        memcache.set(key="clubFeed"+request.clubId, value=memData, time=86400)
        #return collegeFeedHelper(request,callFlag)
        return cf

       else:    #Called from the cron job which is updating the cache
           memcache.delete("clubFeed"+request.clubId)
           #time.sleep(10)
           memcache.set(key="clubFeed"+request.clubId, value=memData, time=86400)
           return
   else:
       memData = CollegeFeed()
       memData.items = pylist
       memData.completed = str(1)
       #memcache.add(key="collegeFeed"+request.collegeId, value=memData, time=3600)
       if callFlag:
        memcache.set(key="collegeFeed"+request.collegeId, value=memData, time=86400)
        #return collegeFeedHelper(request,callFlag)
        return cf
       else:
           memcache.delete("collegeFeed"+request.collegeId)
           memcache.flush_all()
           #time.sleep(10)
           memcache.set(key="collegeFeed"+request.collegeId, value=memData, time=86400)
           return

def createCollegeHelper(request):
        clubRequest = createCollege(request)
        return None

def createClubRequestHelper(request):
    collegeId = ndb.Key('CollegeDb',int(request.collegeId))
    print("Required College ID",collegeId)

    college_ret = collegeId.get()

    print("College Ret",college_ret)
    if(college_ret):
           club_ret = Club.query(Club.name == request.clubName).filter(Club.abbreviation == request.abbreviation).filter(Club.collegeId == college_ret.key).fetch(1)
           print("Club Ret",club_ret)
           if(len(club_ret) == 0):
              clubRequest = createClub(request)
              currentProfile = clubRequest.to_pid.get()
              newNotif = Notifications(
                     clubName = clubRequest.club_name,
                     clubphotoUrl = clubRequest.photoUrl,
                     #to_pid = clubRequest.to_pid,
                     type = "Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              newNotif.to_pid_list.append(clubRequest.to_pid)

              print("Notification to be inserted in club creation request",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': clubRequest.club_name,"title": "Creation Request",'id':str(clubRequest.key.id()),'type':"Admin"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              #gcm_conn.notify_device(gcm_message)
              print("Finished the clubRequest")


    return None        


def approveClubHelper(request):
  
   clubRequest = ndb.Key('Club_Creation',int(request.reqId))
   action = request.action 
        
   print ("Action is",action)
   req = clubRequest.get()
   currentProfile = req.from_pid.get()
   print("From Pid profile is",currentProfile)
   if (action == 'N'):
            print ("Disapproving request and removing entry")
            print("Request Approval Denied")
            newNotif = Notifications(
                     clubName = req.club_name,
                     clubphotoUrl = req.photoUrl,
                     #to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

            newNotif.to_pid_list.append(req.from_pid)
            print("Notification to be inserted in club approval rejection",newNotif)
            newNotifKey = newNotif.put()
            data = {'message': req.club_name,"title": "Creation Request Denied",'id':"None",'type':"None"}
            print (data)
            gcmId = currentProfile.gcmId
            gcm_message = GCMMessage(gcmId, data)
            gcm_conn = GCMConnection()
            #gcm_conn.notify_device(gcm_message)
            req.key.delete()
        
   elif (req and req.approval_status == "N"):
           status = approveClub(req)
           if(status == "Y"):
              print("Request Approval Granted")
              newClub = createClubAfterApproval(req)
              currentProfile = newClub.admin.get()
              if(newClub):
                  newNotif = Notifications(
                     clubName = newClub.name,
                     clubId = newClub.key,
                     clubphotoUrl = newClub.photoUrl,
                     #to_pid = newClub.admin,
                     type = "Approved Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )
                  newNotif.to_pid_list.append(newClub.admin)

              print("Notification to be inserted in club approval ",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': newClub.name,"title": "Creation Request Approved",
                      'id':str(newClub.key.id()),'type':"Club"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              #gcm_conn.notify_device(gcm_message)
              
              print("The club that has been created is",newClub)
              req.key.delete()
           else:
              print("Request Approval Denied")
              newNotif = Notifications(
                     clubName = req.club_name,
                     clubphotoUrl = req.photoUrl,
                     #to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              newNotif.to_pid_list.append(req.from_pid)

              print("Notification to be inserted in club approval rejection",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': req.club_name,"title": "Creation Request Denied",
                      'id':"None",'type':"None"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              #gcm_conn.notify_device(gcm_message)
              req.key.delete()
            
   return message_types.VoidMessage()


def createEventHelper(request):
        response = MessageResponse()
        print("Entered Event Entry Portion")
        
        try:
            person_key = ndb.Key('Profile',int(request.eventCreator))
            print(person_key)
            profile = person_key.get()
            
            club_key = ndb.Key('Club',int(request.clubId))
            if club_key in profile.clubsJoined:
                    print "GOING INTO EVENTS ENTRY"
                    newEvent = eventEntry(request)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    group = newEvent.club_id.get()
                    groupName = group.name

                    

                    data = {'message': groupName,"title": newEvent.title,
                           'id':str(newEvent.key.id()),'type':"newEvent"}
                    #get the followers of the club pids. Get GCM Id's from those and send
                    print ("GROUP FOLLOWS LIST ", group.follows)

                    eventlist = []
                    if (group.follows):
                        newNotif = Notifications(
                                        clubName = groupName,
                                        clubId = newEvent.club_id,
                                        clubphotoUrl = group.photoUrl,
                                        eventName = newEvent.title,
                                        eventId = newEvent.key,
                                        timestamp = newEvent.timestamp,
                                        type = "Event",
                                        #to_pid = pid
                                        )
                       


                        for pid in group.follows:
                           person = pid.get()
                           newNotif.to_pid_list.append(pid)
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             eventlist.append(gcmId)
                             
                           #newNotif = Notifications(
                           #             clubName = groupName,
                           #             clubId = newEvent.club_id,
                           #             clubphotoUrl = group.photoUrl,
                           #             eventName = newEvent.title,
                           #             eventId = newEvent.key,
                           #             timestamp = newEvent.timestamp,
                           #             type = "Event",
                           #             to_pid = pid
                           #             )
                        print("Notification to be inserted",newNotif)
                        newNotifKey = newNotif.put()

                            
                      
                             
                    
                    print ("Event list is",eventlist)
                    gcm_message = GCMMessage(eventlist, data)
                    gcm_conn = GCMConnection()
                    #gcm_conn.notify_device(gcm_message)
                   
                    print("Should have worked")

            else:
                print "Not Present"
                response.status = "2"
                response.text = "Could not insert"

        except Exception,e:
                print "Error"
                print str(e)
                response.status = "3"
                response.text = "Error"

        return response


def createPostHelper(request):
        response = MessageResponse()
        print("Entered Post Entry Portion")
        flag=0
        try:
            person_key = ndb.Key('Profile',int(request.fromPid))

            profile = person_key.get()
            print(profile)
            club_key = ndb.Key('Club',int(request.clubId))
            if club_key in profile.follows:
                    print "Present"
                    newPost = postEntry(request,flag)

                    print("NEW POST",newPost)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    #Create Notification Feed
                    group = newPost.club_id.get()
                    groupName = group.name
                    data = {'message': groupName,"title": newPost.title,
                            'id':str(newPost.key.id()),'type':"Post"}
                    
                    
                    postlist = []
                    if (group.follows):
                      newNotif = Notifications(
                                      clubName = groupName,
                                      clubId = newPost.club_id,
                                      clubphotoUrl = group.photoUrl,
                                      postName = newPost.title,
                                      postId = newPost.key,
                                      timestamp = newPost.timestamp,
                                      type = "Post",
                                      #to_pid = pid
                                      )
                      for pid in group.follows:
                           person = pid.get()
                           newNotif.to_pid_list.append(pid)
                           print ("PID is",person)
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             postlist.append(gcmId)
                             
                           #newNotif = Notifications(
                           #          clubName = groupName,
                           #           clubId = newPost.club_id,
                           #           clubphotoUrl = group.photoUrl,
                           #           postName = newPost.title,
                           #           postId = newPost.key,
                           #           timestamp = newPost.timestamp,
                           #           type = "Post",
                           #           to_pid = pid
                           #           )

                      print("Notification to be inserted",newNotif)
                      newNotifKey = newNotif.put()  

                           
                    
                    
                    print ("post list is",postlist)
                    gcm_message = GCMMessage(postlist, data)
                    gcm_conn = GCMConnection()
                    #gcm_conn.notify_device(gcm_message)
                   



            else:
                print "Not present"
                clubRequest = postRequest(request)
                response.status = "2"
                response.text = "Inserted into Posts Requests Table"

        except Exception,e:
                print "Error"
                print str(e)
                response.status = "3"
                response.text = "Couldn't insert into Posts Table"



        print("Inserted into the posts table")



        return response


def scoreBoardHelper(request):
       ob = SlamDunkScoreBoard()
       for field in request.all_fields():
            if field.name == "completed":
                if request.completed is None:
                    ob.completed = "N"
                    print "ENTERED HERE"
                else:
                    completed = str(getattr(request,field.name))
                    setattr(ob,field.name,completed.upper())
            else:
                setattr(ob,field.name,getattr(request,field.name))

       flag=0
       query = SlamDunkScoreBoard.query()
       for q in query:
           if (q.team1.upper() == ob.team1.upper() and q.team2.upper() == ob.team2.upper() and q.round.upper() == ob.round.upper()) or (q.team1.upper() == ob.team2.upper() and q.team2.upper() == ob.team1.upper() and q.round.upper() == ob.round.upper()):
               if (q.score1 != ob.score1 or q.score2 != ob.score2):
                q.score1 = ob.score1
                q.score2 = ob.score2
                eventlist = []
                if request.crazy == "Y":
                        if(q.crazy=="C"):

                           eventlist = []
                           dynamicmessage = "Quarter " + str(q.quarter) + " Score : " + str(q.score1) + " : " + str(q.score2) 
                           title = str(q.team1) + " vs " + str(q.team2)
                           data = {'message': dynamicmessage,"title": title,
                                    'id':None,'type':"ScoreBoard"}
                           print "Gonna send GCM"
                           for profile in q.subscribers:
                               person = profile.get()
                               gcmId = person.gcmId
                               if (gcmId):
                                 print ("GCM ID is",gcmId)
                                 eventlist.append(gcmId)
                           print ("Event list is",eventlist)
                           gcm_message = GCMMessage(eventlist, data)
                           gcm_conn = GCMConnection()
                           #gcm_conn.notify_device(gcm_message)
                           print("Should have worked")     

  
                        else:
                           dynamicmessage = "Things are heating up! Stay tuned for live updates "
                           data = {'message': dynamicmessage,"title": "ScoreBoard",
                                    'id':None,'type':"ScoreBoard"}
                           print "Gonna send GCM"
                           for profile in q.subscribers:
                              person = profile.get()
                              gcmId = person.gcmId
                              if (gcmId):
                                 print ("GCM ID is",gcmId)
                                 eventlist.append(gcmId)
                           print ("Event list is",eventlist)
                           gcm_message = GCMMessage(eventlist, data)
                           gcm_conn = GCMConnection()
                           #gcm_conn.notify_device(gcm_message)
                           print("Should have worked") 
                           q.crazy = "C"



               if q.completed!=ob.completed and request.completed is not None:
                q.completed = ob.completed

               if q.quarter != ob.quarter:
                    q.quarter = ob.quarter
                    #Insert GCM HERE
                    eventlist = []
                    dynamicmessage = "End of quarter " + str(q.quarter) + " Score : " + str(q.score1) + " : " + str(q.score2) 
                    title = str(q.team1) + " vs " + str(q.team2)
                    data = {'message': dynamicmessage,"title": title,
                        'id':None,'type':"ScoreBoard"}
                    print "Gonna send GCM"
                    for profile in q.subscribers:
                           person = profile.get()
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             eventlist.append(gcmId)
                    print ("Event list is",eventlist)
                    gcm_message = GCMMessage(eventlist, data)
                    gcm_conn = GCMConnection()
                    #gcm_conn.notify_device(gcm_message)
                    print("Should have worked")

               q.put()
               flag=1

       if flag==0:
           ob.put()

       return message_types.VoidMessage()