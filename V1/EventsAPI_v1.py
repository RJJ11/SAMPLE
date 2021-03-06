__author__ = 'rohit'
import endpoints
import logging
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
import datetime as dt
from datetime import datetime,date,time
from Models_v1 import Event,CollegeDb,Profile,Club,EventForm,ModifyEvent,Notifications,PersonalResponse,PersonalInfoResponse
from ProfileAPI_v1 import PersonalInfoForm
from gae_python_gcm.gcm import GCMMessage, GCMConnection
from Models_v1 import GetEventsEitherSideMiniForm,GetEventsESReturnForm,GetEventsResponse
def eventEntry(requestentity=None):

        event_request = Event()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        start = ""
        end = ""
        flag = 0
        profile_key = ""
        if requestentity:
            print "Begun"
            profile_key=ndb.Key('Profile',int(getattr(requestentity,"eventCreator")))
            person = profile_key.get()
            print "Person's email-id ", person.email
            person_collegeId = person.collegeId
            for field in ('title','description','clubId','venue','startTime','endTime','attendees','completed','tags','views','isAlumni','eventCreator','collegeId','timestamp','photo','photoUrl'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="clubId"):
                        club_key=ndb.Key('Club',int(getattr(requestentity,"clubId")))
                        setattr(event_request, 'club_id', club_key)


                    elif(field=="views"):
                        setattr(event_request, field, 0)


                    elif field == "eventCreator":
                        profile_key=ndb.Key('Profile',int(getattr(requestentity,"eventCreator")))
                        person = profile_key.get()
                        print "Person's email-id ", person.email
                        person_collegeId = person.collegeId
                        setattr(event_request, 'event_creator', profile_key)

                    #setattr(event_request, 'from_pid', profile_key)

                    elif field == "startTime":
                        temp = datetime.strptime(getattr(requestentity,"startDate"),"%Y-%m-%d").date()
                        temp1 = datetime.strptime(getattr(requestentity,"startTime"),"%H:%M:%S").time()
                        setattr(event_request,'start_time',datetime.combine(temp,temp1))
                        start = datetime.combine(temp,temp1)

                    elif field == "endTime":
                        temp = datetime.strptime(getattr(requestentity,"endDate"),"%Y-%m-%d").date()
                        temp1 = datetime.strptime(getattr(requestentity,"endTime"),"%H:%M:%S").time()
                        setattr(event_request,'end_time',datetime.combine(temp,temp1))
                        end = datetime.combine(temp,temp1)

                    elif field=="photoUrl" and val == None:
                            setattr(event_request, field, "https://lh3.googleusercontent.com/VLbWVdaJaq2HoYnu6J3T5aKC9DP_ku0KC3eelxawe6sqsPdNTarc5Vc0sx6VGqZ1Y-MlguZNd0plkDEZKYM9OnDbvR2tomX-Kg")

                    #elif field == "end_time":
                     #   temp = datetime.strptime(getattr(requestentity,field),"%H:%M:%S").time()
                      #  setattr(event_request,field,temp)


                    elif field == "attendees":
                        profile_key=ndb.Key('Profile',int(getattr(requestentity,"eventCreator")))
                        pylist = []
                        pylist.append(profile_key)
                        setattr(event_request,field,pylist)


                    elif field == "tags":
                        print("TAGS Value is",val)
                        setattr(event_request, field, val)



                    elif val:
                        print("Value is",val)
                        setattr(event_request, field, str(val))


                elif field == "collegeId":
                    setattr(event_request, field, person_collegeId)

                elif field == "timestamp":
                            temp = datetime.strptime(getattr(requestentity,"date"),"%Y-%m-%d").date()
                            temp1 = datetime.strptime(getattr(requestentity,"time"),"%H:%M:%S").time()
                            setattr(event_request,field,datetime.combine(temp,temp1))


        print("About to create Event")
        print(event_request)
        if(start<end):
            flag=1
            print "SATISFIED"

        if(flag==1):

            event_id= event_request.put()
            print "INSERTED THE EVENT"
            person = profile_key.get()
            list1 = person.eventsAttending
            if list1 == None:
                list2 = []
                list2.append(event_id)
                person.eventsAttending = list2
                person.put()
            else:
                person.eventsAttending.append(event_id)
                person.put()



        return event_request

def copyEventToForm(event,pid):
        pf = EventForm()
        for field in pf.all_fields():
            if hasattr(event, field.name):
                    setattr(pf, field.name, str(getattr(event, field.name)))
            elif field.name == 'startTime':
                    setattr(pf,"startDate", str(event.start_time.strftime("%Y-%m-%d")))
                    setattr(pf, field.name, str(event.start_time.strftime("%H:%M:%S")))
            elif field.name == 'endTime':
                    setattr(pf, "endDate", str(event.end_time.strftime("%Y-%m-%d")))
                    setattr(pf, field.name, str(event.end_time.strftime("%H:%M:%S")))
            elif field.name == "eventCreator":
                    setattr(pf,field.name,str(event.event_creator.get().name))

            elif field.name == "isAttending":
                if pid in event.attendees:
                     setattr(pf,field.name,"Y")
                else:
                    setattr(pf,field.name,"N")
            if field.name == 'eventId':
                setattr(pf, field.name, str(event.key.id()))
            #if field.name == 'date':
            #    setattr(pf, field.name, str(event.timestamp.strftime("%Y-%m-%d")))
            #if field.name == 'time':
            #    setattr(pf, field.name, str(event.timestamp.strftime("%H:%M:%S")))
            if field.name == 'timestamp':
                setattr(pf, field.name, str(event.timestamp))
                        


            if field.name == 'clubphotoUrl':
                print "Reached here-1"
                print event.title
                #print str(post.club_id.get().picture)
                setattr(pf, field.name, event.club_id.get().photoUrl)
            if field.name == 'clubName':
                setattr(pf, field.name, event.club_id.get().name)
            if field.name == 'photoUrl':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(pf, field.name, event.photoUrl)
                
        print pf          
        return pf

def deleteEvent(request):
        event_id = ndb.Key('Event',int(request.eventId))
        from_pid = ndb.Key('Profile',int(request.fromPid))
        try:
            person = from_pid.get()
        except:
            print "Non existent person"

        event = event_id.get()
        club_admin = event.club_id.get().admin
        flag=0
        if (event.event_creator==from_pid or club_admin==from_pid):
            print "Same"
            flag=1
        else:
            print "Different"

        if flag==1:
            event = event_id.get()

            if (len(event.attendees)!=0):
                for x in event.attendees:
                  try:
                    person = x.get()
                    print person.eventsAttending
                    person.eventsAttending.remove(event_id)
                    person.put()
                  except:
                      print "PROFILE NOT AVAILABLE"

            event_id.delete()
            memcache.delete("collegeFeed"+str(event.collegeId.id()))
            memcache.delete("clubFeed"+str(event.club_id.id()))

        return

def attendEvent(request):
       lp = ModifyEvent()
       event_id = ndb.Key('Event',int(request.eventId))
       from_pid = ndb.Key('Profile',int(request.fromPid))

       event = event_id.get()
       person = from_pid.get()
       pylist = event.attendees


       if(from_pid not in pylist):
             
              event.attendees.append(from_pid)
              if person.eventsAttending != None:
                 print "ENTERED HERE"
                 person.eventsAttending.append(event_id)
                 person.put()
                 event.put()

              else:
                 print "Entered the second part"
                 person.eventsAttending = event_id
                 person.put()
                 event.put()
       else:
            print "Sorry Already Attending"

       print ("Event Attendees List",person.eventsAttending)
       memcache.delete("collegeFeed"+str(event.collegeId.id()))
       memcache.delete("clubFeed"+str(event.club_id.id()))

       return message_types.VoidMessage

def getEventsBasedonTimeLeft():
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)
    current  = dt.datetime.now().replace(microsecond = 0)
    #current_utc = current - dt.timedelta(hours =5,minutes=30)
    currentDate = current.date()
    currentTime  = current.time()
    LOG.info("Current time")
    LOG.info(currentTime)
    eventlist = []   
    event_query = Event.query().fetch()
    for event in event_query:
        #LOG.info("Event")
        #LOG.info(event.title)
        #LOG.info(event.start_time)
        start_time_utc = event.start_time - dt.timedelta(hours=5,minutes=30) 
        start_date =  start_time_utc.date()
        diff = start_date - currentDate
        #LOG.info("Considering this event")
        #LOG.info(event.title)
        
        if(diff == dt.timedelta(hours=0) and diff == dt.timedelta(minutes=0) and diff == dt.timedelta(seconds = 0)):
             LOG.info("this event is happening today")
             LOG.info(event.title) 
             start_time = start_time_utc.time()
             FMT = '%H:%M:%S'
             tdelta = datetime.strptime(str(start_time), FMT) - datetime.strptime(str(currentTime), FMT)
             LOG.info("Time delta is")
             LOG.info(tdelta) 

             b = dt.timedelta(days = 0)
             c = dt.timedelta(hours = 2)
             
             if tdelta >= b: 
                LOG.info("made through first part")
                
                if(tdelta<=c):
                    LOG.info(event.title)
                    eventlist.append(event.key)
                    LOG.info("has reached here")
                    LOG.info("Creating notification")
                    group = event.club_id.get()
                    groupName = group.name
                    
                    
                    data = {'message': event.title + "About to start soon","title": groupName,
                            'id':str(event.key.id()),'type':"Event" }
                    LOG.info(data)
                    
                    #get the followers of the club pids. Get GCM Id's from those and send
                    LOG.info("Event attendees list")
                    LOG.info(event.attendees)

                    attendeeslist = []
                    if (event.attendees):
                       newNotif = Notifications(
                                      clubName = groupName,
                                      clubId = event.club_id,
                                      clubphotoUrl = group.photoUrl,
                                      eventName = event.title,
                                      eventId = event.key,
                                      timestamp = dt.datetime.now().replace(microsecond = 0),
                                      type = "Reminder")                                     
                       
                       for pid in event.attendees:
                           person = pid.get()
                           LOG.info("PID is")
                           LOG.info(person)
                           gcmId = person.gcmId
                           
                                      #to_pid = pid)


                           if (gcmId):
                             attendeeslist.append(gcmId)
                             newNotif.to_pid_list.append(pid)
                           #newNotif = Notifications(
                           #           clubName = groupName,
                           #           clubId = event.club_id,
                           #           clubphotoUrl = group.photoUrl,
                           #           eventName = event.title,
                           #           eventId = event.key,
                           #           timestamp = dt.datetime.now().replace(microsecond = 0),
                           #           type = "Reminder",
                           #           to_pid = pid)
                             
                       newNotifKey = newNotif.put()
                    
                    LOG.info("Attendees GCM list is")
                    LOG.info(attendeeslist)
                    gcm_message = GCMMessage(attendeeslist, data)
                    gcm_conn = GCMConnection()
                    gcm_conn.notify_device(gcm_message)
                   
                    LOG.info("Chill")

                else:
                 LOG.info("This event is still some time away from notification") 
             else:
                LOG.info("This event is over")   
    
    LOG.info(eventlist)

def attendeeDetails(eventId):
    event = eventId.get()
    pylist = []
    for p in event.attendees:
        person = p.get()
        x=PersonalInfoForm(person)
        setattr(x,'pid',str(p.id()))
        pylist.append(x)

    return PersonalInfoResponse(items = pylist)


def unAttend(request):
    person = ndb.Key('Profile',int(request.fromPid))
    eventId = ndb.Key('Event',int(request.postId))

    if person not in eventId.get().attendees:
        return
    else:
        event = eventId.get()

        event.attendees.remove(person)
        event.put()

        p = person.get()
        p.eventsAttending.remove(eventId)
        p.put()

    return

def editEventFn(request,event):
    event.title = request.title
    event.description = request.description
    event.photoUrl = request.photoUrl
    event.venue = request.venue


    temp = datetime.strptime(getattr(request,"date"),"%Y-%m-%d").date()
    temp1 = datetime.strptime(getattr(request,"time"),"%H:%M:%S").time()

    event.timestamp = datetime.combine(temp,temp1)

    temp = datetime.strptime(getattr(request,"startDate"),"%Y-%m-%d").date()
    temp1 = datetime.strptime(getattr(request,"startTime"),"%H:%M:%S").time()
    start = datetime.combine(temp,temp1)
    event.start_time = start


    temp = datetime.strptime(getattr(request,"endDate"),"%Y-%m-%d").date()
    temp1 = datetime.strptime(getattr(request,"endTime"),"%H:%M:%S").time()
    end = datetime.combine(temp,temp1)
    event.end_time = end


    key1 = event.put()
    return event
def getEventsEitherSide(request):
    
    timestamp = request.timestamp
    collegeId = request.collegeId

    timestampdatetime = dt.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    upperbound = timestampdatetime + dt.timedelta(hours=12)
    lowerbound = timestampdatetime - dt.timedelta(hours=12)


    print timestampdatetime
    print upperbound
    print lowerbound
    college_key = ndb.Key('CollegeDb',int(collegeId))
    print college_key

    eventlist = Event.query(Event.collegeId == college_key)
    newList = []
    print eventlist

    for event in eventlist:
        start_datetime = event.start_time + dt.timedelta(hours=5,minutes=30)
        #print "Considering"
        #print event.title
        #print start_datetime 
        if(start_datetime>=lowerbound and start_datetime<=upperbound):
            newList.append(event)

    #eventlist2 = Event.query(ndb.AND(Event.collegeId == college_key, ndb.OR(Event.completed == "N",Event.completed == "No"))).fetch()
    #print eventlist2

    for event in eventlist:
        if(event.completed == "N" or event.completed == "No") : 
            start_datetime = event.start_time + dt.timedelta(hours=5,minutes=30)
            if(start_datetime<=timestampdatetime):
               print event.completed
               if event not in newList:
                  newList.append(event) 
    newList.sort(key=lambda x: x.start_time)
    
    finallist = []
    for x in newList:
        returnobj = GetEventsESReturnForm()
        returnobj.name = str(x.title)
        returnobj.startTime = str(x.start_time)
        returnobj.collegeId = str(x.collegeId)
        returnobj.status = str(x.completed)
        finallist.append(returnobj)
  
    

    return GetEventsResponse(items=finallist)        

def changeStatusCompletedEvents():
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)
    current  = dt.datetime.now().replace(microsecond = 0)
    current_utc = current + dt.timedelta(hours =5,minutes=30)
    currentDate = current.date()
    currentTime  = current.time()
    LOG.info("Current datetime")
    LOG.info(current_utc)
    eventlist = []   
    event_query = Event.query(ndb.OR(Event.completed == "N",Event.completed == "No")).fetch()
    for event in event_query:
        LOG.info("Event")
        LOG.info(event.title)
        end_datetime = event.end_time + dt.timedelta(hours =5,minutes=30)
        LOG.info(end_datetime)
        LOG.info(event.completed)
        
        if(end_datetime<=current_utc): #event has been completed
           event.completed = "Yes"
           event.put()