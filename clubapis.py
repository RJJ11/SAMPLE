from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models import ClubRequestMiniForm, PostMiniForm,Colleges, Posts, GetAllPosts
from Models import Club, Post_Request, Post, Event_Request, PostForm
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

# GETSTREAM KEY - urgm3xjebe9d

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

   def postRequest(self, requestentity=None):

        post_request = Post_Request()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        key1 = ndb.Key('Club',int(requestentity.club_id))
        key2 = ndb.Key('Profile',int(requestentity.from_pid))
        club_key = key1
        profile_key = key2
        #change the ID portion when merging with front end
                    #setattr(clubRequest, field, profile_key)

        if requestentity:
            for field in ('to_pid','club_id','description','status','post_request_id','collegeId','title','from_pid'):
                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="club_id"):
                        setattr(post_request, field, club_key)
                    elif(field=="from_pid"):
                        setattr(post_request, field, profile_key)
                    elif val:
                        print("Value is",val)
                        setattr(post_request, field, str(val))



                elif field == "to_pid":

                    query = club_key.get()
                    admin_id = query.admin
                    person = admin_id.get()
                    print "Person's email-id ", person.email
                    person_collegeId = person.collegeId
                    print "His college Id ", person.collegeId
                    college_details = person_collegeId.get()
                    print "The sup is ", college_details.student_sup
                    print("Finished to-pid")
                    setattr(post_request, field,admin_id)
                elif field == "status":
                    setattr(post_request, field, "Yes")
                elif field == "post_request_id":
                    setattr(post_request, field, "ABCD123")
                elif field == "collegeId":
                    setattr(post_request, field, person_collegeId)

        print("About to createClubRequest")
        print(post_request)
        post_request.put()

        return post_request

   def postEntry(self,requestentity=None):

        newPost = Post()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        club_name = Club.query()
        print "The request entity key is " + requestentity.club_id
        key1 = ndb.Key('Club',int(requestentity.club_id))
        key2 = ndb.Key('Profile',int(requestentity.from_pid))
        persons = Profile.query()
        #print club_name[0]
        #print "The key is " + club_name[0].key
        club_key = key1
        profile_key = key2
        print "Profile Key " + str(profile_key)
        for x in persons:
            print x.key
            if(x.key == profile_key):
                print "Same"
            else:
                print "NOPE"
                    #setattr(clubRequest, field, profile_key)

        #Change the below portion once you incorporate actual Ids.

        if requestentity:
            for field in ('title','description','club_id','from_pid','likes','postId','views','collegeId'):

                if hasattr(requestentity, field):
                    print(field,"is there")
                    val = getattr(requestentity, field)
                    if(field=="club_id"):
                        print "Club_Id stage"
                        setattr(newPost, field, club_key)

                    elif field == "from_pid":
                        print "Entered here"
                        person = profile_key.get()
                        print "Person's email-id ", person.email
                        person_collegeId = person.collegeId
                        print "His college Id ", person.collegeId
                        college_details = person_collegeId.get()
                        print "The sup is ", college_details.student_sup
                        setattr(newPost, field, "SDBJFB")
                        print "Put PID"
                        setattr(newPost,'collegeId',person_collegeId)
                        print "Put college id"

                    elif val:
                        print("Value is",val)
                        setattr(newPost, field, str(val))

                elif field == "likes":
                    setattr(newPost, field, 0)
                elif field == "postId":
                    setattr(newPost, field, "ABCD123")
                elif field == "views":
                    setattr(newPost, field, 0)


        print("About to createClubRequest")
        print(newPost)
        newPost.put()

        return newPost

   def getColleges(self):
       colleges = Colleges()
       query = CollegeDb.query()
       temp = ""
       for records in query:
           temp = temp + records.abbreviation
           temp +=","
           print "\n"

       print "The list of colleges are " + temp
       setattr(colleges,'collegeList',temp)

       return colleges

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

   def copyPostToForm(self,post):
        pf = PostForm()
        for field in pf.all_fields():
            if hasattr(post, field.name):
                setattr(pf, field.name, str(getattr(post, field.name)))
        return pf




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


   @endpoints.method(PostMiniForm,message_types.VoidMessage,path='postRequest', http_method='POST', name='postRequest')
   def createPostRequest(self, request):
        print("Entered Post Request Portion")
        clubRequest = self.postRequest(request)
        print("Inserted into the post request table")


   @endpoints.method(PostMiniForm,message_types.VoidMessage,path='postEntry', http_method='POST', name='postEntry')
   def createPost(self, request):
        print("Entered Post Entry Portion")
        clubRequest = self.postEntry(request)
        print("Inserted into the posts table")

   @endpoints.method(message_types.VoidMessage,Colleges,path='getColleges', http_method='GET', name='getColleges')
   def getAllColleges(self, request):
        print("Entered get all colleges Portion")
        return self.getColleges()

   @endpoints.method(Event_Request,message_types.VoidMessage,path='eventEntry', http_method='POST', name='eventEntry')
   def createEvent(self, request):
        print("Entered Event Entry Portion")
        clubRequest = self.postEntry(request)
        print("Inserted into the events table")

   @endpoints.method(GetAllPosts,Posts,path='getPosts', http_method='GET', name='getPosts')
   def getPosts(self, request):
        print("Entered Get Posts Portion")
        temp = request.collegeId
        temp2 = request.clubId
        print "temp2" + str(temp2)
        if(temp2==None):
            print "None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            posts = Post.query(Post.collegeId==collegeId)
        else:
            print "Not None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            clubId = ndb.Key('Club',int(temp2))
            posts = Post.query(Post.collegeId==collegeId,Post.club_id==clubId)

        return Posts(items=[self.copyPostToForm(x) for x in posts])
        #clubRequest = self.postEntry(request)
        #print("Inserted into the events table")


api = endpoints.api_server([ClubApi]) # register API	