# Sample comment
import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class Notifications(ndb.Model):
    clubName = ndb.StringProperty(required=True)
    clubId = ndb.KeyProperty(kind='Club')
    clubphotoUrl = ndb.StringProperty()
    eventName = ndb.StringProperty()
    eventId = ndb.KeyProperty(kind ='Event')
    to_pid = ndb.KeyProperty(kind = 'Profile')
    to_pid_list = ndb.KeyProperty(kind = 'Profile',repeated=True)
    postName = ndb.StringProperty()
    postId = ndb.KeyProperty(kind ='Post')
    timestamp = ndb.DateTimeProperty()
    type = ndb.StringProperty(required='True')

class NotificationResponseForm(messages.Message):
    clubName = messages.StringField(1)
    clubId = messages.StringField(2)
    clubphotoUrl = messages.StringField(3)
    eventName = messages.StringField(4)
    eventId = messages.StringField(5)
    postName = messages.StringField(6)
    postId = messages.StringField(7)
    timestamp = messages.StringField(8)
    type = messages.StringField(9)
class NotificationList(messages.Message):
    list = messages.MessageField(NotificationResponseForm, 1, repeated=True)



class Profile(ndb.Model):
    """Profile -- User profile object"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    phone = ndb.StringProperty(required=True)
    photo = ndb.BlobProperty()
    batch = ndb.StringProperty()
    branch = ndb.StringProperty()
    follows = ndb.KeyProperty(kind='Club', repeated=True)  # ndb.StringProperty(repeated=True)
    tags = ndb.StringProperty(repeated=True)
    clubsJoined = ndb.KeyProperty(kind='Club',
                                  repeated=True)  # One club, many students ndb.StringProperty(repeated=True)
    #pid = ndb.StringProperty(required=True)
    gcmId = ndb.StringProperty()  # make gcmid compulsory
    isAlumni = ndb.StringProperty(required=True)
    company = ndb.StringProperty()
    location = ndb.StringProperty()
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many people
    eventsAttending = ndb.KeyProperty(kind='Event',repeated=True)
    photoUrl = ndb.StringProperty()
    admin = ndb.KeyProperty(kind='Club', repeated=True)
    superadmin = ndb.KeyProperty(kind='CollegeDb', repeated=True)
    #id = pid

class Club(ndb.Model):
    name = ndb.StringProperty(required=True)
    picture = ndb.BlobProperty()
    #clubId = ndb.StringProperty(required=True)
    admin = ndb.KeyProperty(kind='Profile', required=True)
    description = ndb.TextProperty()
    members = ndb.KeyProperty(kind='Profile', repeated=True)
    follows = ndb.KeyProperty(kind='Profile',
                              repeated=True)  # Only includes the set of people apart from members. By default a member of a club follows it.
    abbreviation = ndb.StringProperty()
    photo = ndb.BlobProperty()
    photoUrl = ndb.StringProperty()
    isAlumni = ndb.StringProperty(required=True)
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)


class ClubMiniForm(messages.Message):
    name = messages.StringField(1, required=True)
    adminName = messages.StringField(2)
    description = messages.StringField(3)
    members = messages.StringField(4)
    followers = messages.StringField(
        5)  # Only includes the set of people apart from members. By default a member of a club follows it.
    abbreviation = messages.StringField(6, required=True)
    # photo = ndb.BlobProperty()
    collegeName = messages.StringField(7, required=True)
    clubId = messages.StringField(8,required=True)
    photoUrl = messages.StringField(9)
    memberCount = messages.StringField(10)
    followerCount = messages.StringField(11)
    isMember = messages.StringField(12)
    isFollower = messages.StringField(13)
    #members = messages.StringField(10,repeated=True)

class GetClubMiniForm(messages.Message):
    clubId = messages.StringField(1, required="True")
    pid = messages.StringField(2)
class DelClubMiniForm(messages.Message):
    clubId = messages.StringField(1, required="True")
    pid = messages.StringField(2,required="True")

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    from_pid = ndb.KeyProperty(kind="Profile",required=True)  # ancestor relationship here?
    photo = ndb.BlobProperty()
    club_id = ndb.KeyProperty(kind='Club', required=True)  # Many posts belong to one club
    likes = ndb.IntegerProperty()
    views = ndb.IntegerProperty()
    # id = postId
    likers = ndb.KeyProperty(kind='Profile', repeated=True)
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many posts
    timestamp = ndb.DateTimeProperty()
    photoUrl = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)

class PostForm(messages.Message):
    title = messages.StringField(1)
    description = messages.StringField(2)
    fromPid = messages.StringField(3)  # ancestor relationship here?
    photoUrl = messages.StringField(4)
    # club_id = ndb.KeyProperty(kind='Club',required=True)#Many posts belong to one club
    likes = messages.StringField(5)
    views = messages.StringField(6)
    likers = messages.StringField(7)
    #date = messages.StringField(8)
    #time = messages.StringField(9)
    timestamp = messages.StringField(8)
    clubphotoUrl = messages.StringField(9)
    clubName = messages.StringField(10)
    clubId = messages.StringField(11)

class EditPostForm(messages.Message):
    title = messages.StringField(1)
    description = messages.StringField(2)
    photoUrl = messages.StringField(3)
    postId = messages.StringField(4,required=True)

class Posts(messages.Message):
    items = messages.MessageField(PostForm, 1, repeated=True)


class GetAllPosts(messages.Message):
    collegeId = messages.StringField(1)
    clubId = messages.StringField(2)
    date = messages.StringField(3)
    futureDate = messages.StringField(4)
    pid = messages.StringField(5)
    postId = messages.StringField(6)


class Post_Request(ndb.Model):
    title = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True)
    from_pid = ndb.KeyProperty(kind='Profile', required=True)  # This is the post creator
    to_pid = ndb.KeyProperty(kind='Profile', required=True)  # many requests to one profile
    club_id = ndb.KeyProperty(kind='Club', required=True)
    status = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty()
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many post requests
    photoUrl = ndb.StringProperty()


class GetInformation(messages.Message):
    pid = messages.StringField(1)
    collegeId = messages.StringField(2)
    clubId = messages.StringField(3)
    date = messages.StringField(4)
    pageNumber = messages.StringField(5)
    eventId = messages.StringField(6)
    postId = messages.StringField(7)




class GetPostRequestsForm(messages.Message):
    postName = messages.StringField(1)
    #description = messages.StringField(2)
    fromName = messages.StringField(2)
    fromPhotoUrl = messages.StringField(3)
    clubName = messages.StringField(4)
    postRequestId = messages.StringField(5)
    timestamp = messages.StringField(6)

class GetAllPostRequests(messages.Message):
    items = messages.MessageField(GetPostRequestsForm,1,repeated=True)

class UpdatePostRequests(messages.Message):
    postRequestId = messages.StringField(1,required=True)
    action = messages.StringField(2,required=True)


class PostMiniForm(messages.Message):
    """PostMiniForm -- What's shown on the UI for a post"""
    fromPid = messages.StringField(1, required=True)
    clubId = messages.StringField(2, required=True)
    title = messages.StringField(3, required=True)
    description = messages.StringField(4, required=True)
    likers = messages.StringField(5)
    date = messages.StringField(6)
    time = messages.StringField(7)
    photoUrl = messages.StringField(8)
    postId = messages.StringField(9)
    tags = messages.StringField(10,repeated=True)
    # '''photo ='''


class LikePost(messages.Message):
    fromPid = messages.StringField(1, required=True)
    postId = messages.StringField(2, required=True)


class Event(ndb.Model):
    title = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    photo = ndb.BlobProperty()
    photoUrl = ndb.StringProperty()
    club_id = ndb.KeyProperty(kind='Club', required=True)  # Many events belong to one club
    venue = ndb.StringProperty(required=True)
    start_time = ndb.DateTimeProperty(required=True)#make this required
    end_time = ndb.DateTimeProperty(required=True)
    attendees = ndb.KeyProperty(kind='Profile',repeated=True)
    completed = ndb.StringProperty(required=True)
    views = ndb.IntegerProperty()
    isAlumni = ndb.StringProperty(required=True)
    event_creator = ndb.KeyProperty(kind='Profile',required=True)  # ancestor relationship?
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many events
    tags = ndb.StringProperty(repeated=True)
    timestamp = ndb.DateTimeProperty()

class EventMiniForm(messages.Message):
    title = messages.StringField(1, required=True)
    description = messages.StringField(2)
    photoUrl = messages.StringField(17)
    # photo = ndb.BlobProperty()
    clubId = messages.StringField(3, required=True)  # Many events belong to one club
    # eventId = messages.StringField(4,required=True)
    venue = messages.StringField(4, required=True)
    startDate = messages.StringField(5, required=True)
    startTime = messages.StringField(6, required=True)
    endTime = messages.StringField(7, required=True)
    endDate = messages.StringField(8,required=True)
    attendees = messages.StringField(9)
    completed = messages.StringField(10, required=True)
    views = messages.StringField(11)
    isAlumni = messages.StringField(12, required=True)
    eventCreator = messages.StringField(13, required=True)
    tags = messages.StringField(14,repeated=True)
    date = messages.StringField(15)
    time = messages.StringField(16)
    eventId = messages.StringField(18)

class EventForm(messages.Message):
    title = messages.StringField(1)
    description = messages.StringField(2)
    
    clubId = messages.StringField(3)  # Many events belong to one club
    # eventId = messages.StringField(4,required=True)
    venue = messages.StringField(4)
    startDate = messages.StringField(5)
    startTime = messages.StringField(6)
    endTime = messages.StringField(7)
    endDate = messages.StringField(8)
    attendees = messages.StringField(9)
    completed = messages.StringField(10)
    views = messages.StringField(11)
    isAlumni = messages.StringField(12)
    eventCreator = messages.StringField(13)
    collegeId = messages.StringField(14)
    eventId = messages.StringField(15)
    tags = messages.StringField(16)
    #date = messages.StringField(17)
    #time = messages.StringField(18)
    timestamp = messages.StringField(17)
    
    clubphotoUrl = messages.StringField(18)
    clubName = messages.StringField(19)
    photoUrl = messages.StringField(20)
    isAttending = messages.StringField(21)
    
# id=eventId

class ModifyEvent(messages.Message):
    fromPid = messages.StringField(1, required=True)
    eventId = messages.StringField(2, required=True)


class Events(messages.Message):
    items = messages.MessageField(EventForm,1,repeated=True)


"""
class PostRequestMiniForm(messages.Message):
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    description = messages.StringField(3,required=True)
"""


class Club_Creation(ndb.Model):
    from_pid = ndb.KeyProperty(kind='Profile', required=True)  # One profile can have many club creation requests
    to_pid = ndb.KeyProperty(kind='Profile', required=True)  # many requests to student council admin
   # club_id = ndb.StringProperty(required=True)
    photoUrl = ndb.StringProperty()
    description = ndb.TextProperty(required=True)
    club_name = ndb.StringProperty(required=True)
    abbreviation = ndb.StringProperty(required=True)
    isAlumni = ndb.StringProperty(required=True)
    #club_creation_id = ndb.StringProperty(required=True)
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many club creation requests
    approval_status = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty()
    #id = club_creation_id
class Join_Creation(ndb.Model):
    from_pid = ndb.KeyProperty(kind='Profile', required=True)  # One profile can have many club creation requests
    to_pid = ndb.KeyProperty(kind='Profile', required=True)  # many requests to student council admin
    club_id = ndb.KeyProperty(kind='Club', required=True)
    timestamp = ndb.DateTimeProperty()
    

class ClubRequestMiniForm(messages.Message):
    """ClubRequestMiniForm -- What's shown on the UI for an club request"""
    # from_pid = messages.StringField(1,required=True)
    clubName = messages.StringField(1, required=True)
    abbreviation = messages.StringField(2, required=True)
    description = messages.StringField(3, required=True)
    fromPid = messages.StringField(4, required=True)
    collegeId = messages.StringField(5, required=True)
    photoUrl = messages.StringField(6)


class Join_Request(ndb.Model):
    from_pid = ndb.KeyProperty(kind='Profile', required=True)  # One profile can have many join requests
    to_pid = ndb.KeyProperty(kind='Profile', required=True)  # many requests to join one club
    club_id = ndb.KeyProperty(kind='Club', required=True)
    status = ndb.StringProperty(required=True)
    join_request_id = ndb.StringProperty(required=True)
    id = join_request_id
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many join requests


class JoinRequestMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    fromPid = messages.StringField(1, required=True)
    clubId = messages.StringField(2, required=True)


class JoinClubMiniForm(messages.Message):
    clubId = messages.StringField(1, required=True)
    fromPid = messages.StringField(2, required=True)


class FollowClubMiniForm(messages.Message):
    clubId = messages.StringField(1, required=True)
    fromPid = messages.StringField(2, required=True)


class Comments(ndb.Model):
    pid = ndb.KeyProperty(kind='Profile', required=True)  # One profile can have many comments
    # postId = ndb.KeyProperty(kind=Post,required=True)
    commentBody = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(required=True)
    likes = ndb.IntegerProperty()
    postId = ndb.KeyProperty(kind='Post',required=True)
    collegeId = ndb.KeyProperty(kind='CollegeDb', required=True)  # One college has many comments

class CommentsForm(messages.Message):
    pid = messages.StringField(1,required=True)
    commentBody = messages.StringField(2,required=True)
    date = messages.StringField(3,required=True)
    time = messages.StringField(4,required=True)
    postId = messages.StringField(5,required=True)

class CommentsResponseForm(messages.Message):
    commentor = messages.StringField(1)
    commentBody = messages.StringField(2)
    timestamp = messages.StringField(3)
    photoUrl = messages.StringField(4)

class CommentsResponse(messages.Message):
    completed = messages.StringField(2)
    items = messages.MessageField(CommentsResponseForm,1,repeated=True)

class CollegeDb(ndb.Model):
    name = ndb.StringProperty(required=True)
    abbreviation = ndb.StringProperty()
    location = ndb.StringProperty()
    student_count = ndb.IntegerProperty()
    group_count = ndb.IntegerProperty()
    group_list = ndb.KeyProperty(repeated=True)
    student_sup = ndb.StringProperty(required=True)
    alumni_sup = ndb.StringProperty()
    collegeId = ndb.StringProperty()
    sup_emailId = ndb.StringProperty(required=True)



class CollegeDbMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    name = messages.StringField(1, required=True)
    abbreviation = messages.StringField(2, required=True)
    location = messages.StringField(3, required=True)
    studentSup = messages.StringField(4, required=True)
    alumniSup = messages.StringField(5)
    email = messages.StringField(6,required=True)
    phone = messages.StringField(7,required=True)

# Define Response Classes here

class ClubListResponse(messages.Message):
    list = messages.MessageField(ClubMiniForm, 1, repeated=True)

class GetCollege(messages.Message):
    abbreviation = messages.StringField(1)
    collegeId = messages.StringField(2)
    location = messages.StringField(3)
    name = messages.StringField(4)

class ClubRetrievalMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    collegeId = messages.StringField(1, required=True)
    pid = messages.StringField(2)

class Colleges(messages.Message):
    collegeList = messages.MessageField(GetCollege,1,repeated=True)


class ProfileRetrievalMiniForm(messages.Message):
    email=messages.StringField(1)
    gcmId=messages.StringField(2)
    pid=messages.StringField(3)

class Feed(messages.Message):
    title = messages.StringField(1)
    description = messages.StringField(2)
    # photo = ndb.BlobProperty()
    clubName = messages.StringField(3)  # Many events belong to one club
    # eventId = messages.StringField(4,required=True)
    clubId = messages.StringField(4)
    venue = messages.StringField(5)
    startDate = messages.StringField(6)
    startTime = messages.StringField(7)
    endTime = messages.StringField(8)
    endDate = messages.StringField(9)
    attendees = messages.StringField(10)
    completed = messages.StringField(11)
    views = messages.StringField(12)
    isAlumni = messages.StringField(13)
    contentCreator = messages.StringField(14)
    id = messages.StringField(16) #the post or event creator
    tags = messages.StringField(17,repeated=True)
    likers = messages.StringField(18,repeated=True)
    timestamp = messages.StringField(19)
    photoUrl = messages.StringField(20)
    clubphotoUrl = messages.StringField(21)
    likes = messages.StringField(22)
    clubabbreviation = messages.StringField(23)
    hasLiked = messages.StringField(24)
    isAttending = messages.StringField(25)
    commentCount = messages.StringField(26)
    attendeeList = messages.StringField(27,repeated=True)
    likersList = messages.StringField(28,repeated=True)
    feedType = messages.StringField(29)

class CollegeFeed(messages.Message):
    items = messages.MessageField(Feed,1,repeated=True)
    completed = messages.StringField(2)

class RequestMiniForm(messages.Message):
    reqId = messages.StringField(1, required="True")
    action = messages.StringField(2, required="True")

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- What's shown on the UI"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)
    '''picture ='''
    photoUrl = messages.StringField(3)
    tags = messages.StringField(5, repeated=True)
    batch = messages.StringField(6)
    branch = messages.StringField(7)
    follows = messages.StringField(8, repeated=True)
    clubsJoined = messages.StringField(9,repeated=True)
    collegeId = messages.StringField(10,required=True)
    isAlumni = messages.StringField(12)
    phone=messages.StringField(13,required=True)
    clubNames = messages.MessageField(ClubMiniForm,14,repeated=True)
    #club_names = messages.StringField(14,repeated=True)
    followsNames = messages.StringField(15,repeated=True)
    pid = messages.StringField(16)
    gcmId = messages.StringField(17)
    photoUrl = messages.StringField(18)
    company = messages.StringField(19)
    location = messages.StringField(20)

class MessageResponse(messages.Message):
    status = messages.StringField(1)
    text = messages.StringField(2)

class UpdateGCM(messages.Message):
    gcmId = messages.StringField(1)
    email = messages.StringField(2)

class ProfileResponse(messages.Message):
    success = messages.StringField(1)
    result = messages.MessageField(ProfileMiniForm,2)
    isAdmin = messages.StringField(3)
    isSuperAdmin = messages.StringField(4)

class NotificationMiniForm(messages.Message):
    pid = messages.StringField(1)

class PersonalInfoRequest(messages.Message):
    pid = messages.StringField(1,repeated=True)

class PersonalResponse(messages.Message):
    name = messages.StringField(1)
    batch = messages.StringField(2)
    branch = messages.StringField(3)
    photoUrl = messages.StringField(4)
    pid = messages.StringField(5)

class PersonalInfoResponse(messages.Message):
    items = messages.MessageField(PersonalResponse,1,repeated=True)

class ClubJoinResponse(messages.Message):
    fromPid = messages.StringField(1)
    fromName = messages.StringField(2)
    requestId = messages.StringField(3)
    fromPhotoUrl = messages.StringField(4)
    clubName = messages.StringField(5)
    timestamp = messages.StringField(6)
    fromBranch = messages.StringField(7)
    fromBatch = messages.StringField(8)

class AdminFeed(messages.Message):
    joinReq = messages.MessageField(ClubJoinResponse,1,repeated=True)
    #postItems = messages.MessageField(GetPostRequestsForm,1,repeated=True)    
class SuperAdminFeed(messages.Message):
    fromPid = messages.StringField(1)
    fromName = messages.StringField(2)
    fromPhotoUrl = messages.StringField(3)
    description = messages.StringField(4)
    clubName = messages.StringField(5)
    abbreviation = messages.StringField(6)
    isAlumni = messages.StringField(7)
    requestId = messages.StringField(8)
    timestamp = messages.StringField(9)

class SuperAdminFeedResponse(messages.Message):
    items = messages.MessageField(SuperAdminFeed,1,repeated=True) 
class SetSuperAdminInputForm(messages.Message):
    collegeId = messages.StringField(1)
class SetAdminInputForm(messages.Message):
    clubId = messages.StringField(1)  
class ChangeAdminInputForm(messages.Message):
    clubId = messages.StringField(1)
    currentAdminCheckId = messages.StringField(2)
    newAdminId =  messages.StringField(3)                 
class AdminStatus(messages.Message):
    isAdmin = messages.StringField(3)
    isSuperAdmin = messages.StringField(4)

class UpdateStatus(messages.Message):
    update = messages.StringField(1)
class UpdateGCMMessageMiniForm(messages.Message):
    title = messages.StringField(1)
    type = messages.StringField(2)
    id = messages.StringField(3)
    message = messages.StringField(4)
    batch = messages.StringField(5)
class EditBatchMiniForm(messages.Message):
    fromBatch = messages.StringField(1,required=True)
    toBatch = messages.StringField(2,required=True)


class BDComments(ndb.Model):
    pid = ndb.KeyProperty(kind='Profile', required=True)  # One profile can have many comments
    # postId = ndb.KeyProperty(kind=Post,required=True)
    commentBody = ndb.StringProperty(repeated=True)
    commentHashTag = ndb.StringProperty()
    name = ndb.StringProperty()



class BDCommentCount(messages.Message):
    count = messages.StringField(1)
    commentHashTag = messages.StringField(2)

class BDCommentResponse(messages.Message):
    items = messages.MessageField(BDCommentCount,1,repeated=True)
class DelProfileMiniForm(messages.Message):
    fromPid = messages.StringField(1)
    pid = messages.StringField(2)

class UnjoinClubMiniForm(messages.Message):
    fromPid = messages.StringField(1,required=True)
    pid = messages.StringField(2,required=True)
    clubId = messages.StringField(3,required=True)


class MiscCount(messages.Message):
    count = messages.StringField(1)

class KMCScoreModel(ndb.Model):
    batch = ndb.StringProperty(required=True)
    score = ndb.StringProperty(required=True)

class KMCScore(messages.Message):
    batch = messages.StringField(1,required=True)
    score = messages.StringField(2,required=True)

class KMCScoreHandler(messages.Message):
    items = messages.MessageField(KMCScore,1,repeated=True)


class AddCollege(ndb.Model):
    name = ndb.StringProperty(required=True)
    collegeName = ndb.StringProperty(required=True)
    phone = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    location = ndb.StringProperty(required=True)

class AddCollegeForm(messages.Message):
    name = messages.StringField(1,required=True)
    collegeName = messages.StringField(2,required=True)
    phone = messages.StringField(3,required=True)
    email = messages.StringField(4,required=True)
    location = messages.StringField(5,required=True)

class ProspectiveColleges(messages.Message):
    items = messages.MessageField(AddCollegeForm,1,repeated=True)


class EventsByDateForm(messages.Message):
    collegeId = messages.StringField(1)
    date = messages.StringField(2)
    time = messages.StringField(3)

class EventsByDate(messages.Message):
    eventName = messages.StringField(1)


class LiveComments(ndb.Model):
    name = ndb.StringProperty()
    photoUrl = ndb.StringProperty()
    imageUrl = ndb.StringProperty()
    description = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    timestamp = ndb.DateTimeProperty()

class LiveCommentsForm(messages.Message):
    name = messages.StringField(1)
    photoUrl = messages.StringField(2)
    imageUrl = messages.StringField(3)
    description = messages.StringField(4)
    tags = messages.StringField(5,repeated=True)
    date = messages.StringField(6)
    time = messages.StringField(7)
    timestamp = messages.StringField(8)

class LiveCommentsResponse(messages.Message):
    items = messages.MessageField(LiveCommentsForm,1,repeated=True)
    completed = messages.StringField(2)


class SlamDunkScoreBoard(ndb.Model):
    team1 = ndb.StringProperty()
    team2 = ndb.StringProperty()
    score1 = ndb.StringProperty()
    score2 = ndb.StringProperty()
    quarter = ndb.StringProperty()
    round = ndb.StringProperty()
    gender = ndb.StringProperty()
    completed = ndb.StringProperty()

class SlamDunkScoreBoardForm(messages.Message):
    team1 = messages.StringField(1)
    team2 = messages.StringField(2)
    score1 = messages.StringField(3)
    score2 = messages.StringField(4)
    quarter = messages.StringField(5)
    gender = messages.StringField(6)
    round = messages.StringField(7)
    completed = messages.StringField(8)

class ScoreResponse(messages.Message):
    items = messages.MessageField(SlamDunkScoreBoardForm,1,repeated=True)