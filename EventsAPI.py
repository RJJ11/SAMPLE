__author__ = 'rohit'
import endpoints
from datetime import datetime,date,time
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Event,CollegeDb,Profile,Club,EventForm,ModifyEvent

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
            for field in ('title','description','club_id','venue','start_time','end_time','attendees','completed','tags','views','isAlumni','event_creator','collegeId','timestamp'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="club_id"):
                        club_key=ndb.Key('Club',int(getattr(requestentity,field)))
                        setattr(event_request, field, club_key)


                    elif(field=="views"):
                        setattr(event_request, field, 0)


                    elif field == "event_creator":
                        """profile =  Profile(
                               name = 'SiddharthRec',
                               email = 'sid.tiger183@gmail.com',
                               phone = '7760531994',
                               password = '1803mutd',
                               pid = '5678',
                               isAlumni='N',
                               collegeId=college_key
                               )
                        profile_key = profile.put()"""
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
            if field.name == 'date':
                setattr(pf, field.name, str(event.timestamp.strftime("%Y-%m-%d")))
            if field.name == 'time':
                setattr(pf, field.name, str(event.timestamp.strftime("%H:%M:%S")))
            if field.name == 'clubphoto':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(pf, field.name, event.club_id.get().picture)
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
        person.eventsAttending.append(event_id)
        person.put()
        event.put()
       else:
        print "Sorry Already Attending"

       return message_types.VoidMessage