from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models import ClubRequestMiniForm, PostMiniForm,Colleges, Posts, GetAllPosts, LikePost, CommentsForm, Comments, GetPostRequestsForm,ProfileRetrievalMiniForm
from Models import Club, Post_Request, Post, EventMiniForm, PostForm, GetCollege, EditPostForm
from Models import Club_Creation, GetInformation,GetAllPostRequests, UpdatePostRequests
from Models import Profile,CollegeFeed
from Models import CollegeDb
from Models import CollegeDbMiniForm
from Models import ClubMiniForm
from Models import GetClubMiniForm
from Models import JoinClubMiniForm
from Models import FollowClubMiniForm,RequestMiniForm
from Models import ClubListResponse
from Models import ProfileMiniForm,Events,Event,ModifyEvent
from Models import ClubRetrievalMiniForm
from CollegesAPI import getColleges,createCollege,copyToCollegeFeed
from PostsAPI import postEntry,postRequest,deletePost,unlikePost,likePost,commentForm,copyPostToForm,editpost
from PostsAPI import copyPostRequestToForm,update
from EventsAPI import eventEntry,copyEventToForm,deleteEvent,attendEvent
from ClubAPI import createClub,createClubAfterApproval,getClub,unfollowClub,approveClub
from ProfileAPI import _copyProfileToForm,_doProfile,_getProfileFromEmail
from settings import ANROID_CLIENT_ID,WEB_CLIENT_ID,ANDROID_ID2
EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

@endpoints.api(name='clubs', version='v1',
    allowed_client_ids=[ANROID_CLIENT_ID,WEB_CLIENT_ID,API_EXPLORER_CLIENT_ID,ANDROID_ID2],
    scopes=[EMAIL_SCOPE])

# GETSTREAM KEY - urgm3xjebe9d

class ClubApi(remote.Service):

   @endpoints.method(GetClubMiniForm,ClubMiniForm,path='getClub', http_method='POST', name='getClub')
   def getClubApi(self,request):
        print("Request entity is",request)
        retClub = ClubMiniForm()
        if request:
             retClub = getClub(request)

        return retClub

   @endpoints.method(JoinClubMiniForm,message_types.VoidMessage,path='joinClub', http_method='POST', name='joinClub')
   def joinClubApi(self,request):


        if request:

            clubKey = ndb.Key('Club',int(request.club_id))
            club = clubKey.get()

            profileKey = ndb.Key('Profile',int(request.from_pid))
            profile = profileKey.get()
            print("Retrieved Profile ",profile)


            if (club and profile) :
                #add profile to club
                print("entered here")
                currentClub = club
                currentClub.members.append(profile.key)
                currentClub.follows.append(profile.key)
                currentClub.put()

                currentProfile = profile
                currentProfile.clubsJoined.append(currentClub.key)
                currentProfile.follows.append(currentClub.key)
                currentProfile.put()



        return message_types.VoidMessage()

   @endpoints.method(FollowClubMiniForm,message_types.VoidMessage,path='followClub', http_method='POST', name='followClub')
   def followClubApi(self,request):

        print("Request entity is",request)

        if request:

            clubKey = ndb.Key('Club',int(request.club_id))
            club = clubKey.get()

            profileKey = ndb.Key('Profile',int(request.from_pid))
            profile = profileKey.get()

            if (club and profile) :
                #add profile to club
                currentClub = club
                currentClub.follows.append(profile.key)
                currentClub.put()

                currentProfile = profile
                currentProfile.follows.append(currentClub.key)
                currentProfile.put()



        return message_types.VoidMessage()

   @endpoints.method(FollowClubMiniForm,message_types.VoidMessage,path='unfollowclub', http_method='POST', name='unfClub')
   def unfClub(self, request):
        """Update & return user profile."""
        ret = unfollowClub(request)

        if(ret == True):
          print("Cool")


        else:
          print("Operation not allowed")

        return message_types.VoidMessage()

   @endpoints.method(ClubRetrievalMiniForm,ClubListResponse,path='getClubList', http_method='POST', name='getClubList')
   def getClubListApi(self,request):
        list_of_clubs = ClubListResponse()
        print("Request entity is",request)

        if request:


            collegeKey = ndb.Key('CollegeDb',int(request.college_id))
            college = collegeKey.get()

            if(college):


                for obj in college.group_list :
                   ret_club = obj.get()

                   format_club = ClubMiniForm()

                   format_club.name = ret_club.name

                   format_club.abbreviation = ret_club.abbreviation

                   format_club.admin = ret_club.admin.get().name

                   format_club.collegeName = ret_club.collegeId.get().name

                   format_club.description = ret_club.description

                   format_club.club_id = str(ret_club.key.id())


                   list_of_clubs.list.append(format_club)





        return list_of_clubs

   @endpoints.method(ClubRequestMiniForm,message_types.VoidMessage,path='club', http_method='POST', name='createClubRequest')
   def createClubRequest(self, request):

        collegeId = ndb.Key('CollegeDb',int(request.college_id))
        print("Required College ID",collegeId)

        college_ret = collegeId.get()

        print("College Ret",college_ret)
        if(college_ret):
           club_ret = Club.query(Club.name == request.club_name).filter(Club.abbreviation == request.abbreviation).filter(Club.collegeId == college_ret.key).fetch(1)
           print("Club Ret",club_ret)
           if(len(club_ret) == 0):
              clubRequest = createClub(request)
              print("Finished the clubRequest")


        return message_types.VoidMessage()

   @endpoints.method(RequestMiniForm,message_types.VoidMessage,path='approveclubreq', http_method='POST', name='approveClubReq')
   def approveClub(self,request):
        #Obtain the club request object

        clubRequest = ndb.Key('Club_Creation',int(request.req_id))
        req = clubRequest.get()

        if(req and req.approval_status == "N"):
           status = approveClub(req)
           #status returns a "y" or "N"
           if(status == "Y"):
              print("Request Approval Granted")
           else:
              print("Request Approval Denied")
              req.key.delete()
        return message_types.VoidMessage()







   @endpoints.method(RequestMiniForm,message_types.VoidMessage,path='clubcreate', http_method='POST', name='createClub')
   def createClub(self,request):
        #Obtain the club request object

        clubRequest = ndb.Key('Club_Creation',int(request.req_id))
        print("Club Request",clubRequest)

        req = clubRequest.get()

        print(req)


        if(req.approval_status=="Y"):
         newClub = createClubAfterApproval(req)
         print ("The new club is",newClub)
        else :
         print("Request hasn't been approved")

        return message_types.VoidMessage()

   @endpoints.method(CollegeDbMiniForm,message_types.VoidMessage,path='collegeDB', http_method='POST', name='createCollege')
   def createCollegeDb(self, request):
        print("Entered CollegeDb Portion")
        clubRequest = createCollege(request)
        print("Finished entering a college")
        return message_types.VoidMessage()


   @endpoints.method(PostMiniForm,message_types.VoidMessage,path='postRequest', http_method='POST', name='postRequest')
   def createPostRequest(self, request):
        print("Entered Post Request Portion")
        clubRequest = postRequest(request)
        print("Inserted into the post request table")
        return message_types.VoidMessage()


   @endpoints.method(PostMiniForm,message_types.VoidMessage,path='postEntry', http_method='POST', name='postEntry')
   def createPost(self, request):
        print("Entered Post Entry Portion")
        flag=0
        clubRequest = postEntry(request,flag)
        print("Inserted into the posts table")
        return message_types.VoidMessage()

   @endpoints.method(message_types.VoidMessage,Colleges,path='getColleges', http_method='GET', name='getColleges')
   def getAllColleges(self, request):
        print("Entered get all colleges Portion")
        colleges = CollegeDb.query()
        return Colleges(collegeList=[getColleges(x) for x in colleges])

   @endpoints.method(message_types.VoidMessage,message_types.VoidMessage,path='insertUnique', http_method='POST', name='insertUnique')
   def insertUnique(self,request):

        #This method is just a reference in order for you to reuse this code in order to insert unique entries in the DB
        college_key = ndb.Key('CollegeDb',int('5629499534213120'))
        profile =  Profile(name = 'RJJ',
                            email = 'rohitjjoseph@gmail.com',
                            phone = '7760532293',

                            isAlumni='N',
                            collegeId= college_key)


        profile_key = profile.put()


   @endpoints.method(EventMiniForm,message_types.VoidMessage,path='eventEntry', http_method='POST', name='eventEntry')
   def createEvent(self, request):
        print("Entered Event Entry Portion")
        print request.club_id
        clubRequest = eventEntry(request)
        print("Inserted into the events table")
        return message_types.VoidMessage()

   @endpoints.method(GetAllPosts,Posts,path='getPosts', http_method='GET', name='getPosts')
   def getPosts(self, request):
        print("Entered Get Posts Portion")
        temp = request.collegeId
        temp2 = request.clubId
        print "temp2" + str(temp2)
        if(temp2==None):
            print "None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            posts = Post.query(Post.collegeId==collegeId).order(-Post.timestamp)
        elif(temp==None):
            print "None"
            clubId = ndb.Key('Club',int(temp2))
            posts = Post.query(Post.club_id==clubId).order(-Post.timestamp)

        else:
            print "Not None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            clubId = ndb.Key('Club',int(temp2))
            posts = Post.query(Post.collegeId==collegeId,Post.club_id==clubId).order(-Post.timestamp)

        #pylist =[copyPostToForm(x) for x in posts]
        #print "the list"
        #print pylist

        return Posts(items=[copyPostToForm(x) for x in posts])
        #clubRequest = self.postEntry(request)
        #print("Inserted into the events table")

   @endpoints.method(LikePost,message_types.VoidMessage,path='likePost', http_method='POST', name='likePosts')
   def likePosts(self, request):
       print "Entered the Like Posts Section"
       x = likePost(request)
       return message_types.VoidMessage()


   @endpoints.method(EditPostForm,message_types.VoidMessage,path='editPost', http_method='POST', name='editPost')
   def editPost(self, request):
       print "Entered the Like Posts Section"
       editpost(request)
       return message_types.VoidMessage()


   @endpoints.method(CommentsForm,message_types.VoidMessage,path='comment', http_method='POST', name='comments')
   def comments(self, request):
       print "Entered the Like Posts Section"
       return commentForm(request)
       return message_types.VoidMessage()

   @endpoints.method(ProfileRetrievalMiniForm, ProfileMiniForm,
            path='profile', http_method='GET', name='getProfile')
   def getProfile(self, request):
        """Return user profile."""
        email=getattr(request,"email")
        return _doProfile(email)


   @endpoints.method(ProfileMiniForm,ProfileMiniForm,
            path='profile', http_method='POST', name='saveProfile')
   def saveProfile(self, request):
        """Update & return user profile."""
        email=getattr(request,"email")
        return _doProfile(email,request)



   @endpoints.method(LikePost,message_types.VoidMessage,
            path='deletePost', http_method='DELETE', name='delPost')
   def delPost(self, request):
        """Update & return user profile."""
        deletePost(request)
        return message_types.VoidMessage()

   @endpoints.method(LikePost,message_types.VoidMessage,
            path='unlikePost', http_method='POST', name='unlikePost')
   def unlike(self, request):
        """Update & return user profile."""
        unlikePost(request)
        return message_types.VoidMessage()

   @endpoints.method(GetInformation,GetAllPostRequests,
            path='getPostRequests', http_method='POST', name='getPostRequests')
   def getPostRequests(self, request):
        """Update & return user profile."""

        to_pid = ndb.Key('Profile',int(request.pid))
        query = Post_Request.query(Post_Request.to_pid==to_pid).order(-Post_Request.timestamp)


        return GetAllPostRequests(items=[copyPostRequestToForm(x) for x in query])


   @endpoints.method(UpdatePostRequests,message_types.VoidMessage,
            path='updatePostRequests', http_method='POST', name='updatePostRequests')
   def updatePostRequests(self, request):
        """Update & return user profile."""
        update(request)
        return message_types.VoidMessage()

   @endpoints.method(GetAllPosts,Events,path='getEvents', http_method='GET', name='getEvents')
   def getEvents(self, request):
        print("Entered Get Events Portion")
        temp = request.collegeId
        temp2 = request.clubId
        print "temp2" + str(temp2)
        if(temp2==None):
            print "No CLubId"
            collegeId = ndb.Key('CollegeDb',int(temp))
            events = Event.query(Event.collegeId==collegeId).order(-Event.start_time)
        elif(temp==None):
            print "No collegeID"
            clubId = ndb.Key('Club',int(temp2))
            events = Event.query(Event.club_id==clubId).order(-Event.start_time)

        else:
            print "Not None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            clubId = ndb.Key('Club',int(temp2))
            events = Event.query(Event.collegeId==collegeId,Event.club_id==clubId).order(-Event.start_time)

        return Events(items=[copyEventToForm(x) for x in events])

   @endpoints.method(ModifyEvent,message_types.VoidMessage,
            path='deleteEvent', http_method='DELETE', name='delEvent')
   def delEvent(self, request):
        """Update & return user profile."""
        deleteEvent(request)
        return message_types.VoidMessage()

   @endpoints.method(ModifyEvent,message_types.VoidMessage,path='attendEvent', http_method='POST', name='attendEvents')
   def attendEvents(self, request):
       print "Entered the Like Posts Section"
       x = attendEvent(request)
       return message_types.VoidMessage()

   @endpoints.method(GetInformation,CollegeFeed,path='mainFeed', http_method='POST', name='collegeFeed')
   def collegeFeed(self, request):
       print "Entered the Like Posts Section"
       collegeId = ndb.Key('CollegeDb',int(request.collegeId))
       posts = Post.query(Post.collegeId==collegeId).order(-Post.timestamp)
       events = Event.query(Event.collegeId==collegeId).order(-Event.timestamp)
       print events
       #CollegeFeed(items=[copyEventToForm(x) for x in posts])
       #CollegeFeed(items=[copyEventToForm(x) for x in events])
       pylist = [copyToCollegeFeed(x) for x in events]
       print pylist
       pylist2 = [copyToCollegeFeed(x) for x in posts]
       pylist+=pylist2
       #pylist.append(copyToCollegeFeed(x) for x in events)
       pylist.sort(key=lambda x: x.timestamp, reverse=True)
       print pylist[1].timestamp
       #print pylist
       CollegeFeed(items=pylist)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       return CollegeFeed(items=pylist)

   @endpoints.method(GetInformation,CollegeFeed,path='myFeed', http_method='POST', name='personalFeed')
   def personalFeed(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       profile = pid.get()
       posts = []
       events = []
       pylist = []
       pylist2 = []
       for x in profile.follows:
           print x
           posts = (Post.query(Post.club_id==x))
           events = (Event.query(Event.club_id==x))
           list1 = [copyToCollegeFeed(y) for y in events]
           list2 = [copyToCollegeFeed(z) for z in posts]
           print "LIST-1"
           print list1
           pylist+=list1
           pylist2+=list2
       #for x in events:
       #    print x


       #pylist = [copyToCollegeFeed(x) for x in events]
       #pylist2 = [copyToCollegeFeed(x) for x in posts]
       pylist+=pylist2
       #pylist.append(copyToCollegeFeed(x) for x in events)
       pylist.sort(key=lambda x: x.timestamp, reverse=True)
       print pylist[1].timestamp
       #print pylist
       CollegeFeed(items=pylist)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       return CollegeFeed(items=pylist)


api = endpoints.api_server([ClubApi]) # register API	
