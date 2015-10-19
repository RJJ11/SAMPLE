__author__ = 'rohit'
from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import GetCollege,CollegeDb,Event,Profile

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
            profile.put()

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
