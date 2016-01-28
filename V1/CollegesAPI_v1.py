__author__ = 'rohit'
from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import GetCollege,CollegeDb,Event,Profile,Feed,Post

def createCollege(requestentity=None):

        newCollege = CollegeDb()
        query = CollegeDb.query()
        print "The data got on querying is " , query , " type is ", type(query), "\n"
        count = 0
        names = []
        location = []

        """profile =  Profile(name = 'RJJ',
                            email = 'rohitjjoseph@gmail.com',
                            phone = '7760532293',
                            password = '13211',
                            pid = '1234',
                            isAlumni='N',
                            collegeId= 'NIoTK')
        profile_key = profile.put()
        """

        for records in query:
           print"The name of the college is ", records.name , " and location is " , records.location
           names.append(records.name)
           location.append(records.location)
           count += 1
           #print "\n"

        print "count is, " , count

        collegeName = ""
        if requestentity:
            for field in ('name','abbreviation','location','student_sup','alumni_sup','email'):
                val = getattr(requestentity, field)
                if field == "name":
                    collegeName = getattr(requestentity, field).strip()
                if val:
                    val = val.strip()
                    print("Value is",val)
                    setattr(newCollege, field, str(val))
            #Now setting the attributes not recieved from the front-end.
            setattr(newCollege, 'student_count', 0)
            setattr(newCollege, 'group_count', 0)
            newlist = []
            setattr(newCollege, 'group_list', newlist)
            setattr(newCollege,'sup_emailId',requestentity.email)
            # Making CollegeId
            newString = ""
            newString = collegeName[0]
            for x in xrange(len(collegeName)):
                if(collegeName[x]==' '):
                    newString+=collegeName[x+1]

            setattr(newCollege, 'collegeId', newString)

        print(newCollege)
        flag = 0
        for var in xrange(count):
            if(newCollege.name==names[var] and newCollege.location==location[var]):
                flag=1

        if(flag):
            print "Sorry already existing record"

        else:
            print "Unique"
            email = getattr(requestentity, "email")
            phone = getattr(requestentity, "phone")
            if(getattr(requestentity, "student_sup")==None):
                isAlumni = "Yes"
                person_name = getattr(requestentity, "alumni_sup")
            else:
                isAlumni = "No"
                person_name = getattr(requestentity, "student_sup")

            collegeId = newCollege.put()
            profile =  Profile(name = person_name ,
                            email = email,
                            phone = phone,
                            isAlumni=isAlumni,
                            collegeId= collegeId)
            profile.superadmin.append(collegeId)
            key1 = profile.put()
            return newCollege



def getColleges(college):
    gc = GetCollege()
    print "THe ID IS"
    print college.key.id()
    for field in gc.all_fields():
        if hasattr(college, field.name):
            setattr(gc, field.name, str(getattr(college, field.name)))

        if field.name == 'collegeId':
            setattr(gc, field.name, str(college.key.id()))


    return gc


def copyToCollegeFeed(entity):
    feed = Feed()
    for field in feed.all_fields():
        if hasattr(entity, field.name):
                if field.name == 'start_time':
                    print field.name
                    setattr(feed,"start_date", str(entity.start_time.strftime("%Y-%m-%d")))
                    setattr(feed, field.name, str(entity.start_time.strftime("%H:%M:%S")))
                elif field.name == 'end_time':
                    print field.name
                    setattr(feed, "end_date", str(entity.end_time.strftime("%Y-%m-%d")))
                    setattr(feed, field.name, str(entity.end_time.strftime("%H:%M:%S")))
                elif field.name == 'club_name':
                    print "field name" + field.name
                    setattr(feed, field.name, entity.club_id.get().name)
                elif field.name == 'club_id':
                    setattr(feed, field.name, str(entity.club_id.id()))

                elif field.name == 'collegeId':
                    print field.name
                    setattr(feed, field.name, entity.collegeId.get().name)

                elif (field.name=='event_creator'):
                    print field.name
                    setattr(feed, field.name, entity.event_creator.get().name)
                elif (field.name=='likers'):
                    print field.name
                    pylist=[]
                    for key in entity.likers:
                        pylist.append(key.get().name)
                    setattr(feed, field.name, pylist)

                elif (field.name=='attendees'):
                    print field.name
                    pylist=[]
                    print entity.title
                    for key in entity.attendees:
                        pylist.append(key.get().name)
                    setattr(feed, field.name, pylist)

                else:
                    setattr(feed, field.name, str(getattr(entity, field.name)))

        elif (field.name=='id'):
            print field.name
            setattr(feed, field.name, str(entity.key.id()))

        elif (field.name=='event_creator'):
            print field.name
            setattr(feed, field.name, entity.from_pid.get().name)


        elif field.name == 'clubphotoUrl':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(feed, field.name, entity.club_id.get().photoUrl)
        elif field.name == 'club_name':
                print "field name" + field.name
                setattr(feed, field.name, entity.club_id.get().name)
        elif field.name == 'club_id':
                setattr(feed, field.name, str(entity.club_id.id()))
        elif field.name == 'clubabbreviation':
                setattr(feed, field.name, entity.club_id.get().abbreviation)

        """
        elif field.name == 'date':
                setattr(feed, field.name, str(entity.timestamp.strftime("%Y-%m-%d")))
        elif field.name == 'time':
                setattr(feed, field.name, str(entity.timestamp.strftime("%H:%M:%S")))
        """
    return feed

"""
def copyToCollegeFeed(entity):
    feed = Feed()
    for field in feed.all_fields():
        if hasattr(entity, field.name):
                if field.name == 'start_time':
                    print field.name
                    setattr(feed,"start_date", str(entity.start_time.strftime("%Y-%m-%d")))
                    setattr(feed, field.name, str(entity.start_time.strftime("%H:%M:%S")))
                elif field.name == 'end_time':
                    print field.name
                    setattr(feed, "end_date", str(entity.end_time.strftime("%Y-%m-%d")))
                    setattr(feed, field.name, str(entity.end_time.strftime("%H:%M:%S")))
                elif field.name == 'club_id':
                    print field.name
                    setattr(feed, field.name, entity.club_id.get().name)
                elif field.name == 'collegeId':
                    print field.name
                    setattr(feed, field.name, entity.collegeId.get().name)
                elif (field.name=='event_creator'):
                    print field.name
                    setattr(feed, field.name, entity.event_creator.get().name)
                elif (field.name=='likers'):
                    print field.name
                    pylist=[]
                    for key in entity.likers:
                        pylist.append(key.get().name)
                    setattr(feed, field.name, pylist)
                elif (field.name=='attendees'):
                    print field.name
                    pylist=[]
                    for key in entity.attendees:
                        pylist.append(key.get().name)
                    setattr(feed, field.name, pylist)
                else:
                    setattr(feed, field.name, str(getattr(entity, field.name)))
        elif (field.name=='pid'):
            print field.name
            setattr(feed, field.name, str(entity.key.id()))
        elif (field.name=='event_creator'):
            print field.name
            setattr(feed, field.name, entity.from_pid.get().name)
        if field.name == 'clubphoto':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(feed, field.name, entity.club_id.get().picture)
        """
#        elif field.name == 'date':
#                setattr(feed, field.name, str(entity.timestamp.strftime("%Y-%m-%d")))
#        elif field.name == 'time':
#                setattr(feed, field.name, str(entity.timestamp.strftime("%H:%M:%S")))
#        """

#    return feed
#"""