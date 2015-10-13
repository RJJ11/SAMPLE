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

        if requestentity:
            print "Begun"
            for field in ('title','description','clubId','venue','date','start_time','attendees','completed','tags','views','isAlumni','event_creator','collegeId'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="clubId"):
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

                    elif field == "date":
                        temp = datetime.strptime(getattr(requestentity,field),"%Y-%m-%d").date()
                        setattr(event_request,field,temp)

                    elif field == "start_time":
                        temp = datetime.strptime(getattr(requestentity,field),"%H:%M:%S").time()
                        setattr(event_request,field,temp)


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

        print("About to create Event")
        print(event_request)
        event_request.put()

        return event_request

def copyEventToForm(event):
        pf = EventForm()
        for field in pf.all_fields():
            if hasattr(event, field.name):
                setattr(pf, field.name, str(getattr(event, field.name)))
            if field.name == 'eventId':
                setattr(pf, field.name, str(event.key.id()))
        return pf

def deleteEvent(request):
        event_id = ndb.Key('Event',int(request.eventId))
        from_pid = ndb.Key('Profile',int(request.from_pid))
        event = event_id.get()
        club_admin = event.clubId.get().admin
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
       pylist = event.attendees
       if(from_pid not in pylist):
        event.attendees.append(from_pid)
        event.put()
       else:
        print "Sorry Already Attending"

       return message_types.VoidMessage