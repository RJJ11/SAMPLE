__author__ = 'rohit'
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Event_Request,CollegeDb,Profile,Club

def eventEntry(self, requestentity=None):

        event_request = Event_Request()
        college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        college_key = college.put()
        query = CollegeDb.query()
        profile =  Profile(name = 'RJJ',
                            email = 'rohitjjoseph@gmail.com',
                            phone = '7760532293',
                            password = '13211',
                            pid = '1234',
                            isAlumni='N',
                            collegeId= college_key)
        profile_key = profile.put()
        newClub = Club()
        newClub.abbreviation = "fngjnfjdv"
        newClub.clubId = "erfrgty"
        newClub.admin = profile_key
        newClub.collegeId = college_key
        newClub.name = "BLAH"
        newClub.isAlumni = "Yes"

        club_key=newClub.put()
        print("Finished frompid")
                    #setattr(clubRequest, field, profile_key)


        if requestentity:
            for field in ('title','description','clubId','eventId','venue','date','start_time','end_time','attendees','completed','views','isAlumni','event_creator','collegeId'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="clubId"):
                        setattr(event_request, field, club_key)

                    elif(field=="views"):
                        val = getattr(requestentity,field)
                        temp = int(str(val))
                        setattr(event_request, field, temp)

                    elif val:
                        print("Value is",val)
                        setattr(event_request, field, str(val))



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
                    person = profile_key.get()
                    print "Person's email-id ", person.email
                    person_collegeId = person.collegeId
                    print "His college Id ", person.collegeId
                    college_details = person_collegeId.get()
                    print "The sup is ", college_details.student_sup
                    print("Finished to-pid")

                    setattr(event_request, field, profile_key)
                    #setattr(event_request, 'from_pid', profile_key)
                elif field == "eventId":
                    setattr(event_request, field, "ABCDXYZ")
                elif field == "collegeId":
                    setattr(event_request, field, person_collegeId)

        print("About to createClubRequest")
        print(event_request)
        event_request.put()

        return event_request