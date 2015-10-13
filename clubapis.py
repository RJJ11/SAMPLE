from datetime import datetime
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models import ClubRequestMiniForm, PostMiniForm,Colleges, Posts, GetAllPosts, LikePost, CommentsForm, Comments, GetPostRequestsForm
from Models import Club, Post_Request, Post, EventMiniForm, PostForm, GetCollege, EditPostForm
from Models import Club_Creation, GetInformation,GetAllPostRequests, UpdatePostRequests
from Models import Profile
from Models import CollegeDb
from Models import CollegeDbMiniForm
from Models import ClubMiniForm
from Models import GetClubMiniForm
from Models import JoinClubMiniForm
from Models import FollowClubMiniForm
from Models import ClubListResponse
from Models import ProfileMiniForm,Events,Event,ModifyEvent
from Models import ClubRetrievalMiniForm
from CollegesAPI import getColleges,createCollege
from PostsAPI import postEntry,postRequest,deletePost,unlikePost,likePost,commentForm,copyPostToForm,editpost
from PostsAPI import copyPostRequestToForm,update
from EventsAPI import eventEntry,copyEventToForm,deleteEvent,attendEvent
from ClubAPI import createClub,createClubAfterApproval,getClub
from ProfileAPI import _copyProfileToForm,_doProfile,_getProfileFromUser
from settings import ANROID_CLIENT_ID,WEB_CLIENT_ID
EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

@endpoints.api(name='clubs', version='v1',
    allowed_client_ids=[ANROID_CLIENT_ID,WEB_CLIENT_ID,API_EXPLORER_CLIENT_ID],
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
        college_ret = CollegeDb.query(CollegeDb.key == collegeId).fetch(1)

        print("College Ret",college_ret[0])
        if(college_ret):
           club_ret = Club.query(Club.name == request.club_name).filter(Club.abbreviation == request.abbreviation).filter(Club.collegeId == college_ret[0].key).fetch(1)
           print("Club Ret",club_ret)
           if(len(club_ret) == 0):
              clubRequest = createClub(request)
              print("Finished the clubRequest")

              newClub = createClubAfterApproval(clubRequest)
              print ("The new club is",newClub)
              #retClub = self.getClub(newClub)'''
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

        profileret = Profile.query(Profile.pid == profile.pid).fetch(1)
        print("A is ", profileret)
        if profileret:
          print("Not inserting")
        else :
          print("Inserting")
          profile_key = profile.put()


   @endpoints.method(EventMiniForm,message_types.VoidMessage,path='eventEntry', http_method='POST', name='eventEntry')
   def createEvent(self, request):
        print("Entered Event Entry Portion")
        print request.clubId
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
            posts = Post.query(Post.collegeId==collegeId)
        elif(temp==None):
            print "None"
            clubId = ndb.Key('Club',int(temp2))
            posts = Post.query(Post.club_id==clubId)

        else:
            print "Not None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            clubId = ndb.Key('Club',int(temp2))
            posts = Post.query(Post.collegeId==collegeId,Post.club_id==clubId)

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


   @endpoints.method(message_types.VoidMessage, ProfileMiniForm,
            path='profile', http_method='GET', name='getProfile')
   def getProfile(self, request):
        """Return user profile."""
        return _doProfile()


   @endpoints.method(ProfileMiniForm,ProfileMiniForm,
            path='profile', http_method='POST', name='saveProfile')
   def saveProfile(self, request):
        """Update & return user profile."""
        return _doProfile(request)


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
        query = Post_Request.query(Post_Request.to_pid==to_pid)


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
            events = Event.query(Event.collegeId==collegeId)
        elif(temp==None):
            print "No collegeID"
            clubId = ndb.Key('Club',int(temp2))
            events = Event.query(Event.clubId==clubId)

        else:
            print "Not None"
            collegeId = ndb.Key('CollegeDb',int(temp))
            clubId = ndb.Key('Club',int(temp2))
            events = Post.query(Event.collegeId==collegeId,Event.clubId==clubId)

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

api = endpoints.api_server([ClubApi]) # register API	
