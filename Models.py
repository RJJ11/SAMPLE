#Sample comment
import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class Profile(ndb.Model):
    """Profile -- User profile object"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    phone = ndb.StringProperty(required=True)
    userHash = ndb.StringProperty()
    picture = ndb.BlobProperty()
    batch = ndb.StringProperty()
    branch = ndb.StringProperty()
    follows = ndb.KeyProperty(kind='Club',repeated=True)#ndb.StringProperty(repeated=True)
    tags = ndb.StringProperty(repeated=True)
    clubsJoined = ndb.KeyProperty(kind='Club',repeated=True)# One club, many students ndb.StringProperty(repeated=True)
    phone_type = ndb.StringProperty()
    pid = ndb.StringProperty(required=True)
    gcmId = ndb.StringProperty() # make gcmid compulsory
    isAlumni = ndb.StringProperty(required=True)
    company = ndb.StringProperty()
    location = ndb.StringProperty()
    collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many people
    id = pid

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- What's shown on the UI"""
    name = messages.StringField(1,required=True)
    email = messages.StringField(2,required=True)
    password = messages.StringField(3,required=True)
    phone = messages.StringField(4,required=True)
    '''picture =''' 
    tags = messages.StringField(5,repeated=True)
    batch =messages.StringField(6,required=True) 
    branch = messages.StringField(7,required=True)
    follows = messages.StringField(8,repeated=True)
    clubsJoined = messages.StringField(9,repeated=True)


class Club(ndb.Model):
	name = ndb.StringProperty(required=True)
	clubId = ndb.StringProperty(required=True)
	admin = ndb.KeyProperty(kind='Profile',required=True)
	description = ndb.StringProperty()
	members = ndb.StringProperty(repeated=True)
	followers = ndb.StringProperty(repeated=True) # Only includes the set of people apart from members. By default a member of a club follows it.
	abbreviation = ndb.StringProperty()
	photo = ndb.BlobProperty()
	isAlumni = ndb.StringProperty(required=True)
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)

class ClubMiniForm(messages.Message):
	name = messages.StringField(1,required=True)
	clubId = messages.StringField(2,required=True)
	admin = messages.StringField(3)
	description = messages.StringField(4)
	members = messages.StringField(5)
	followers = messages.StringField(6) # Only includes the set of people apart from members. By default a member of a club follows it.
	abbreviation = messages.StringField(7,required=True)
	#photo = ndb.BlobProperty()
	collegeName =  messages.StringField(8,required=True)

class Post(ndb.Model):
	title = ndb.StringProperty(required=True)
	description = ndb.StringProperty()
	from_pid = ndb.StringProperty(required=True)#ancestor relationship here?
	photo = ndb.BlobProperty()
	club_id = ndb.KeyProperty(kind='CollegeDb',required=True)#Many posts belong to one club
	likes = ndb.IntegerProperty()
	postId = ndb.StringProperty(required=True)
	views = ndb.IntegerProperty()
 	id = postId
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many posts

class Post_Request(ndb.Model):
	title = ndb.StringProperty(required = True)
	description = ndb.StringProperty(required=True)
	from_pid = ndb.KeyProperty(kind='Profile',required=True) #This is the post creator
	to_pid = ndb.KeyProperty(kind='Profile',required=True)# many requests to one profile
	club_id = ndb.KeyProperty(kind='CollegeDb',required=True)
	status = ndb.StringProperty(required=True)
	post_request_id = ndb.StringProperty(required=True)
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many post requests
	id = post_request_id

class PostMiniForm(messages.Message):
    """PostMiniForm -- What's shown on the UI for a post"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    title = messages.StringField(3,required=True)
    description = messages.StringField(4,required=True)
    '''photo ='''     
    
class Event(ndb.Model):
	title = ndb.StringProperty(required=True)
	description = ndb.StringProperty()
	photo = ndb.BlobProperty()
	clubId = ndb.KeyProperty(kind='Club',required=True)#Many events belong to one club
	eventId = ndb.StringProperty(required=True)
	venue = ndb.StringProperty(required=True)
	date = ndb.DateProperty(required=True)
	start_time = ndb.TimeProperty(required=True)
	end_time = ndb.TimeProperty(required=True)
	attendees = ndb.StringProperty(repeated=True)
	completed = ndb.StringProperty(required=True)
	views = ndb.StringProperty()
	isAlumni = ndb.StringProperty(required=True)
	event_creator = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
	event_creator = ndb.StringProperty(required=True)#ancestor relationship?
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many events
	id=eventId	
	
class EventMiniForm(messages.Message):
    """EventMiniForm -- What's shown on the UI for an event"""
    title = messages.StringField(1,required=True)
    description = messages.StringField(2,required=True)
    clubId = messages.StringField(3,required=True)
    views = messages.StringField(4,required=True)
    event_creator =messages.StringField(5,required=True)
    venue = messages.StringField(6,required=True)
    date = messages.StringField(7,required=True)
    start_time = messages.StringField(8,required=True)
    end_time = messages.StringField(9,required=True)
    '''photo ='''
"""
class PostRequestMiniForm(messages.Message):
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    description = messages.StringField(3,required=True)
"""

class Club_Creation(ndb.Model):
	from_pid = ndb.KeyProperty(kind='Profile',required=True) #One profile can have many club creation requests
	to_pid = ndb.KeyProperty(kind='Profile',required=True)# many requests to student council admin
	club_id = ndb.StringProperty(required=True)
	club_name = ndb.StringProperty(required=True)
	abbreviation = ndb.StringProperty(required=True)
	isAlumni = ndb.StringProperty(required=True)
	club_creation_id = ndb.StringProperty(required=True)
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many club creation requests
	id = club_creation_id

class ClubRequestMiniForm(messages.Message):
    """ClubRequestMiniForm -- What's shown on the UI for an club request"""
    #from_pid = messages.StringField(1,required=True)
    club_name = messages.StringField(1,required=True)
    abbreviation = messages.StringField(2,required=True)



class Join_Request(ndb.Model):
	from_pid = ndb.KeyProperty(kind='Profile',required=True) #One profile can have many join requests
	to_pid = ndb.KeyProperty(kind='Profile',required=True)# many requests to join one club
	club_id = ndb.KeyProperty(kind='Club',required=True)
	status = ndb.StringProperty(required=True)
	join_request_id = ndb.StringProperty(required=True)
	id = join_request_id
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many join requests

class JoinRequestMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    


class Comments(ndb.Model):
	pid = ndb.KeyProperty(kind='Profile',required=True) #One profile can have many comments
	commentId = ndb.StringProperty(required=True)
    #postId = ndb.KeyProperty(kind=Post,required=True)
	comment_body = ndb.StringProperty()
	timestamp = ndb.TimeProperty()
	likes = ndb.IntegerProperty()
	commentId = ndb.StringProperty()
	collegeId = ndb.KeyProperty(kind='CollegeDb',required=True)# One college has many comments
	id = commentId

class CollegeDb(ndb.Model):
	name = ndb.StringProperty(required=True)
	abbreviation = ndb.StringProperty()
	location = ndb.StringProperty()
	student_count = ndb.IntegerProperty()
	group_count = ndb.IntegerProperty()
	group_list = ndb.StringProperty(repeated=True)
	student_sup = ndb.StringProperty(required=True) 
	alumni_sup = ndb.StringProperty()
	collegeId = ndb.StringProperty(required=True)
	id = collegeId

class CollegeDbMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    name = messages.StringField(1,required=True)
    abbreviation = messages.StringField(2,required=True)
    location = messages.StringField(3,required=True)
    student_sup = messages.StringField(4,required=True)
    alumni_sup = messages.StringField(5)
