from datetime import datetime
import endpoints
import datetime as dt
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from datetime import datetime,date,time
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models import ClubRequestMiniForm, PostMiniForm,Colleges, Posts, GetAllPosts, LikePost, CommentsForm, Comments, GetPostRequestsForm,ProfileRetrievalMiniForm, \
    MessageResponse, ProfileResponse
from Models import Club, Post_Request, Post, EventMiniForm, PostForm, GetCollege, EditPostForm
from Models import Club_Creation, GetInformation,GetAllPostRequests, UpdatePostRequests
from Models import Profile,CollegeFeed
from Models import CollegeDb,Notifications,NotificationResponseForm,NotificationList
from Models import CollegeDbMiniForm
from Models import ClubMiniForm
from Models import GetClubMiniForm
from Models import JoinClubMiniForm
from Models import FollowClubMiniForm,RequestMiniForm,NotificationMiniForm,PersonalInfoRequest,PersonalInfoResponse,PersonalResponse
from Models import ClubListResponse
from Models import ProfileMiniForm,Events,Event,ModifyEvent
from Models import ClubRetrievalMiniForm,UpdateGCM,Join_Creation,AdminFeed,SuperAdminFeedResponse,SetSuperAdminInputForm,SetAdminInputForm
from CollegesAPI import getColleges,createCollege,copyToCollegeFeed
from PostsAPI import postEntry,postRequest,deletePost,unlikePost,likePost,commentForm,copyPostToForm,editpost
from PostsAPI import copyPostRequestToForm,update
from EventsAPI import eventEntry,copyEventToForm,deleteEvent,attendEvent
from ClubAPI import createClub,createClubAfterApproval,getClub,unfollowClub,approveClub,copyJoinRequestToForm,copyToSuperAdminList
from ProfileAPI import _copyProfileToForm,_doProfile,_getProfileFromEmail,changeGcm,PersonalInfoForm
from settings import ANROID_CLIENT_ID,WEB_CLIENT_ID,ANDROID_ID2,ANDROID_ID3
from gae_python_gcm.gcm import GCMMessage, GCMConnection

#data = {'message': '5 mins later',"title":"Hi RKD"}
#gcm_message = GCMMessage('cDXc7bMlwPQ:APA91bGAXV7203E6GUPkrbSOzQBv1_Xc4ztClQ6XcEcr80jw9jKBdZmLZ1U04_dTiH37AOydvv07_fBGiZXrszGkIxN5ZQgjsdqu35orSSOVq02XxDLVcBaqRMvxQTr-ucYQzbVoj5kE', data)
#gcm_conn = GCMConnection()
#gcm_conn.notify_device(gcm_message)



EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


@endpoints.api(name='clubs', version='v1',
    allowed_client_ids=[ANROID_CLIENT_ID,WEB_CLIENT_ID,API_EXPLORER_CLIENT_ID,ANDROID_ID2,ANDROID_ID3],
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

   @endpoints.method(GetClubMiniForm,PersonalInfoResponse,path='getClubMembers', http_method='POST', name='getClubMembers')
   def getClubMembersApi(self,request):
        #print("Request entity is",request)
        clubKey = ndb.Key('Club',int(request.club_id))
        club = clubKey.get()
        #print("Received Club is",club)  
        list1 = club.members
        pylist=[]
        for x in list1:
           person = x.get()
           pylist.append(PersonalInfoForm(person))

        return PersonalInfoResponse(items = pylist)

   @endpoints.method(JoinClubMiniForm,message_types.VoidMessage,path='joinClub', http_method='POST', name='joinClubReq')
   def joinClubApi(self,request):
            
            if request:
             clubKey = ndb.Key('Club',int(request.club_id))
             club = clubKey.get()

             profileKey = ndb.Key('Profile',int(request.from_pid))
             profile = profileKey.get()
             
             if (club and profile and profileKey not in club.members):
                joinCreationObj = Join_Creation()
                joinCreationObj.from_pid = profileKey
                joinCreationObj.to_pid = club.admin
                to_pidProfile = joinCreationObj.to_pid.get()
                joinCreationObj.club_id = clubKey
                joinCreationObj.timestamp = dt.datetime.now().replace(microsecond = 0)
                print("join obj",joinCreationObj)
                joinCreationObjKey = joinCreationObj.put()

                newNotif = Notifications(
                     clubName = club.name,
                     clubId = club.key,
                     clubphotoUrl = club.photoUrl,
                     to_pid = joinCreationObj.to_pid,
                     type = "Join Request",
                     timestamp = joinCreationObj.timestamp
                    )

                print("Notification to be inserted in join approval",newNotif)
                newNotifKey = newNotif.put()
                 
                data = {'message': profile.name + " wishes to join","title":  club.name}
                print (data)
                gcmId = to_pidProfile.gcmId
                gcm_message = GCMMessage(gcmId, data)
                gcm_conn = GCMConnection()
                gcm_conn.notify_device(gcm_message)
             
           
            return message_types.VoidMessage()


   @endpoints.method(RequestMiniForm,message_types.VoidMessage,path='joinClubApproval', http_method='POST', name='joinClubApproval')
   def joinClubApprovalApi(self,request):
        if request:
          
          joinCreation = ndb.Key('Join_Creation',int(request.req_id)).get()
          club = joinCreation.club_id.get()
          profileKey = joinCreation.from_pid
          profile = profileKey.get()
          print("Retrieved Profile ",profile)

          if(request.action == "N"):
                 
                 #send notif message to the guy who has req,saying that it has been rejected
                 newNotif = Notifications(
                     clubName = club.name,
                     clubId = club.key,
                     clubphotoUrl = club.photoUrl,
                     to_pid = joinCreation.from_pid,
                     type = "Approval Rejection",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                     
                    )

                 print("Notification to be inserted in join approval",newNotif)
                 newNotifKey = newNotif.put()
                 data = {'message': "Approval Denied","title": club.name}
                 print (data)
                 gcmId = profile.gcmId
                 gcm_message = GCMMessage(gcmId, data)
                 gcm_conn = GCMConnection()
                 gcm_conn.notify_device(gcm_message)
                 joinCreation.key.delete()


          elif (club and profile and (profileKey not in  club.members)):
                 print("entered here")
                 currentClub = club
                 currentClub.members.append(profile.key)
                 
                 currentProfile = profile
                 currentProfile.clubsJoined.append(currentClub.key)
                 
                 if (currentProfile.key not in currentClub.follows):
                   print ("I've entered this because these guys are totally new")
                   currentProfile.follows.append(currentClub.key)
                   currentClub.follows.append(profile.key)
                 
                 currentClub.put()
                 currentProfile.put()

                 #Create Notification here where the to_pid = guy who has made the join req
                 #Send push notification to the gcm id of this dude.
                 newNotif = Notifications(
                     clubName = club.name,
                     clubId = club.key,
                     clubphotoUrl = club.photoUrl,
                     to_pid = joinCreation.from_pid,
                     type = "Approved Join Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

                 print("Notification to be inserted in join approval",newNotif)
                 newNotifKey = newNotif.put()
                 data = {'message': "You are now a member","title": currentClub.name}
                 print (data)
                 gcmId = currentProfile.gcmId
                 gcm_message = GCMMessage(gcmId, data)
                 gcm_conn = GCMConnection()
                 gcm_conn.notify_device(gcm_message)
                 joinCreation.key.delete()
          

        return message_types.VoidMessage()

   @endpoints.method(FollowClubMiniForm,message_types.VoidMessage,path='followClub', http_method='POST', name='followClub')
   def followClubApi(self,request):

        print("Request entity is",request)

        if request:

            clubKey = ndb.Key('Club',int(request.club_id))
            club = clubKey.get()

            profileKey = ndb.Key('Profile',int(request.from_pid))
            profile = profileKey.get()

            if (club and profile and (profileKey not in  club.follows)):
                #add profile to club
                currentClub = club
                currentClub.follows.append(profile.key)
                currentClub.put()

                currentProfile = profile
                currentProfile.follows.append(currentClub.key)
                currentProfile.put()
            else:
                print ("He's already following the club")     



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
                   format_club.collegeName = ret_club.collegeId.get().name
                   format_club.name = ret_club.admin.get().name
                   format_club.description = ret_club.description
                   format_club.club_id = str(ret_club.key.id())
                   if(request.pid != None):
                         format_club.isMember = "N"
                         format_club.isFollower = "N"
                         profileKey = ndb.Key('Profile',int(request.pid))
                         print ("retrieved profile key is ", profileKey)

                         if (profileKey in ret_club.follows):
                             format_club.isFollower = "Y"
                         if (profileKey in ret_club.members):
                             format_club.isMember = "Y"


                   list_of_clubs.list.append(format_club)





        return list_of_clubs

   @endpoints.method(NotificationMiniForm,ClubListResponse,path='getClubListofAdmin', http_method='POST', name='getClubListofAdmin')
   def getClubListApiofAdmin(self,request):
               #Make new api for GetList of clubs you are admin of.
               #Take PID and return all clubs he is admin of.
               #Return response just like getClubList response
               profileKey = ndb.Key('Profile',int(request.pid))
               profile = profileKey.get()
               list_of_clubs = ClubListResponse()
               for obj in profile.admin:
                   ret_club = obj.get()
                   format_club = ClubMiniForm()
                   format_club.name = ret_club.name
                   format_club.abbreviation = ret_club.abbreviation
                   format_club.collegeName = ret_club.collegeId.get().name
                   format_club.name = ret_club.admin.get().name
                   format_club.description = ret_club.description
                   format_club.club_id = str(ret_club.key.id())
                   format_club.isMember = "Y"
                   format_club.isFollower = "Y"
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
              currentProfile = clubRequest.to_pid.get()
              newNotif = Notifications(
                     clubName = clubRequest.club_name,
                     clubphotoUrl = clubRequest.photoUrl,
                     to_pid = clubRequest.to_pid,
                     type = "Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              print("Notification to be inserted in club creation request",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': clubRequest.club_name,"title": "Creation Request"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              gcm_conn.notify_device(gcm_message)
              print("Finished the clubRequest")


        return message_types.VoidMessage()

   @endpoints.method(RequestMiniForm,message_types.VoidMessage,path='approveclubreq', http_method='POST', name='approveClubReq')
   def approveClub(self,request):
        #Obtain the club request object

        clubRequest = ndb.Key('Club_Creation',int(request.req_id))
        action = request.action 
        
        print ("Action is",action)
        
        req = clubRequest.get()
        currentProfile = req.from_pid.get()

        print("From Pid profile is",currentProfile)
        
        if (action == 'N'):
            print ("Disapproving request and removing entry")
            print("Request Approval Denied")
            newNotif = Notifications(
                     clubName = req.club_name,
                     clubphotoUrl = req.photoUrl,
                     to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

            print("Notification to be inserted in club approval rejection",newNotif)
            newNotifKey = newNotif.put()
            data = {'message': req.club_name,"title": "Creation Request Denied"}
            print (data)
            gcmId = currentProfile.gcmId
            gcm_message = GCMMessage(gcmId, data)
            gcm_conn = GCMConnection()
            gcm_conn.notify_device(gcm_message)
            req.key.delete()
        
        elif (req and req.approval_status == "N"):
           status = approveClub(req)
           if(status == "Y"):
              print("Request Approval Granted")
              newClub = createClubAfterApproval(req)
              currentProfile = newClub.admin.get()
              if(newClub):
              	  newNotif = Notifications(
                     clubName = newClub.name,
                     clubId = newClub.key,
                     clubphotoUrl = newClub.photoUrl,
                     to_pid = newClub.admin,
                     type = "Approved Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              print("Notification to be inserted in club approval ",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': newClub.name,"title": "Creation Request Approved"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              gcm_conn.notify_device(gcm_message)
              
              print("The club that has been created is",newClub)
              req.key.delete()
           else:
              print("Request Approval Denied")
              newNotif = Notifications(
                     clubName = req.club_name,
                     clubphotoUrl = req.photoUrl,
                     to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              print("Notification to be inserted in club approval rejection",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': req.club_name,"title": "Creation Request Denied"}
              print (data)
              gcmId = currentProfile.gcmId
              gcm_message = GCMMessage(gcmId, data)
              gcm_conn = GCMConnection()
              gcm_conn.notify_device(gcm_message)
              req.key.delete()
            
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
        currentProfile = clubRequest.to_pid.get()
        newNotif = Notifications(
                     clubName = clubRequest.club_id.get().name,
                     clubId = clubRequest.club_id,
                     clubphotoUrl = clubRequest.photoUrl,
                     to_pid = clubRequest.to_pid,
                     type = "Post Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    
                    )

        print("Notification to be inserted in Post Creation Request",newNotif)
        newNotifKey = newNotif.put()
        data = {'message': clubRequest.title,"title": "Post Creation Request"}
        print (data)
        gcmId = currentProfile.gcmId
        gcm_message = GCMMessage(gcmId, data)
        gcm_conn = GCMConnection()
        gcm_conn.notify_device(gcm_message)
        print("Inserted into the post request table")
        return message_types.VoidMessage()


   @endpoints.method(PostMiniForm,MessageResponse,path='postEntry', http_method='POST', name='postEntry')
   def createPost(self, request):
        response = MessageResponse()
        print("Entered Post Entry Portion")
        flag=0
        try:
            person_key = ndb.Key('Profile',int(request.from_pid))

            profile = person_key.get()
            print(profile)
            club_key = ndb.Key('Club',int(request.club_id))
            if club_key in profile.follows:
                    print "Present"
                    newPost = postEntry(request,flag)

                    print("NEW POST",newPost)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    #Create Notification Feed
                    group = newPost.club_id.get()
                    groupName = group.name
                    data = {'message': groupName,"title": newPost.title}
                    
                    postlist = []
                    if (group.follows):
                    	for pid in group.follows:
                           person = pid.get()
                           print ("PID is",person)
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             postlist.append(gcmId)
                           newNotif = Notifications(
                                      clubName = groupName,
                                      clubId = newPost.club_id,
                                      clubphotoUrl = group.photoUrl,
                                      postName = newPost.title,
                                      postId = newPost.key,
                                      timestamp = newPost.timestamp,
                                      type = "Post",
                                      to_pid = pid
                                      )

                           print("Notification to be inserted",newNotif)
                           newNotifKey = newNotif.put()  

                           
                    
                    
                    print ("post list is",postlist)
                    gcm_message = GCMMessage(postlist, data)
                    gcm_conn = GCMConnection()
                    gcm_conn.notify_device(gcm_message)
                   



            else:
                print "Not present"
                clubRequest = postRequest(request)
                response.status = "2"
                response.text = "Inserted into Posts Requests Table"

        except:
                print "Error"
                response.status = "3"
                response.text = "Couldn't insert into Posts Table"



        print("Inserted into the posts table")



        return response

   @endpoints.method(message_types.VoidMessage,Colleges,path='getColleges', http_method='GET', name='getColleges')
   def getAllColleges(self, request):
        print("Entered get all colleges Portion")
        colleges = CollegeDb.query()
        return Colleges(collegeList=[getColleges(x) for x in colleges])




   @endpoints.method(EventMiniForm,MessageResponse,path='eventEntry', http_method='POST', name='eventEntry')
   def createEvent(self, request):
        response = MessageResponse()
        print("Entered Event Entry Portion")
        
        try:
            person_key = ndb.Key('Profile',int(request.event_creator))
            print(person_key)
            profile = person_key.get()
            
            club_key = ndb.Key('Club',int(request.club_id))
            if club_key in profile.clubsJoined:
                    newEvent = eventEntry(request)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    group = newEvent.club_id.get()
                    groupName = group.name

                    

                    data = {'message': groupName,"title": newEvent.title}
                    
                    #get the followers of the club pids. Get GCM Id's from those and send
                    print ("GROUP FOLLOWS LIST ", group.follows)

                    eventlist = []
                    if (group.follows):
                        for pid in group.follows:
                           person = pid.get()
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             eventlist.append(gcmId)
                           newNotif = Notifications(
                                        clubName = groupName,
                                        clubId = newEvent.club_id,
                                        clubphotoUrl = group.photoUrl,
                                        eventName = newEvent.title,
                                        eventId = newEvent.key,
                                        timestamp = newEvent.timestamp,
                                        type = "Event",
                                        to_pid = pid
                                        )
                           print("Notification to be inserted",newNotif)
                           newNotifKey = newNotif.put()

                            
                      
                             
                    
                    print ("Event list is",eventlist)
                    gcm_message = GCMMessage(eventlist, data)
                    gcm_conn = GCMConnection()
                    gcm_conn.notify_device(gcm_message)
                   
                    print("Should have worked")

            else:
                print "Not Present"
                response.status = "2"
                response.text = "Could not insert"

        except Exception,e:
                print "Error"
                print str(e)
                response.status = "3"
                response.text = "Error"

        return response

   @endpoints.method(GetAllPosts,Posts,path='getPosts', http_method='GET', name='getPosts')
   def getPosts(self, request):
        print("Entered Get Posts Portion")
        temp = request.collegeId
        temp2 = request.clubId
        print "temp" + str(temp)
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

        return Posts(items=list(reversed([copyPostToForm(x) for x in posts])))
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

   @endpoints.method(ProfileRetrievalMiniForm, ProfileResponse,
            path='profile', http_method='GET', name='getProfile')
   def getProfile(self, request):
        """Return user profile."""
        email=getattr(request,"email")
        result = Profile.query(Profile.email==email)
        present =0
        isAdmin="N"
        isSuperAdmin="N"
        for y in result:
            if y.email == email:
                present = 1
                if y.admin is not None:
                    if len(y.admin)>0:
                        isAdmin="Y"
                if y.superadmin is not None:
                    if len(y.superadmin)>0:
                        isSuperAdmin="Y"
        if present ==1:
            success="True"
            a = _doProfile(email)
            return ProfileResponse(success=success,result=a,isAdmin=isAdmin,isSuperAdmin=isSuperAdmin)
        else:
            success="False"
            a = ProfileMiniForm(name = '',
                           email = '',
                           phone = '',
                           isAlumni='',
                           collegeId =''
                           )
            return ProfileResponse(success=success,result=a,isAdmin=isAdmin,isSuperAdmin=isSuperAdmin)


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
        date = request.date
        future_date = request.future_date
        

        print ("Future date is",future_date)
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

        #All events have been obtained, check if date field is provided and take only those that have start date = req.date

        finalList = []
        if(future_date!=None):
           print ("Future Date part")
           for x in events:
              start_date = str(x.start_time.date())
              print("Retrieve start date",start_date)
              if(start_date >= future_date):
                 print ("Start Date is",start_date)
                 print ("Event to be added",x.title)
                 finalList.append(x)
           print("Returning all events from Final List")
           return Events(items=list(reversed([copyEventToForm(x) for x in finalList])))
        elif(date != None):
           for x in events:
              start_date = str(x.start_time.date())
              if(start_date == date):	
                 finalList.append(x)
           print("Returning all events from Final List")
           return Events(items=list(reversed([copyEventToForm(x) for x in finalList])))
        else:
           print("Returning all events from Events List")
           return Events(items=list(reversed([copyEventToForm(x) for x in events])))

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
       temp = request.clubId
       flag =0
       pageLimit = 5
       skipCount=0
       upperBound=pageLimit
       print request.pageNumber

       try:
        skipCount = (int(request.pageNumber)-1)*pageLimit
        upperBound = int(request.pageNumber)*pageLimit

       except:
          print "Didnt give pageNumber-Default to 1"

       if request.date != None:
        date = datetime.strptime(getattr(request,"date"),"%Y-%m-%d").date()
        flag = 1
       #print "TYPE-DATE", type(date)
       if (temp==None):
           collegeId = ndb.Key('CollegeDb',int(request.collegeId))
           posts = Post.query(Post.collegeId==collegeId).order(-Post.timestamp)
           events = Event.query(Event.collegeId==collegeId).order(-Event.timestamp)
           print "TEMP IS NONE"
       else:
           clubId = ndb.Key('Club',int(request.clubId))
           posts = Post.query(Post.club_id==clubId).order(-Post.timestamp)
           events = Event.query(Event.club_id==clubId).order(-Event.timestamp)

       print events
       #CollegeFeed(items=[copyEventToForm(x) for x in posts])
       #CollegeFeed(items=[copyEventToForm(x) for x in events])
       #pylist = [copyToCollegeFeed(x) for x in events]
       pylist=[]
       for x in events:
           print "TImestamp",type(x.timestamp.strftime("%Y-%m-%d"))
           if flag==1:
            if x.timestamp.strftime("%Y-%m-%d") == str(date):
                pylist.append(copyToCollegeFeed(x))
           else:
               pylist.append(copyToCollegeFeed(x))
       print pylist
       pylist2 = []
       for x in posts:
           print "TImestamp",type(x.timestamp.strftime("%Y-%m-%d"))
           if flag==1:
            if x.timestamp.strftime("%Y-%m-%d") == str(date):
                pylist.append(copyToCollegeFeed(x))
           else:
               pylist.append(copyToCollegeFeed(x))
       #pylist2 = [copyToCollegeFeed(x) for x in posts]
       pylist+=pylist2
       #pylist.append(copyToCollegeFeed(x) for x in events)
       pylist.sort(key=lambda x: x.timestamp, reverse=True)
       #print pylist[1].timestamp
       #print pylist
       #CollegeFeed(items=pylist)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       #return CollegeFeed(items=pylist)

       finalList = []
       for i in xrange(skipCount,upperBound):
           if(i>=len(pylist)):
            break
           finalList.append(pylist[i])

       cf = CollegeFeed()
       cf.items = finalList
       cf.completed=str(0)
       if(upperBound>=len(pylist)):
                cf.completed=str(1)
       #print pylist[1].timestamp
       #print pylist

       CollegeFeed(items=finalList)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       return cf


   @endpoints.method(GetInformation,CollegeFeed,path='myFeed', http_method='POST', name='personalFeed')
   def personalFeed(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       profile = pid.get()
       posts = []
       events = []
       pylist = []
       pylist2 = []
       pageLimit = 5
       skipCount=0
       upperBound=pageLimit
       print request.pageNumber

       try:
        skipCount = (int(request.pageNumber)-1)*pageLimit
        upperBound = int(request.pageNumber)*pageLimit

       except:
          print "Didnt give pageNumber-Default to 1"



       list1=[]
       list2=[]
       for x in profile.follows:
           print x
           print "LOOP-1"
           posts = (Post.query(Post.club_id==x))
           events = (Event.query(Event.club_id==x))
           list1=[]
           list2=[]
           #list1 = [copyToCollegeFeed(y) for y in events]
           #list2 = [copyToCollegeFeed(z) for z in posts]
           iteration=0
           for y in posts:
               #if(iteration>=skipCount and iteration<upperBound):
               list1.append(copyToCollegeFeed(y))

               #iteration+=1
               #if(iteration==upperBound):
               #    break

           iteration=0

           for z in events:
               #if(iteration>=skipCount and iteration<upperBound):
                list1.append(copyToCollegeFeed(z))
                #iteration+=1
               #if(iteration==upperBound):
               #    break

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
       finalList = []
       for i in xrange(skipCount,upperBound):
           if(i>=len(pylist)):
            break
           finalList.append(pylist[i])

       cf = CollegeFeed()
       cf.items = finalList
       cf.completed=str(0)
       if(upperBound>=len(pylist)):
                cf.completed=str(1)
       #print pylist[1].timestamp
       #print pylist

       CollegeFeed(items=finalList)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       return cf

    


   @endpoints.method(GetInformation,CollegeFeed,path='dontTouch', http_method='POST', name='dontTouch')
   def dontTouch(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       clubId = Club.query(Club.admin==pid)
       pylist=[]
       for x in clubId:
           print x.key
           posts = Post.query(Post.club_id==x.key).order(-Post.timestamp)
           events = Event.query(Event.club_id==x.key).order(-Post.timestamp)
           list1=[]
           list2=[]
           list1 = [copyToCollegeFeed(y) for y in events]
           list2 = [copyToCollegeFeed(z) for z in posts]
           list1+=list2
           print "List-1",list1
           pylist+=list1
       pylist.sort(key=lambda x: x.timestamp, reverse=True)
       return CollegeFeed(items=pylist)

   @endpoints.method(GetInformation,AdminFeed,path='adminFeed', http_method='POST', name='adminFeed')
   def adminFeed(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       clubId = ndb.Key('Club',int(request.clubId))
       #post_requests = Post_Request.query(Post_Request.to_pid==pid,Post_Request.club_id==clubId).order(Post_Request.reqtimestamp)
       #list1=[]
       list2 = []
       #for y in post_requests:
           #list1.append(copyPostRequestToForm(y))

       join_requests = Join_Creation.query(Join_Creation.to_pid==pid,Join_Creation.club_id==clubId).order(Join_Creation.timestamp)
       for y in join_requests:
           list2.append(copyJoinRequestToForm(y))


       return AdminFeed(joinReq=list2)
   @endpoints.method(GetInformation,SuperAdminFeedResponse,path='superAdminFeed', http_method='POST', name='superAdminFeed')
   def superAdminFeed(self,request):
       pid = ndb.Key('Profile',int(request.pid))
       collegeId = ndb.Key('CollegeDb',int(request.collegeId))
       profile = pid.get()
       college = collegeId.get()
       list1=[]
       if collegeId in profile.superadmin:
           query = Club_Creation.query(Club_Creation.to_pid==pid).order(Club_Creation.timestamp)
           for x in query:
             list1.append(copyToSuperAdminList(x))
            

       return SuperAdminFeedResponse(items=list1)
       

   



   @endpoints.method(ProfileRetrievalMiniForm, ProfileResponse,path='profileGCM', http_method='POST', name='profileGCM')
   def profileGCM(self, request):
        email=getattr(request,"email")
        gcmId=getattr(request,"gcmId")
        result = Profile.query(Profile.email==email)
        present =0
        isAdmin = "N"
        isSuperAdmin = "N"
        for y in result:
            if y.email == email:
                present = 1
                print y.gcmId
                y.gcmId = gcmId
                y.put()
                if y.admin is not None:
                    if len(y.admin)>0:
                        isAdmin="Y"
                if y.superadmin is not None:
                    if len(y.superadmin)>0:
                        isSuperAdmin="Y"

        if present ==1:
            success="True"
            a = _doProfile(email)
            return ProfileResponse(success=success,result=a,isAdmin=isAdmin,isSuperAdmin=isSuperAdmin)
        else:
            success="False"
            a = ProfileMiniForm(name = '',
                           email = '',
                           phone = '',
                           isAlumni='',
                           collegeId =''
                           )
            return ProfileResponse(success=success,result=a,isAdmin=isAdmin,isSuperAdmin=isSuperAdmin)

   @endpoints.method(NotificationMiniForm,NotificationList,path='myNotifications', http_method='POST', name='myNotificationFeed')
   def myNotificationFeed(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       notificationslist = Notifications.query(Notifications.to_pid == pid).order(-Notifications.timestamp).fetch()
       
       listresponse = NotificationList()

       for obj in notificationslist:
             newListObj = NotificationResponseForm()
             
             #if( pid in obj.to_pid):

             if(obj.clubName != None):
                  newListObj.clubName = obj.clubName
             else:
                  newListObj.clubName = None
             

             if(obj.clubId != None):
                  newListObj.clubId = str(obj.clubId.id())
             else:
                  newListObj.clubId = None
                          
             if(obj.clubphotoUrl != None):
                  newListObj.clubphotoUrl = obj.clubphotoUrl
             else:
                  newListObj.clubphotoUrl = None

             if(obj.eventName != None):
                  newListObj.eventName = obj.eventName
             else:
                  newListObj.eventName = None
             

             if(obj.eventId != None):
                  newListObj.eventId = str(obj.eventId.id())
             else:
                  newListObj.eventId = None
             

             if(obj.postName != None):
                  newListObj.postName = obj.postName
             else :
                  newListObj.postName = None
             

             if(obj.postId != None):
                  newListObj.postId = str(obj.postId.id())
             else :
                  newListObj.postId = None
             newListObj.timestamp = str(obj.timestamp)   
             
             newListObj.type = obj.type
             listresponse.list.append(newListObj) 
               
       
       

       return listresponse

   @endpoints.method(PersonalInfoRequest,PersonalInfoResponse,path='personalInfo', http_method='POST', name='personalInfo')
   def personalInfo(self,request):
       list1 = request.pid
       pylist=[]
       for x in list1:
           pid = ndb.Key('Profile',int(x))
           person = pid.get()
           pylist.append(PersonalInfoForm(person))

       return PersonalInfoResponse(items = pylist)


   @endpoints.method(SetSuperAdminInputForm,message_types.VoidMessage,path='setSuperAdmin', http_method='POST', name='setSuperAdmin')
   def setSuperAdmin(self,request):
       collegeKey = ndb.Key('CollegeDb',int(request.collegeId))
       college = collegeKey.get()
       emailId = college.sup_emailId
       retrievedProfile = Profile.query(Profile.email==emailId).fetch(1)
       print ("retrievedProfile is",retrievedProfile[0])

       if not retrievedProfile[0].superadmin:
          retrievedProfile[0].superadmin.append(collegeKey)
          retrievedProfile[0].put()
          print("inserted into profile table")       



       return message_types.VoidMessage()

   @endpoints.method(SetAdminInputForm,message_types.VoidMessage,path='setAdmin', http_method='POST', name='setAdmin')
   def setAdmin(self,request):
       clubKey = ndb.Key('Club',int(request.clubId))
       club = clubKey.get()
       adminProfile = club.admin.get()
       
       if clubKey not in adminProfile.admin:
          adminProfile.admin.append(clubKey)
          adminProfile.put()
       



       return message_types.VoidMessage()


api = endpoints.api_server([ClubApi])   # register API
