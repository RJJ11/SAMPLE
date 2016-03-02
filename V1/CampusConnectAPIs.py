from datetime import datetime
import endpoints
import datetime as dt
import time as t
import os
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from datetime import datetime,date,time
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from Models_v1 import ClubRequestMiniForm, PostMiniForm,Colleges, Posts, GetAllPosts, LikePost, CommentsForm,CommentsResponseForm,CommentsResponse, Comments, GetPostRequestsForm,ProfileRetrievalMiniForm, \
    MessageResponse, ProfileResponse, BDCommentResponse, BDCommentCount, BDComments, MiscCount, KMCScoreHandler, KMCScore, \
    KMCScoreModel, AddCollegeForm, ProspectiveColleges, EventsByDateForm, EventsByDate, LiveCommentsForm, LiveComments, \
    LiveCommentsResponse, SlamDunkScoreBoardForm, SlamDunkScoreBoard, ScoreResponse, SubscribeMatch
from Models_v1 import Club, Post_Request, Post, EventMiniForm, PostForm, GetCollege, EditPostForm
from Models_v1 import Club_Creation, GetInformation,GetAllPostRequests, UpdatePostRequests
from Models_v1 import Profile,CollegeFeed
from Models_v1 import CollegeDb,Notifications,NotificationResponseForm,NotificationList
from Models_v1 import CollegeDbMiniForm
from Models_v1 import ClubMiniForm
from Models_v1 import GetClubMiniForm
from Models_v1 import JoinClubMiniForm,GetEventsEitherSideMiniForm,GetEventsESReturnForm,GetEventsResponse
from Models_v1 import FollowClubMiniForm,RequestMiniForm,NotificationMiniForm,PersonalInfoRequest,PersonalInfoResponse,PersonalResponse
from Models_v1 import ClubListResponse
from Models_v1 import ProfileMiniForm,Events,Event,ModifyEvent
from Models_v1 import ClubRetrievalMiniForm,UpdateGCM,Join_Creation,AdminFeed,SuperAdminFeedResponse,SetSuperAdminInputForm,SetAdminInputForm,ChangeAdminInputForm
from CollegesAPI_v1 import getColleges,createCollege,copyToCollegeFeed, addCollegeFn, prospectiveCollegeFn
from PostsAPI import editPostFn
from PostsAPI_v1 import postEntry,postRequest,deletePost,unlikePost,likePost,commentForm,copyPostToForm,editpost,copyCommentToForm
from Models_v1 import AdminStatus,UpdateStatus,DelClubMiniForm,UpdateGCMMessageMiniForm,EditBatchMiniForm,DelProfileMiniForm,UnjoinClubMiniForm
from PostsAPI_v1 import copyPostRequestToForm,update
from EventsAPI_v1 import eventEntry,copyEventToForm,deleteEvent,attendEvent,attendeeDetails, unAttend, editEventFn,getEventsEitherSide
from ClubAPI_v1 import createClub,createClubAfterApproval,getClub,unfollowClub,approveClub,copyJoinRequestToForm,copyToSuperAdminList, \
    deleteClub,unJoinClub
from ProfileAPI_v1 import _copyProfileToForm,_doProfile,_getProfileFromEmail,changeGcm,PersonalInfoForm,deleteProfile
from V1.Helpers import collegeFeedHelper, scoreBoardHelper
from settings import ANROID_CLIENT_ID,WEB_CLIENT_ID,ANDROID_ID2,ANDROID_ID3
from gae_python_gcm.gcm import GCMMessage, GCMConnection
from Helpers import messageProp,createCollegeHelper,createClubRequestHelper,approveClubHelper,createEventHelper,createPostHelper


#data = {'message': '5 mins later',"title":"Hi RKD"}
#gcm_message = GCMMessage('cDXc7bMlwPQ:APA91bGAXV7203E6GUPkrbSOzQBv1_Xc4ztClQ6XcEcr80jw9jKBdZmLZ1U04_dTiH37AOydvv07_fBGiZXrszGkIxN5ZQgjsdqu35orSSOVq02XxDLVcBaqRMvxQTr-ucYQzbVoj5kE', data)
#gcm_conn = GCMConnection()
#gcm_conn.notify_device(gcm_message)



EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


@endpoints.api(name='campusConnectApis', version='v1',
    allowed_client_ids=[ANROID_CLIENT_ID,WEB_CLIENT_ID,API_EXPLORER_CLIENT_ID,ANDROID_ID2,ANDROID_ID3],
    scopes=[EMAIL_SCOPE])

# GETSTREAM KEY - urgm3xjebe9d

class CampusConnectApi(remote.Service):

   @endpoints.method(GetClubMiniForm,ClubMiniForm,path='getClub', http_method='GET', name='getClub')
   def getClubApi(self,request):
        print("Request entity is",request)
        retClub = ClubMiniForm()
        if request:
             retClub = getClub(request)

        return retClub

   @endpoints.method(GetClubMiniForm,PersonalInfoResponse,path='getClubMembers', http_method='GET', name='getClubMembers')
   def getClubMembersApi(self,request):
        #print("Request entity is",request)
        clubKey = ndb.Key('Club',int(request.clubId))
        club = clubKey.get()
        #print("Received Club is",club)  
        list1 = club.members
        pylist=[]
        for p in list1:
           person = p.get()
           x=PersonalInfoForm(person)
           setattr(x,'pid',str(p.id()))
           pylist.append(x)

        return PersonalInfoResponse(items = pylist)

   @endpoints.method(JoinClubMiniForm,message_types.VoidMessage,path='joinClub', http_method='POST', name='joinClubReq')
   def joinClubApi(self,request):
            
            if request:
             clubKey = ndb.Key('Club',int(request.clubId))
             club = clubKey.get()

             profileKey = ndb.Key('Profile',int(request.fromPid))
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
                     #to_pid = joinCreationObj.to_pid,
                     type = "Join Request",
                     timestamp = joinCreationObj.timestamp
                    )
                newNotif.to_pid_list.append(joinCreationObj.to_pid)

                print("Notification to be inserted in join approval",newNotif)
                newNotifKey = newNotif.put()
                 
                data = {'message': profile.name + " wishes to join","title":  club.name,
                        'id':str(joinCreationObjKey.id()),'type':"Admin"
                       }
                print (data)
                gcmId = to_pidProfile.gcmId
                gcm_message = GCMMessage(gcmId, data)
                gcm_conn = GCMConnection()
                gcm_conn.notify_device(gcm_message)
             
           
            return message_types.VoidMessage()


   @endpoints.method(RequestMiniForm,message_types.VoidMessage,path='joinClubApproval', http_method='POST', name='joinClubApproval')
   def joinClubApprovalApi(self,request):
        if request:
          
          joinCreation = ndb.Key('Join_Creation',int(request.reqId)).get()
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
                     #to_pid = joinCreation.from_pid,
                     type = "Approval Rejection",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                     
                    )
                 newNotif.to_pid_list.append(joinCreation.from_pid)


                 print("Notification to be inserted in join approval",newNotif)
                 newNotifKey = newNotif.put()
                 data = {'message': "Approval Denied","title": club.name,'id':str(club.key.id()),'type':"Club"}
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
                     #to_pid = joinCreation.from_pid,
                     type = "Approved Join Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

                 newNotif.to_pid_list.append(joinCreation.from_pid)

                 print("Notification to be inserted in join approval",newNotif)
                 newNotifKey = newNotif.put()
                 data = {'message': "You are now a member","title": currentClub.name,'id':str(currentClub.key.id()),'type':"Club"}
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

            clubKey = ndb.Key('Club',int(request.clubId))
            club = clubKey.get()

            profileKey = ndb.Key('Profile',int(request.fromPid))
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


   @endpoints.method(UnjoinClubMiniForm,message_types.VoidMessage,path='unJoinClub', http_method='POST', name='unjClub')
   def unjClub(self, request):
        """Update & return user profile."""
        ret = unJoinClub(request)

        if(ret == True):
          print("Cool")
        else:
          print("Operation not allowed")

        return message_types.VoidMessage()     

   @endpoints.method(ClubRetrievalMiniForm,ClubListResponse,path='getClubList', http_method='GET', name='getClubList')
   def getClubListApi(self,request):
        list_of_clubs = ClubListResponse()
        print("Request entity is",request)

        if request:


            collegeKey = ndb.Key('CollegeDb',int(request.collegeId))
            college = collegeKey.get()

            if(college):


                for obj in college.group_list :
                   ret_club = obj.get()
                   format_club = ClubMiniForm()
                   format_club.name = ret_club.name
                   format_club.abbreviation = ret_club.abbreviation
                   format_club.collegeName = ret_club.collegeId.get().name
                   format_club.adminName = ret_club.admin.get().name
                   format_club.description = ret_club.description
                   format_club.clubId = str(ret_club.key.id())
                   format_club.memberCount = str(len(ret_club.members))
                   format_club.followerCount = str(len(ret_club.follows))
                   format_club.photoUrl = str(ret_club.photoUrl)
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

   @endpoints.method(NotificationMiniForm,ClubListResponse,path='getClubListofAdmin', http_method='GET', name='getClubListofAdmin')
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
                   format_club.adminName = ret_club.admin.get().name
                   format_club.description = ret_club.description
                   format_club.clubId = str(ret_club.key.id())
                   format_club.isMember = "Y"
                   format_club.isFollower = "Y"
                   list_of_clubs.list.append(format_club)





               return list_of_clubs




   @endpoints.method(ClubRequestMiniForm,message_types.VoidMessage,path='club', http_method='POST', name='createClubRequest')
   def createClubRequest(self, request):

        collegeId = ndb.Key('CollegeDb',int(request.collegeId))
        print("Required College ID",collegeId)

        college_ret = collegeId.get()

        print("College Ret",college_ret)
        if(college_ret):
           club_ret = Club.query(Club.name == request.clubName).filter(Club.abbreviation == request.abbreviation).filter(Club.collegeId == college_ret.key).fetch(1)
           print("Club Ret",club_ret)
           if(len(club_ret) == 0):
              clubRequest = createClub(request)
              currentProfile = clubRequest.to_pid.get()
              newNotif = Notifications(
                     clubName = clubRequest.club_name,
                     clubphotoUrl = clubRequest.photoUrl,
                     #to_pid = clubRequest.to_pid,
                     type = "Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              newNotif.to_pid_list.append(clubRequest.to_pid)

              print("Notification to be inserted in club creation request",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': clubRequest.club_name,"title": "Creation Request",'id':str(clubRequest.key.id()),'type':"Admin"}
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

        clubRequest = ndb.Key('Club_Creation',int(request.reqId))
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
                     #to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

            newNotif.to_pid_list.append(req.from_pid)
            print("Notification to be inserted in club approval rejection",newNotif)
            newNotifKey = newNotif.put()
            data = {'message': req.club_name,"title": "Creation Request Denied",'id':"None",'type':"None"}
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
                     #to_pid = newClub.admin,
                     type = "Approved Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )
                  newNotif.to_pid_list.append(newClub.admin)

              print("Notification to be inserted in club approval ",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': newClub.name,"title": "Creation Request Approved",
                      'id':str(newClub.key.id()),'type':"Club"}
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
                     #to_pid = req.from_pid,
                     type = "Rejected Club Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    )

              newNotif.to_pid_list.append(req.from_pid)

              print("Notification to be inserted in club approval rejection",newNotif)
              newNotifKey = newNotif.put()
              data = {'message': req.club_name,"title": "Creation Request Denied",
                      'id':"None",'type':"None"}
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
                     #to_pid = clubRequest.to_pid,
                     type = "Post Creation Request",
                     timestamp  = dt.datetime.now().replace(microsecond = 0)
                    
                    )
        newNotif.to_pid_list.append(clubRequest.to_pid)

        print("Notification to be inserted in Post Creation Request",newNotif)
        newNotifKey = newNotif.put()
        data = {'message': clubRequest.title,"title": "Post Creation Request",
                'id':str(clubRequest.key.id()),'type':"Admin"}
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
            person_key = ndb.Key('Profile',int(request.fromPid))

            profile = person_key.get()
            collegeId = profile.collegeId
            print(profile)
            club_key = ndb.Key('Club',int(request.clubId))
            if club_key in profile.clubsJoined:
                    print "Present"
                    newPost = postEntry(request,flag)

                    print("NEW POST",newPost)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    #Create Notification Feed
                    group = newPost.club_id.get()
                    groupName = group.name
                    data = {'message': groupName,"title": newPost.title,
                            'id':str(newPost.key.id()),'type':"Post"}
                    
                    
                    postlist = []
                    if (group.follows):
                      newNotif = Notifications(
                                      clubName = groupName,
                                      clubId = newPost.club_id,
                                      clubphotoUrl = group.photoUrl,
                                      postName = newPost.title,
                                      postId = newPost.key,
                                      timestamp = newPost.timestamp,
                                      type = "Post",
                                      #to_pid = pid
                                      )
                      for pid in group.follows:
                           person = pid.get()
                           print ("PID is",person)
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             postlist.append(gcmId)
                             newNotif.to_pid_list.append(pid)
                           #newNotif = Notifications(
                           #          clubName = groupName,
                           #           clubId = newPost.club_id,
                           #           clubphotoUrl = group.photoUrl,
                           #           postName = newPost.title,
                           #           postId = newPost.key,
                           #           timestamp = newPost.timestamp,
                           #           type = "Post",
                           #           to_pid = pid
                           #           )

                      print("Notification to be inserted",newNotif)
                      newNotifKey = newNotif.put()  

                           
                    dummyRequest = GetInformation()
                    dummyRequest.collegeId = str(collegeId.id())
                    dummyRequest.pid = "123432"
                    collegeFeedHelper(dummyRequest,0,newPost)
                    
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
        newList = []
        colleges = CollegeDb.query()
        for x in colleges:
          if(str(x.key.id()) != '5720605454237696' and str(x.key.id()) != '5743114304094208'):
             newList.append(x)

        return Colleges(collegeList=[getColleges(x) for x in newList])




   @endpoints.method(EventMiniForm,MessageResponse,path='eventEntry', http_method='POST', name='eventEntry')
   def createEvent(self, request):
        response = MessageResponse()
        print("Entered Event Entry Portion")
        
        try:
            person_key = ndb.Key('Profile',int(request.eventCreator))
            print(person_key)
            profile = person_key.get()
            collegeId = profile.collegeId
            club_key = ndb.Key('Club',int(request.clubId))
            if club_key in profile.clubsJoined:
                    print "GOING INTO EVENTS ENTRY"
                    newEvent = eventEntry(request)

                    temp = datetime.strptime(getattr(request,"startDate"),"%Y-%m-%d").date()
                    temp1 = datetime.strptime(getattr(request,"startTime"),"%H:%M:%S").time()
                    start = datetime.combine(temp,temp1)


                    temp = datetime.strptime(getattr(request,"endDate"),"%Y-%m-%d").date()
                    temp1 = datetime.strptime(getattr(request,"endTime"),"%H:%M:%S").time()

                    end = datetime.combine(temp,temp1)

                    if start > end:
                        response.status = "2"
                        response.text = "Could not insert"
                        return response

                    response.status = "1"
                    response.text = "Inserted into events Table"
                    group = newEvent.club_id.get()
                    groupName = group.name

                    

                    data = {'message': groupName,"title": newEvent.title,
                           'id':str(newEvent.key.id()),'type':"newEvent"}
                    #get the followers of the club pids. Get GCM Id's from those and send
                    print ("GROUP FOLLOWS LIST ", group.follows)

                    dummyRequest = GetInformation()
                    dummyRequest.collegeId = str(collegeId.id())
                    dummyRequest.pid = "123432"
                    collegeFeedHelper(dummyRequest,0,newEvent)

                    eventlist = []
                    if (group.follows):
                        newNotif = Notifications(
                                        clubName = groupName,
                                        clubId = newEvent.club_id,
                                        clubphotoUrl = group.photoUrl,
                                        eventName = newEvent.title,
                                        eventId = newEvent.key,
                                        timestamp = newEvent.timestamp,
                                        type = "Event",
                                        #to_pid = pid
                                        )
                       


                        for pid in group.follows:
                           person = pid.get()
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             eventlist.append(gcmId)
                             newNotif.to_pid_list.append(pid)
                           #newNotif = Notifications(
                           #             clubName = groupName,
                           #             clubId = newEvent.club_id,
                           #             clubphotoUrl = group.photoUrl,
                           #             eventName = newEvent.title,
                           #             eventId = newEvent.key,
                           #             timestamp = newEvent.timestamp,
                           #             type = "Event",
                           #             to_pid = pid
                           #             )
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

   @endpoints.method(GetAllPosts,CollegeFeed,path='getPosts', http_method='GET', name='getPosts')
   def getPosts(self, request):
        print("Entered Get Posts Portion")
        temp = request.collegeId
        temp2 = request.clubId
        pid = ndb.Key('Profile',int(request.pid))
        print "temp" + str(temp)
        print "temp2" + str(temp2)

        if request.postId is not None:
            postId = ndb.Key('Post',int(request.postId))
            post = postId.get() #IMprove this with try catch later
            return CollegeFeed(items=list(([copyToCollegeFeed(pid,post)])))

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

        return CollegeFeed(items=list(([copyToCollegeFeed(pid,x) for x in posts])))
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
       print "Entered the comments Section"
       return commentForm(request)
       return message_types.VoidMessage()

   @endpoints.method(ProfileRetrievalMiniForm, ProfileResponse,
            path='profile', http_method='GET', name='getProfile')
   def getProfile(self, request):
        """Return user profile."""
        email=getattr(request,"email")
        pid = ndb.Key('Profile',int(request.pid))
        profile = pid.get()
        #result = Profile.query(Profile.email==email)
        present =0
        isAdmin="N"
        isSuperAdmin="N"
        #for y in result:
            #if y.email == email:
        if profile:        
            present = 1
            if profile.admin is not None:
                    if len(profile.admin)>0:
                        isAdmin="Y"
            if profile.superadmin is not None:
                    if len(profile.superadmin)>0:
                        isSuperAdmin="Y"
        if present ==1:
            success="True"
            a = _doProfile(profile.email)
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
            path='getPostRequests', http_method='GET', name='getPostRequests')
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

   @endpoints.method(GetAllPosts,CollegeFeed,path='getEvents', http_method='GET', name='getEvents')
   def getEvents(self, request):
        print("Entered Get Events Portion")
        temp = request.collegeId
        temp2 = request.clubId
        date = request.date
        future_date = request.futureDate
        pid = ndb.Key('Profile',int(request.pid))

        if request.postId is not None:
            postId = ndb.Key('Event',int(request.postId))
            event = postId.get()
            return CollegeFeed(items=list(([copyToCollegeFeed(pid,event)])))

        #person = pid.get()

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
           return CollegeFeed(items=list(([copyToCollegeFeed(pid,x) for x in finalList])))
        elif(date != None):
           for x in events:
              start_date = str(x.start_time.date())
              if(start_date == date):
                 finalList.append(x)
           print("Returning all events from Final List")
           return CollegeFeed(items=list(([copyToCollegeFeed(pid,x)  for x in finalList])))
        else:
           print("Returning all events from Events List")
           return CollegeFeed(items=list(([copyToCollegeFeed(pid,x)  for x in events])))

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

   @endpoints.method(GetInformation,CollegeFeed,path='mainFeed', http_method='GET', name='collegeFeed')
   def collegeFeed(self, request):
       flag = 1
       cf = collegeFeedHelper(request,flag)
       #return CollegeFeed(items=[copyToCollegeFeed(x) for x in events])
       return cf


   @endpoints.method(GetInformation,CollegeFeed,path='myFeed', http_method='GET', name='personalFeed')
   def personalFeed(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       profile = pid.get()
       posts = []
       events = []
       pylist = []
       pylist2 = []
       pageLimit = 10
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
               list1.append(copyToCollegeFeed(pid,y))

               #iteration+=1
               #if(iteration==upperBound):
               #    break

           iteration=0

           for z in events:
               #if(iteration>=skipCount and iteration<upperBound):
                list1.append(copyToCollegeFeed(pid,z))
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

   @endpoints.method(GetInformation,AdminFeed,path='adminFeed', http_method='GET', name='adminFeed')
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
   @endpoints.method(GetInformation,SuperAdminFeedResponse,path='superAdminFeed', http_method='GET', name='superAdminFeed')
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
       #notificationslist = Notifications.query(Notifications.to_pid.IN([pid])).order(-Notifications.timestamp)
       listresponse = NotificationList()

       for obj in notificationslist:
          newListObj = NotificationResponseForm()
             
          if( pid == obj.to_pid):

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

   @endpoints.method(NotificationMiniForm,NotificationList,path='myNotificationsMod', http_method='POST', name='myNotificationFeedMod')
   def myNotificationFeedMod(self, request):
       pid = ndb.Key('Profile',int(request.pid))
       #notificationslist = Notifications.query(Notifications.to_pid == pid).order(-Notifications.timestamp).fetch()
       notificationslist = Notifications.query(Notifications.to_pid_list.IN([pid])).order(-Notifications.timestamp)
       listresponse = NotificationList()

       for obj in notificationslist:
          newListObj = NotificationResponseForm()
             
          if( pid in obj.to_pid_list):

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










   @endpoints.method(PersonalInfoRequest,PersonalInfoResponse,path='personalInfo', http_method='GET', name='personalInfo')
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
   
   @endpoints.method(ChangeAdminInputForm,message_types.VoidMessage,path='changeAdmin', http_method='POST', name='changeAdmin')
   def changeAdmin(self,request):
       clubKey = ndb.Key('Club',int(request.clubId))
       currentAdminCheckKey = ndb.Key('Profile',int(request.currentAdminCheckId))
       currentAdmincheck = currentAdminCheckKey.get()  
       newAdminKey = ndb.Key('Profile',int(request.newAdminId))
       club = clubKey.get()
       currentAdmin = club.admin.get()
       newAdmin = newAdminKey.get()

       
       if(newAdmin and currentAdmincheck == currentAdmin):
         club.admin = newAdminKey
         newAdmin.admin.append(clubKey)
         currentAdmin.admin.remove(clubKey)
         #Check if newAdmin is not a member or a follower
         if(newAdminKey not in club.follows):
            club.follows.append(newAdminKey)
         if(newAdminKey not in club.members):
            club.members.append(newAdminKey)
         if(clubKey not in newAdmin.clubsJoined):
            newAdmin.clubsJoined.append(clubKey)   

         club.put()
         newAdmin.put()
         currentAdmin.put()


       return message_types.VoidMessage()

   @endpoints.method(ProfileRetrievalMiniForm,AdminStatus,path='adminStatus', http_method='GET', name='adminStatus')
   def adminStatus(self,request):
       profileKey = ndb.Key('Profile',int(request.pid))
       person = profileKey.get()
       isAdmin="N"
       isSuperAdmin="N"
       if person.admin is not None:
            if len(person.admin)>0:
                isAdmin="Y"
       if person.superadmin is not None:
            if len(person.superadmin)>0:
                isSuperAdmin="Y"

       return AdminStatus(isSuperAdmin=isSuperAdmin,isAdmin=isAdmin)


   @endpoints.method(message_types.VoidMessage,UpdateStatus,path='updateStatus', http_method='GET', name='updateStatus')
   def updateStatus(self,request):
       update="5"
       return UpdateStatus(update=update,message="Incident Update")

   @endpoints.method(DelClubMiniForm,message_types.VoidMessage,path='delClub', http_method='POST', name='delClub')
   def delClub(self,request):
       deleteClub(request)
       return message_types.VoidMessage()

   @endpoints.method(DelProfileMiniForm,message_types.VoidMessage,path='delProfile', http_method='POST', name='delProfile')
   def delProfile(self,request):
       deleteProfile(request)
       return message_types.VoidMessage()    

   @endpoints.method(GetInformation,PersonalInfoResponse,path='getAttendeeDetails', http_method='GET', name='getAttendeeDetails')
   def getAttendeeDetails(self,request):
        eventId = ndb.Key('Event',int(request.eventId))
        return attendeeDetails(eventId)

   @endpoints.method(GetInformation,CommentsResponse,path='getComments', http_method='GET', name='getComments')
   def getComments(self,request):
       postId = ndb.Key('Post',int(request.postId))
       pageLimit = 25
       skipCount=0
       upperBound=pageLimit
       print request.pageNumber

       try:
        skipCount = (int(request.pageNumber)-1)*pageLimit
        upperBound = int(request.pageNumber)*pageLimit
       except:
          print "Didnt give pageNumber-Default to 1"

       q = Comments.query(Comments.postId==postId)
       pylist=[]
       for x in q:
           pylist.append(copyCommentToForm(x))

       pylist.sort(key=lambda x: x.timestamp, reverse=True)

       finalList = []
       for i in xrange(skipCount,upperBound):
           if(i>=len(pylist)):
            break
           finalList.append(pylist[i])

       cf = CommentsResponse()
       cf.items = finalList
       cf.completed=str(0)
       if(upperBound>=len(pylist)):
                cf.completed=str(1)


       return cf

   @endpoints.method(LikePost,message_types.VoidMessage,path='unAttendEvent', http_method='POST', name='unAttendEvent')
   def unAttendEvent(self,request):
       unAttend(request)
       return message_types.VoidMessage()
   @endpoints.method(UpdateGCMMessageMiniForm,message_types.VoidMessage,path='propUpdate', http_method='POST', name='propUpdate')
   def propUpdate(self,request):
      if(request.id == None):
          data = {'message': request.message,"title": request.title,
                           'id':'None','type':request.type}
      else:
          data = {'message': request.message,"title": request.title,
                           'id':request.id,'type':request.type}
      print data             

      if(request.batch != None):# and request.type == "BatchRequest"):
          #sending GCM message to a batch
          print "Entered batch in campusConnectApis"
          

          messageProp(request.batch,data)
      else :
          #send message to everyone
          print "Entered none in campusConnectApis"
          
          messageProp(None,data) 
      return message_types.VoidMessage()
    
   @endpoints.method(EditBatchMiniForm,message_types.VoidMessage,path='modifyBatch', http_method='POST', name='modifyBatch')
   def modifyBatch(self,request):
        profileList = Profile.query(Profile.batch == request.fromBatch,Profile.isAlumni == "N") 

        if(profileList):
           for profile in profileList:
               print profile.batch 

               profile.batch = request.toBatch
               profile.put() 
        
        return message_types.VoidMessage()   


   @endpoints.method(message_types.VoidMessage,BDCommentResponse,path='BDCommentCount', http_method='GET', name='BDCommentCount')
   def propUpBDCommentCountdate(self,request):
       #query = BDComments.query(BDComments.commentHashTag == request.commentHashTag)
       count = 0
       #for q in query:
       stateList = ['#GJ','#RJ','#BR','#UP','#MP','#UB','#KA','#KR','#AP','#TS','#MH','#NE','#TN','#WB']
       pylist = []
       for x in stateList:
           query = BDComments.query(BDComments.commentHashTag ==x)
           count = 0
           BD = BDCommentCount()
           for q in query:
                count+=1
           BD.commentHashTag=x
           BD.count=str(count)
           pylist.append(BD)

       return BDCommentResponse(items=pylist)

   @endpoints.method(GetInformation,MiscCount,path='clubCount', http_method='GET', name='clubCount')
   def clubCount(self,request):

       collegeId = ndb.Key('CollegeDb',int(request.collegeId))

       query = Club.query(Club.collegeId==collegeId)
       print query
       Count = 0

       for q in query:

           Count+=1



       return MiscCount(count=str(Count))

   @endpoints.method(GetInformation,MiscCount,path='eventCount', http_method='GET', name='eventCount')
   def eventCount(self,request):
       collegeId = ndb.Key('CollegeDb',int(request.collegeId))
       date = request.date
       Count = 0
       events = Event.query(Event.collegeId==collegeId)
       for x in events:
              start_date = str(x.start_time.date())
              if(start_date == date):
                 Count+=1

       return MiscCount(count=str(Count))


   @endpoints.method(GetInformation,message_types.VoidMessage,path='delComment', http_method='POST', name='delComment')
   def delComment(self,request):
        personId = ndb.Key('Profile',int(request.pid))
        commentId = ndb.Key('Comments',int(request.commentId))

        person = personId.get()
        comment = commentId.get()
        post = comment.postId.get()

        supEmail = post.collegeId.get().sup_emailId
        query = Profile.query(Profile.email==supEmail)
        supKey=  ""
        for q in query:
            supKey = q.key

        if comment.pid == personId or personId == post.from_pid or personId == supKey:
            commentId.key.delete()


   @endpoints.method(message_types.VoidMessage,message_types.VoidMessage,path='testAllInOne', http_method='POST', name='testAllInOne')
   def testAllInOne(self,request):
        requestforcreatecollege = CollegeDbMiniForm()
        requestforcreatecollege.name = "testAllInOneCollege"
        requestforcreatecollege.abbreviation = "TAIOC"
        requestforcreatecollege.location = "Surathkal"
        requestforcreatecollege.studentSup = "TAIOCSUP"
        requestforcreatecollege.alumniSup = "TAIOCASUP"
        requestforcreatecollege.email = "TAIOCSUP@gmail.com"
        requestforcreatecollege.phone = "9228019230"
        collegeReq = createCollegeHelper(requestforcreatecollege)
        #Create college along with sup_profile is done
        
        t.sleep(20)


        college = CollegeDb.query(CollegeDb.sup_emailId == requestforcreatecollege.email).fetch()
        profile = Profile.query(Profile.email == requestforcreatecollege.email).fetch()
        #print college.key
        print ("College is",college)
        for x in college:
           print "entered here"
           print x.key.id()
           collegeId = x.key.id()

        for x in profile:
           print "Entered Profile"
           print x.key.id()
           profileId = x.key.id()   
           
        

        requestforcreateclubrequest =  ClubRequestMiniForm()
        requestforcreateclubrequest.clubName = "TAIOCClub"
        requestforcreateclubrequest.abbreviation = "TAIOCC"
        requestforcreateclubrequest.description = "TAIOCC CLub for test script testing"
        requestforcreateclubrequest.fromPid = str(profileId)
        requestforcreateclubrequest.collegeId = str(collegeId)
        requestforcreateclubrequest.photoUrl = "TAIOCCPHOTOURL"


        clubReq = createClubRequestHelper(requestforcreateclubrequest)

        t.sleep(20)
        #Club Request has been created. Now the request needs to be approved

        clubcreation = Club_Creation.query(Club_Creation.abbreviation == requestforcreateclubrequest.abbreviation).fetch()

        for x in clubcreation:
            reqId = str(x.key.id())

        requestforapproverequest = RequestMiniForm()
        requestforapproverequest.reqId = reqId
        requestforapproverequest.action = "Y"
        
        approveclub = approveClubHelper(requestforapproverequest) 

        #Club has been created

        t.sleep(20)

        club = Club.query(Club.abbreviation == requestforcreateclubrequest.abbreviation).fetch()
        for x in club :
            clubId = str(x.key.id())
        

        #Creating 2 Events and 2 Posts
        evententryrequest1 = EventMiniForm()
        evententryrequest1.title = "TAIOCC Event1"
        evententryrequest1.description = "First test event"
        evententryrequest1.photoUrl = "TAIOCCE1PhotoUrl"
        evententryrequest1.clubId = clubId
        evententryrequest1.venue = "Surathkal"
        evententryrequest1.startDate = "2016-03-08"
        evententryrequest1.startTime = "06:00:00"
        evententryrequest1.endDate = "2016-03-12"
        evententryrequest1.endTime = "10:00:00"
        evententryrequest1.completed = "N"
        evententryrequest1.isAlumni = "N"
        evententryrequest1.eventCreator = str(profileId)
        evententryrequest1.date = "2016-03-12"
        evententryrequest1.time = "04:00:00"
        evententryrequest1.tags = ["TAG-1","TAG-2"]
        evententry1 = createEventHelper(evententryrequest1)
        
        evententryrequest2 = EventMiniForm()
        evententryrequest2.title = "TAIOCC Event2"
        evententryrequest2.description = "Second test event"
        evententryrequest2.photoUrl = "TAIOCCE2PhotoUrl"
        evententryrequest2.clubId = clubId
        evententryrequest2.venue = "Surathkal"
        evententryrequest2.startDate = "2016-03-12"
        evententryrequest2.startTime = "06:00:00"
        evententryrequest2.endDate = "2016-03-12"
        evententryrequest2.endTime = "10:00:00"
        evententryrequest2.completed = "N"
        evententryrequest2.isAlumni = "N"
        evententryrequest2.eventCreator = str(profileId)
        evententryrequest2.date = "2016-03-12"
        evententryrequest1.tags = ["TAG-3","TAG-4"]
        evententryrequest2.time = "04:00:00"
        
        evententry2 = createEventHelper(evententryrequest2)


           
        postentryrequest1 = PostMiniForm()
        postentryrequest1.fromPid = str(profileId)
        postentryrequest1.clubId = clubId
        postentryrequest1.title = "TAIOCC Post 1"
        postentryrequest1.description = "First Test Post"
        postentryrequest1.date = "2016-03-12"
        postentryrequest1.time = "04:00:00"
        postentryrequest1.photoUrl = "TAIOCCP1PhotoUrl"
        postentryrequest1.tags = ["TAG-1","TAG-2"]
        
        postentry1 = createPostHelper(postentryrequest1)

        postentryrequest2 = PostMiniForm()
        postentryrequest2.fromPid = str(profileId)
        postentryrequest2.clubId = clubId
        postentryrequest2.title = "TAIOCC Post 2"
        postentryrequest2.description = "Second Test Post"
        postentryrequest2.date = "2016-03-12"
        postentryrequest2.time = "04:00:00"
        postentryrequest2.photoUrl = "TAIOCCP2PhotoUrl"
        postentryrequest2.tags = ["TAG-3","TAG-4"]
        
        postentry2 = createPostHelper(postentryrequest2)
        

        



        return message_types.VoidMessage()  






   @endpoints.method(PostMiniForm,MessageResponse,path='editPost', http_method='POST', name='editPost')
   def editPost(self,request):
        response = MessageResponse()
        print("Entered Post Entry Portion")
        flag=0
        try:
            person_key = ndb.Key('Profile',int(request.fromPid))

            profile = person_key.get()
            collegeId = profile.collegeId

            postId = ndb.Key('Post',int(request.postId))
            post = postId.get()

            if post.from_pid != person_key:
                print "Error"
                response.status = "3"
                response.text = "Can't edit this post"
                return response

            print(profile)

            club_key = ndb.Key('Club',int(request.clubId))
            if club_key in profile.clubsJoined:
                    print "Present"
                    newPost = editPostFn(request,post)

                    print("NEW POST",newPost)
                    response.status = "1"
                    response.text = "Inserted into Posts Table"
                    #Create Notification Feed
                    group = newPost.club_id.get()
                    groupName = group.name
                    data = {'message': groupName,"title": newPost.title,
                            'id':str(newPost.key.id()),'type':"Post"}


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


                    dummyRequest = GetInformation()
                    dummyRequest.collegeId = str(collegeId.id())
                    dummyRequest.pid = "123432"
                    collegeFeedHelper(dummyRequest,0,newPost,"Y")

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

   @endpoints.method(EventMiniForm,MessageResponse,path='editEvent', http_method='POST', name='editEvent')
   def editEvent(self,request):
        response = MessageResponse()
        print("Entered Event Entry Portion")

        try:
            person_key = ndb.Key('Profile',int(request.eventCreator))
            print(person_key)
            profile = person_key.get()
            collegeId = profile.collegeId
            club_key = ndb.Key('Club',int(request.clubId))
            eventId = ndb.Key('Event',int(request.eventId))
            event = eventId.get()


            if event.event_creator != person_key:
                print "Error"
                response.status = "3"
                response.text = "Can't edit this post"
                return response


            if club_key in profile.clubsJoined:
                    print "GOING INTO EVENTS ENTRY"

                    newEvent = editEventFn(request,event)

                    temp = datetime.strptime(getattr(request,"startDate"),"%Y-%m-%d").date()
                    temp1 = datetime.strptime(getattr(request,"startTime"),"%H:%M:%S").time()
                    start = datetime.combine(temp,temp1)


                    temp = datetime.strptime(getattr(request,"endDate"),"%Y-%m-%d").date()
                    temp1 = datetime.strptime(getattr(request,"endTime"),"%H:%M:%S").time()

                    end = datetime.combine(temp,temp1)

                    if start > end:
                        response.status = "2"
                        response.text = "Could not insert"
                        return response

                    response.status = "1"
                    response.text = "Inserted into events Table"
                    group = newEvent.club_id.get()
                    groupName = group.name



                    data = {'message': "Details of event have been changed","title": newEvent.title,
                           'id':str(newEvent.key.id()),'type':"newEvent"}
                    #get the followers of the club pids. Get GCM Id's from those and send
                    print ("GROUP FOLLOWS LIST ", group.follows)

                    dummyRequest = GetInformation()
                    dummyRequest.collegeId = str(collegeId.id())
                    dummyRequest.pid = "123432"
                    collegeFeedHelper(dummyRequest,0,newEvent,"Y")

                    eventlist = []
                    if (group.follows):
                        for pid in group.follows:
                           person = pid.get()
                           gcmId = person.gcmId
                           if (gcmId):
                             print ("GCM ID is",gcmId)
                             eventlist.append(gcmId)
                           #newNotif = Notifications(
                           #             clubName = groupName,
                           #             clubId = newEvent.club_id,
                           #             clubphotoUrl = group.photoUrl,
                           #             eventName = newEvent.title,
                           #             eventId = newEvent.key,
                           #             timestamp = newEvent.timestamp,
                           #             type = "Event",
                                        #to_pid = pid
                           #             )
                           #print("Notification to be inserted",newNotif)
                           #newNotifKey = newNotif.put()





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


   @endpoints.method(KMCScoreHandler,message_types.VoidMessage,path='kmcScoreUpdate', http_method='POST', name='kmcScoreUpdate')
   def kmcScoreUpdate(self,request):
       scoreCategories = ["ONE","TWO","THREE","FOUR","FIVE","SIX"]
       print "Reached here"
       #t.sleep(10)
       print "FILE PATH " + os.getcwd()
       #f = open(os.getcwd()+'/V1/KMC/scores.txt','w')
       for x in request.items:
           ob = KMCScoreModel()
           ob.batch = str(x.batch)
           ob.score = str(x.score)
           query = KMCScoreModel.query(KMCScoreModel.batch==x.batch.upper())
           print "QUERY IS",query
           count = 0
           for q in query:
               count+=1
           if count == 0:
               ob.put()
           else:
               for q in query:
                   q.score = ob.score
                   q.put()



       return message_types.VoidMessage()


   @endpoints.method(message_types.VoidMessage,KMCScoreHandler,path='kmcScoreQuery', http_method='GET', name='kmcScoreQuery')
   def kmcScoreQuery(self,request):
       query = KMCScoreModel.query()
       pylist = []
       for q in query:
           ob = KMCScore()
           ob.batch = q.batch
           ob.score = q.score
           pylist.append(ob)

       return KMCScoreHandler(items=pylist)

   @endpoints.method(AddCollegeForm,MessageResponse,path='addCollege', http_method='POST', name='addCollege')
   def addCollege(self,request):
        mr = MessageResponse()

        status = addCollegeFn(request)
        if status == 1:
            mr.status = "2"
            mr.text = "Already Existing Record"
        else:
            mr.status = "1"
            mr.text = "Inserted"

        return mr

   @endpoints.method(message_types.VoidMessage,ProspectiveColleges,path='prospectiveColleges', http_method='GET', name='prospectiveColleges')
   def prospectiveColleges(self,request):

       return prospectiveCollegeFn()
   @endpoints.method(GetEventsEitherSideMiniForm,GetEventsResponse,path='getEventsES', http_method='GET', name='getEventsES')
   def getEventsES(self,request):
       return getEventsEitherSide(request) 

   


   @endpoints.method(LiveCommentsForm,message_types.VoidMessage,path='liveComments', http_method='POST', name='liveComments')
   def liveComments(self,request):
       ob = LiveComments()
       for field in request.all_fields():
           if field.name == "timestamp":
                timestampdatetime = dt.datetime.strptime(request.timestamp, '%Y-%m-%d %H:%M:%S')
                setattr(ob,field.name,timestampdatetime)    
           elif field.name == "collegeId":
               collegeId = ndb.Key('CollegeDb',int(request.collegeId))
               setattr(ob,field.name,collegeId)

           elif field.name == "personPhotoUrl":
               setattr(ob,field.name,str(getattr(request,field.name)))

           else:
            setattr(ob,field.name,getattr(request,field.name))


       

       if getattr(request,"reportCount") is None:
           ob.reportCount = 0

       ob.put()

       #print "REPORT COUNT ", getattr(request,"reportCount")

       return message_types.VoidMessage()


   @endpoints.method(GetInformation,LiveCommentsResponse,path='liveCommentsFeed', http_method='GET', name='liveCommentsFeed')
   def liveCommentsFeed(self,request):

       flag =0
       pageLimit = 150
       skipCount=0
       upperBound=pageLimit

       collegeId = ndb.Key('CollegeDb',int(request.collegeId))


       try:
        skipCount = (int(request.pageNumber)-1)*pageLimit
        upperBound = int(request.pageNumber)*pageLimit

       except:
          print "Didnt give pageNumber-Default to 1"

       pylist = []
       #query = LiveComments.query(LiveComments.collegeId==collegeId,LiveComments.reportcount<3).order(-LiveComments.timestamp)
       query = LiveComments.query(LiveComments.collegeId==collegeId,LiveComments.reportCount<3)
       for q in query:
            ob = LiveCommentsForm()
            for field in ob.all_fields():
                if field.name == "date" or field.name == "time":
                    #setattr(ob,"date", str(q.timestamp.strftime("%Y-%m-%d")))
                    #setattr(ob, "time", str(q.timestamp.strftime("%H:%M:%S")))
                    continue

                elif field.name == "tags":
                    setattr(ob,field.name,getattr(q,field.name))

                elif field.name == "messageId":
                    setattr(ob,field.name,str(q.key.id()))

                elif field.name == "collegeId":
                    setattr(ob,field.name,str(q.collegeId.id()))

                elif field.name == "reportCount":
                    #setattr(ob,field.name,int(q.reportCount))
                    continue
                else:
                    setattr(ob,field.name,str(getattr(q,field.name)))

            pylist.append(ob)


       pylist.sort(key=lambda x: x.timestamp, reverse=True)
       finalList = []
       for i in xrange(skipCount,upperBound):
           if(i>=len(pylist)):
            break
           finalList.append(pylist[i])

       cf = LiveCommentsResponse()
       cf.items = finalList
       cf.completed=str(0)
       if(upperBound>=len(pylist)):
                cf.completed=str(1)


       return cf

   @endpoints.method(SlamDunkScoreBoardForm,message_types.VoidMessage,path='scoreboardForm', http_method='POST', name='scoreboardForm')
   def scoreboardForm(self,request):
       return scoreBoardHelper(request)

   @endpoints.method(message_types.VoidMessage,ScoreResponse,path='scoreBoard', http_method='GET', name='scoreBoard')
   def scoreBoard(self,request):
       ob = SlamDunkScoreBoardForm()
       pylist=[]
       query = SlamDunkScoreBoard.query(SlamDunkScoreBoard.completed=="N")
       for q in query:
            ob = SlamDunkScoreBoardForm()
            for field in ob.all_fields():
                print field.name
                if hasattr(q,field.name):
                   setattr(ob,field.name,getattr(q,field.name))
                elif field.name == "matchId":
                   print "MATCH ID"
                   setattr(ob,field.name,str(q.key.id()))

            pylist.append(ob)

       return ScoreResponse(items = pylist)


   @endpoints.method(GetInformation,message_types.VoidMessage,path='reportApi', http_method='POST', name='reportApi')
   def reportApi(self,request):
       try:
           messageId = ndb.Key('LiveComments',int(request.messageId))
           message = messageId.get()
           message.reportCount+=1
           message.put()

           response = MessageResponse()
           response.status = "1"
           response.text = "Reported"

       except:
           response.status = "2"
           response.text = "Not Reported"

       return message_types.VoidMessage()


   @endpoints.method(SubscribeMatch,message_types.VoidMessage,path='subscribeMatch', http_method='POST', name='subscribeMatch')
   def subscribeMatch(self,request):
       matchId = ndb.Key('SlamDunkScoreBoard',int(request.matchId))
       pid = ndb.Key('Profile',int(request.pid))

       match = matchId.get()
       match.subscribers.append(pid)
       match.put()

       return message_types.VoidMessage()


   @endpoints.method(SubscribeMatch,message_types.VoidMessage,path='unsubscribeMatch', http_method='POST', name='unsubscribeMatch')
   def unsubscribeMatch(self,request):
       matchId = ndb.Key('SlamDunkScoreBoard',int(request.matchId))
       pid = ndb.Key('Profile',int(request.pid))

       match = matchId.get()
       if pid in match.subscribers:
        match.subscribers.remove(pid)
        match.put()

       return message_types.VoidMessage()


# api = endpoints.api_server([CampusConnectApi])   # register API
   @endpoints.method(message_types.VoidMessage,message_types.VoidMessage,path='profileCount', http_method='POST', name='profileCount')
   def profileCount(self,request):
       colleges = CollegeDb.query()

       for college in colleges:
           length = 0
           profiles = Profile.query(Profile.collegeId == college.key)

           for profile in profiles:
               length = length+1
           college.student_count = length
           college.put()
       






       return message_types.VoidMessage() 
