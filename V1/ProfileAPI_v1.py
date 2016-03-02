__author__ = 'rohit'
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models_v1 import Profile,ProfileMiniForm,CollegeDb,Club,ClubMiniForm,UpdateGCM,PersonalResponse,Post,Event,Club_Creation,Join_Creation,Post_Request,Join_Request,Comments,Notifications, LikePost, ModifyEvent
#from EventsAPI_v1 import deleteEvent
#from PostsAPI_v1 import deletePost

def _copyProfileToForm(prof):
        pf = ProfileMiniForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                if field.name=='collegeId':
                    collegeId=getattr(prof,field.name)
                    print "College Id"
                    print collegeId
                    setattr(pf,field.name,str(collegeId.id()))
                elif field.name=='clubsJoined':
                    pylist=[]
                    for x in prof.clubsJoined:
                        pylist.append(str(x.id()))
                        setattr(pf, field.name, pylist)
                elif field.name=='follows':
                    pylist=[]
                    for x in prof.follows:
                        pylist.append(str(x.id()))
                        setattr(pf, field.name, pylist)
                elif field.name=='pid':
                    setattr(pf, field.name, str(prof.key.id()))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
            else:
                if field.name=='clubNames':
                    pylist=[]
                    for x in prof.clubsJoined:
                        ret_club = x.get()
                        #ret_club = obj.get()
                        format_club = ClubMiniForm()
                        format_club.name = ret_club.name
                        format_club.abbreviation = ret_club.abbreviation
                        format_club.adminName = ret_club.admin.get().name
                        format_club.collegeName = ret_club.collegeId.get().name
                        format_club.description = ret_club.description
                        format_club.clubId = str(ret_club.key.id())
                        pylist.append(format_club)
                    setattr(pf, field.name, pylist)

                if field.name=='followsNames':
                    pylist=[]
                    for x in prof.follows:
                        clubs = x.get()
                        pylist.append(clubs.name)
                    setattr(pf, field.name, pylist)

                if field.name=='pid':
                    setattr(pf, field.name, str(prof.key.id()))

        pf.check_initialized()
        return pf


def _getProfileFromEmail(email):
        user_id=Profile.query(Profile.email==email).fetch(1)
        if len(user_id)>0:
            print "User Existed"            
            return user_id[0]
            
        else:
            print "New User"
            return Profile(name = '',
                           email = '',
                           phone = '',
                           isAlumni='N',
                           )
    

def _doProfile(email,save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        print ("Here Bitch")

        prof = _getProfileFromEmail(email)
        print ("Profile is",prof)

        if(prof.email == ''):
           key = None 
        else:
           key = prof.key
           print key   
        flag=0
        college = CollegeDb()
        print ("Save Request",save_request)
        

        if save_request:
            print ("Entered here")
            pf = ProfileMiniForm()
            for field in pf.all_fields():
                #collegeLocation=getattr(save_request,'collegeLocation')
                #print collegeLocation,"is location"
                if field.name=='followsNames' or field.name=='follows' or field.name=='clubsJoined' or field.name=='club_names':
                    continue

                if hasattr(save_request, field.name):
                    val = getattr(save_request, field.name)

                

                    if field.name is 'collegeId':
                        #college=CollegeDb.query(CollegeDb.name==val,CollegeDb.location==collegeLocation).fetch()
                        collegeId = ndb.Key('CollegeDb',int(val))
                        college = collegeId.get()
                        print ("coll",collegeId)
                        pylist = [x.key for x in CollegeDb.query()]
                        print pylist
                        if(collegeId in pylist):
                            flag = 1
                            setattr(prof,'collegeId',collegeId)
                        else:
                            flag = 0
                    else:
                        setattr(prof,field.name,val)
            if flag==1:
                k1 = prof.put()
                
                if (key==None):
                    length = college.student_count
                    if(length == None):
                       length = 0                   
 
                    length = length + 1
                    college.student_count = length
                    college.put()

                print "Inserted"
                print k1

        return _copyProfileToForm(prof)

def changeGcm(request):
    email = request.email

    profile = Profile.query(Profile.email==email)
    print  type(profile)

    for y in profile:
        print y.gcmId

        y.gcmId = request.gcmId
        y.put()

    return



def PersonalInfoForm(request):
    a = PersonalResponse()

    for x in ('name','branch','batch','photoUrl'):
        setattr(a,x,getattr(request,x))

    return a

def deleteProfile(request):
   #Steps to be incorporated for deletion of a profile
   #1) Check if fromKey == pidKey 
   from_key = ndb.Key('Profile',int(request.fromPid)) 
   pid_key = ndb.Key('Profile',int(request.pid))
   if(from_key == pid_key and pid_key!=None):
      profile = pid_key.get()
      print profile.name
   
   #2) Remove the profile key from followers and members of every club
   #3) If the profile is in club.admin then remove it from club.admin and make Superadmin the admin of the club   
   clubList = Club.query()
   
   for club in clubList:
       
       
       if(len(club.members)!=0):
          if pid_key in club.members:
             print ("club key is",club.key)
             club.members.remove(pid_key)
             
       
       if(len(club.follows)!=0):
      
          if pid_key in club.follows:
             club.follows.remove(pid_key)
             
       if pid_key == club.admin:
          #obtain super admin profile of college
          college = club.collegeId.get()
          emailId = college.sup_emailId
          profileret = Profile.query(Profile.email == emailId)
          for superadmin in profileret:
            print ("Superadmin",superadmin.name)
            superadmin.admin.append(club.key)
            club.admin = superadmin.key
            superadmin.clubsJoined.append(club.key)
            superadmin.follows.append(club.key)
            club.members.admin(superadmin.key)
            club.follows.admin(superadmin.key)
            superadmin.put()
       club.put()
          


   #4 Delete Posts which are created by the profile
   postRet =  Post.query(Post.from_pid == pid_key)
   
   for posts in postRet:
         likePostmini = LikePost()
         likePostmini.from_pid = str(pid_key.id())
         likePostmini.postId = str(posts.key.id())   
         deletePost(likePostmini)
     
   # Remove pid_key from event_attendees list
   eventlist = Event.query()
   for event in eventlist:
      if(len(event.attendees)!=0):
          if(pid_key in event.attendees):

             event.attendees.remove(pid_key)
             event.put()
             
    #Remove Events created by that profile
   eventRet =  Event.query(Event.event_creator == pid_key)
   for events in eventRet:
         modifyeventmini = ModifyEvent()
         modifyeventmini.from_pid = str(pid_key.id())
         modifyeventmini.eventId = str(events.key.id())   
         deleteEvent(modifyeventmini)

    #Remove Club_Creation requests by that profile or to that profile 
   clubcreationlist = Club_Creation.query(ndb.OR(Club_Creation.from_pid == pid_key,Club_Creation.to_pid == pid_key))
   
   for clubcreation in clubcreationlist:
             print clubcreation
             clubcreation.key.delete()

    #Remove Join Creation, Join Requests, Post_Requests
   joinCreationRet =  Join_Creation.query(ndb.OR(Join_Creation.from_pid == pid_key,Join_Creation.to_pid == pid_key)) 
   for jc in joinCreationRet:
             print jc
             jc.key.delete()
   
   joinReqRet =  Join_Request.query(ndb.OR(Join_Request.from_pid == pid_key,Join_Request.to_pid == pid_key))
   for jr in joinReqRet:
             print jr
             jr.key.delete()
   postReqRet =  Post_Request.query(ndb.OR(Post_Request.from_pid == pid_key or Post_Request.to_pid == pid_key ))
   
   for pr in postReqRet:
         print pr
         pr.key.delete()

   commentlist = Comments.query(Comments.pid == pid_key)
   for comments in commentlist:
         print comments
         comments.key.delete()         

   #notificationsRet =  Notifications.query(Notifications.to_pid == pid_key)
   notificationsRet = Notifications.query(Notifications.to_pid_list.IN([pid_key]))
   for notif in notificationsRet:
        notif.key.delete()

   notificationsRet2 = Notifications.query(Notifications.to_pid == pid)
   for notif in notificationsRet2:
        notif.key.delete()


   #Delete the profile entity
   pid_key.delete()   