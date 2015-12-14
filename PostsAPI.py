__author__ = 'rohit'
import endpoints
from datetime import datetime,date,time
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Post_Request,CollegeDb,Post,Profile,Club
from Models import PostForm,LikePost,CommentsForm,Comments,GetPostRequestsForm

def postRequest(requestentity=None):

        post_request = Post_Request()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        key1 = ndb.Key('Club',int(requestentity.club_id))
        key2 = ndb.Key('Profile',int(requestentity.from_pid))
        club_key = key1
        print "Club key"
        print key1
        profile_key = key2
        #change the ID portion when merging with front end
                    #setattr(clubRequest, field, profile_key)

        if requestentity:
            for field in ('to_pid','club_id','description','status','post_request_id','collegeId','title','from_pid','likers','timestamp','photoUrl'):
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
                    print query
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

                elif field == "timestamp":
                    temp = datetime.strptime(getattr(requestentity,"date"),"%Y-%m-%d").date()
                    temp1 = datetime.strptime(getattr(requestentity,"time"),"%H:%M:%S").time()
                    setattr(post_request,field,datetime.combine(temp,temp1))

        print("About to createClubRequest")
        print(post_request)
        post_request.put()

        return post_request

def postEntry(requestentity=None,check=0):

        newPost = Post()
        #college = CollegeDb(name = 'NITK',student_sup='Anirudh',collegeId='NITK-123')
        #college_key = college.put()
        query = CollegeDb.query()
        club_name = Club.query()
        if check==0:
            print "The request entity key is " + requestentity.club_id
            key1 = ndb.Key('Club',int(requestentity.club_id))
            key2 = ndb.Key('Profile',int(requestentity.from_pid))
        else:
            key1 = requestentity.club_id
            key2 = requestentity.from_pid

        persons = Profile.query()
        #print club_name[0]
        #print "The key is " + club_name[0].key
        club_key = key1
        profile_key = key2
        flag = 0
        flag1 = 0
        clubs = Club.query()

        print "Profile Key " + str(profile_key)
        for x in persons:
            print x.key
            if(x.key == profile_key):
                print "Same"
                flag=1
            else:
                print "NOPE"

        for x in clubs:
            print x.key
            if(x.key == club_key):
                print "Same"
                flag1=1
            else:
                print "NOPE"

                    #setattr(clubRequest, field, profile_key)

        if(flag==1 and flag1==1):
            if requestentity:
                for field in ('title','description','club_id','from_pid','likes','views','timestamp','photo','photoUrl'):

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
                            setattr(newPost, field, profile_key)
                            print "Put PID"
                            setattr(newPost,'collegeId',person_collegeId)
                            print "Put college id"

                        elif field=="timestamp":
                            setattr(newPost, field, val)

                        elif val:
                            print("Value is",val)
                            setattr(newPost, field, str(val))



                    else:
                        if field == "timestamp":
                            temp = datetime.strptime(getattr(requestentity,"date"),"%Y-%m-%d").date()
                            temp1 = datetime.strptime(getattr(requestentity,"time"),"%H:%M:%S").time()
                            setattr(newPost,field,datetime.combine(temp,temp1))

                        setattr(newPost, "likes", 0)
                        setattr(newPost, "views", 0)

            print("About to create Post")
            print(newPost)
            newPost.put()


        else:
             print "Invalid Entry"



        return newPost

def deletePost(request):
        post_id = ndb.Key('Post',int(request.postId))
        from_pid = ndb.Key('Profile',int(request.from_pid))
        post = post_id.get()
        club_admin = post.club_id.get().admin
        flag=0
        if (post.from_pid==from_pid or club_admin==from_pid):
            print "Same"
            flag=1
        else:
            print "Different"

        if flag==1:
            post_id.delete()

        return

def unlikePost(request):
       post_id = ndb.Key('Post',int(request.postId))
       from_pid = ndb.Key('Profile',int(request.from_pid))
       post = post_id.get()
       pylist = post.likers
       if (from_pid in pylist):
           post.likes = post.likes -1
           pylist.remove(from_pid)
           post.likers = pylist
           post.put()
           print pylist
       else:
           print "Nope"

       return


def copyPostToForm(post):
        pf = PostForm()
        for field in pf.all_fields():
            if hasattr(post, field.name):
                setattr(pf, field.name, str(getattr(post, field.name)))
            if field.name == 'postId':
                setattr(pf, field.name, str(post.key.id()))
            if field.name == 'date':
                setattr(pf, field.name, str(post.timestamp.strftime("%Y-%m-%d")))
            if field.name == 'time':
                setattr(pf, field.name, str(post.timestamp.strftime("%H:%M:%S")))
            if field.name == 'clubphotoUrl':
                print "Reached here-1"
                #print str(post.club_id.get().picture)
                setattr(pf, field.name, post.club_id.get().photoUrl)
            if field.name == 'photoUrl':
                setattr(pf, field.name, post.photoUrl)
            if field.name == 'club_name':
                setattr(pf, field.name, post.club_id.get().name)        

        return pf

def likePost(request):
       lp = LikePost()
       post_id = ndb.Key('Post',int(request.postId))
       from_pid = ndb.Key('Profile',int(request.from_pid))
       post = post_id.get()
       pylist = post.likers
       if(from_pid not in pylist):
        post.likes = post.likes+1
        post.likers.append(from_pid)
        post.put()
       else:
        print "Sorry Already liked"

       return message_types.VoidMessage


def editpost(request):
       temp = getattr(request,'postId') #or do request.postId
       key = ndb.Key('Post',int(temp))
       updatedPost = key.get()
       updatedPost.title = request.title
       updatedPost.description = request.description
       updatedPost.put() #Include photo when it comes.
       return

def commentForm(request):
       cf = CommentsForm()
       comment = Comments()
       for field in cf.all_fields():
                if field.name=='pid':
                    print "Entered PID portion"
                    key = ndb.Key('Profile',int(getattr(request,field.name)))
                    print key
                    setattr(comment,field.name,key)
                    person = key.get()
                    print "Second key"
                    key2 = person.collegeId
                    print key2
                    setattr(comment,'collegeId',key2)
                elif field.name=='postId':
                    key = ndb.Key('Post',int(getattr(request,field.name)))
                    setattr(comment,field.name,key)

                else:
                    setattr(comment,field.name,str(getattr(request,field.name)))

       setattr(comment,'likes',0)
       comment.put()
       return message_types.VoidMessage()


def copyPostRequestToForm(request):
       reply = GetPostRequestsForm()
       for field in reply.all_fields():
           print field
           if(hasattr(request,field.name)):
               setattr(reply,field.name,str(getattr(request,field.name)))

           elif(field.name=="person_from"):
               person = request.from_pid.get().name
               setattr(reply,field.name,person)

           elif(field.name=="club_name"):
               club = request.club_id.get().name
               setattr(reply,field.name,club)

           elif field.name == 'date':
                setattr(reply, field.name, str(request.timestamp.strftime("%Y-%m-%d")))
           elif field.name == 'time':
                setattr(reply, field.name, str(request.timestamp.strftime("%H:%M:%S")))

           else:
               setattr(reply,"postRequestId",str(request.key.id()))

       return reply

def update(request):
       requestId = ndb.Key('Post_Request',int(request.postRequestId))
       action = request.action
       if(action.lower()=="accept"):
            post = requestId.get()
            flag=1
            print "Going to post ENtry"
            postEntry(post,flag)
            requestId.delete()
       elif(action.lower()=="reject"):
           print "Oops"
           requestId.delete()
       return