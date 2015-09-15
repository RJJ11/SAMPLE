from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models import ClubRequestMiniForm
from Models import Club
from Models import Club_Creation
from Models import Profile
from Models import CollegeDb
from Models import CollegeDbMiniForm
from Models import ClubMiniForm
EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

@endpoints.api(name='clubs', version='v1', 
    allowed_client_ids=[API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE])

class ClubApi(remote.Service):
   
   
   def createClub(self,requestentity=None):
        
        #When createClubRequest is called  


        clubRequest = Club_Creation()
        college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        college_key = college.put()






        if requestentity:
            for field in ('abbreviation','club_name','from_pid','to_pid','club_id','isAlumni','collegeId','club_creation_id'):
                if hasattr(requestentity, field):
                    val = getattr(requestentity, field)
                    if val:
                        setattr(clubRequest, field, str(val))
                elif field == "from_pid":
                    profile =  Profile(
                            name = 'SiddharthSend',
                            email = 'sid.tiger184@gmail.com',
                            phone = '7760531993',
                            password = '1803mutd1',
                            pid = '1234',
                            isAlumni='N',
                            collegeId=college_key

                            )
                    profile_key = profile.put()
                    #print("Finished frompid")
                    setattr(clubRequest, field, profile_key)
                  

                elif field == "to_pid":
                    profile =  Profile(
                               name = 'SiddharthRec',
                               email = 'sid.tiger183@gmail.com',
                               phone = '7760531994',
                               password = '1803mutd',
                               pid = '5678',
                               isAlumni='N',
                               collegeId=college_key

                               )
                    profile_key = profile.put()

                    setattr(clubRequest, field, profile_key)
                elif field == "club_id":
                    setattr(clubRequest, field, "9999")
                elif field == "isAlumni":
                    setattr(clubRequest, field, "N")
                elif field == "collegeId":
                    setattr(clubRequest, field, college_key)
                elif field == "club_creation_id":
                    setattr(clubRequest, field, "1")
                
        #print(clubRequest)
        clubRequest.put()
        
        return clubRequest


   def createClubAfterApproval(self,requestentity=None):

        if requestentity:
            newClub = Club()
            newClub.abbreviation = requestentity.abbreviation
            newClub.clubId = requestentity.club_id
            newClub.admin = requestentity.from_pid
            newClub.collegeId = requestentity.collegeId
            newClub.name = requestentity.club_name
            newClub.isAlumni = requestentity.isAlumni

            newClub.put()
        return newClub

   @endpoints.method(ClubRequestMiniForm,ClubMiniForm,path='getClub', http_method='POST', name='getClub')
   def getClub(self,requestentity=None):

        print("Request entity is",requestentity)

        if requestentity:


            clubQuery = Club.query(Club.name == requestentity.name).filter(Club.abbreviation == requestentity.abbreviation).fetch(1)
            print(clubQuery)

            if clubQuery:
             college = CollegeDb.query(CollegeDb.collegeId == requestentity.collegeId.get().collegeId).fetch(1)
             profile = Profile.query(Profile.pid == requestentity.admin.get().pid).fetch(1)
             retClub = ClubMiniForm()
             retClub.clubId = requestentity.clubId
             retClub.admin = profile[0].name
             retClub.abbreviation = requestentity.abbreviation
             retClub.name = requestentity.name
             retClub.collegeName = college[0].name



        return retClub





   def createCollege(self, requestentity=None):
        
        newCollege = CollegeDb()
        query = CollegeDb.query()
        print "The data got on querying is " , query , " type is ", type(query), "\n"
        count = 0
        names = []
        location = []       
        
        for records in query:
           print"The name of the college is ", records.name , " and location is " , records.location
           names.append(records.name)
           location.append(records.location)
           count += 1
           print "\n"
        
        print "count is, " , count        
        
        collegeName = ""
        if requestentity:
            for field in ('name','abbreviation','location','student_sup','alumni_sup'):
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
            """ Making CollegeId"""
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
            newCollege.put()
        
        return newCollege
    
                




   @endpoints.method(ClubRequestMiniForm,ClubMiniForm,path='club', http_method='POST', name='createClubRequest')
   def createClubRequest(self, request):
        clubRequest = self.createClub(request)
        #insert logic for request approval
        newClub = self.createClubAfterApproval(clubRequest)
        retClub = self.getClub(newClub)
        return retClub


   @endpoints.method(CollegeDbMiniForm,message_types.VoidMessage,path='collegeDB', http_method='POST', name='createCollege')
   def createCollegeDb(self, request):
        print("Entered CollegeDb Portion")
        clubRequest = self.createCollege(request)
        print("Finished entering a college")     
        





api = endpoints.api_server([ClubApi]) # register API	