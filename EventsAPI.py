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
from Models import Event,CollegeDb,Profile,Club,EventForm,ModifyEvent,Notifications
from gae_python_gcm.gcm import GCMMessage, GCMConnection
def eventEntry(requestentity=None):

        event_request = Event()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        start = ""
        end = ""
        flag = 0
        if requestentity:
            print "Begun"
            for field in ('title','description','club_id','venue','start_time','end_time','attendees','completed','tags','views','isAlumni','event_creator','collegeId','timestamp','photo','photoUrl'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="club_id"):
                        club_key=ndb.Key('Club',int(getattr(requestentity,field)))
                        setattr(event_request, field, club_key)


                    elif(field=="views"):
                        setattr(event_request, field, 0)


                    elif field == "event_creator":
                        profile_key=ndb.Key('Profile',int(getattr(requestentity,field)))
                        person = profile_key.get()
                        print "Person's email-id ", person.email
                        person_collegeId = person.collegeId
                        setattr(event_request, field, profile_key)

                    #setattr(event_request, 'from_pid', profile_key)

                    elif field == "start_time":
                        temp = datetime.strptime(getattr(requestentity,"start_date"),"%Y-%m-%d").date()
                        temp1 = datetime.strptime(getattr(requestentity,field),"%H:%M:%S").time()
                        setattr(event_request,field,datetime.combine(temp,temp1))
                        start = datetime.combine(temp,temp1)

                    elif field == "end_time":
                        temp = datetime.strptime(getattr(requestentity,"end_date"),"%Y-%m-%d").date()
                        temp1 = datetime.strptime(getattr(requestentity,field),"%H:%M:%S").time()
                        setattr(event_request,field,datetime.combine(temp,temp1))
                        end = datetime.combine(temp,temp1)

                    #elif field == "end_time":
                     #   temp = datetime.strptime(getattr(requestentity,field),"%H:%M:%S").time()
                      #  setattr(event_request,field,temp)


                    elif field == "attendees":
                        profile_key=ndb.Key('Profile',int(getattr(requestentity,"event_creator")))
                        pylist = []
                        pylist.append(profile_key)
                        setattr(event_request,field,pylist)

                    elif field == "tags":
                        if (requestentity,field == "None"):
                            continue
                        pylist = getattr(requestentity,field).split(",")
                        length = len(pylist)
                        i = 0
                        newlist = []
                        while(i<length):
                            newlist.append(pylist[i])
                            i = i+1

                        setattr(event_request,field,newlist)

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

        if(flag==1):

            event_request.put()

        return event_request

def copyEventToForm(event):
        pf = EventForm()
        for field in pf.all_fields():
            if hasattr(event, field.name):
                if field.name == 'start_time':
                    setattr(pf,"start_date", str(event.start_time.strftime("%Y-%m-%d")))
                    setattr(pf, field.name, str(event.start_time.strftime("%H:%M:%S")))
                elif field.name == 'end_time':
                    setattr(pf, "end_date", str(event.end_time.strftime("%Y-%m-%d")))
                    setattr(pf, field.name, str(event.end_time.strftime("%H:%M:%S")))
                else:
                    setattr(pf, field.name, str(getattr(event, field.name)))
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
            if field.name == 'club_name':
                setattr(pf, field.name, event.club_id.get().name)
            if field.name == 'photoUrl':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(pf, field.name, event.photoUrl)
                
        print pf          
        return pf

def deleteEvent(request):
        event_id = ndb.Key('Event',int(request.eventId))
        from_pid = ndb.Key('Profile',int(request.from_pid))
        event = event_id.get()
        club_admin = event.club_id.get().admin
        flag=0
        if (event.event_creator==from_pid or club_admin==from_pid):
            print "Same"
            flag=1
        else:
            print "Different"

        if flag==1:
            event_id.delete()

        return

def attendEvent(request):
       lp = ModifyEvent()
       event_id = ndb.Key('Event',int(request.eventId))
       from_pid = ndb.Key('Profile',int(request.from_pid))
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
        LOG.info("Event")
        LOG.info(event.title)
        LOG.info(event.start_time)
        start_time_utc = event.start_time - dt.timedelta(hours=5,minutes=30) 
        start_date =  start_time_utc.date()
        diff = start_date - currentDate
        LOG.info("Considering this event")
        LOG.info(event.title)
        
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
                    
                    
                    data = {'message': event.title + "About to start soon","title": groupName }
                    LOG.info(data)
                    
                    #get the followers of the club pids. Get GCM Id's from those and send
                    LOG.info("Event attendees list")
                    LOG.info(event.attendees)

                    attendeeslist = []
                    if (event.attendees):
                                                            
                       for pid in event.attendees:
                           person = pid.get()
                           LOG.info("PID is")
                           LOG.info(person)
                           gcmId = person.gcmId
                           


                           if (gcmId):
                             attendeeslist.append(gcmId)
                           newNotif = Notifications(
                                      clubName = groupName,
                                      clubId = event.club_id,
                                      clubphotoUrl = group.photoUrl,
                                      eventName = event.title,
                                      eventId = event.key,
                                      timestamp = dt.datetime.now().replace(microsecond = 0),
                                      type = "Reminder",
                                      to_pid = pid)  
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
