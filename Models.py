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
    follows = ndb.StringProperty(repeated=True)
    tags = ndb.StringProperty(repeated=True)
    clubsJoined = ndb.StringProperty(repeated=True)
    pid = ndb.StringProperty(required=True)
    gcmId = ndb.StringProperty() # make gcmid compulsory
    isAlumni = ndb.StringProperty(required=True)
    company = ndb.StringProperty()
    location = ndb.StringProperty()
    collegeId = ndb.StringProperty(required=True)
    id = pid

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- What's shown on the UI"""
    name = messages.StringField(1,required=True)
    email = messages.StringField(2,required=True)
    password = messages.StringField(3,required=True)
    phone = messages.StringField(4,required=True)
    '''picture =''' 
    tags = messages.StringField(5,required=True,repeated=True)
    batch =messages.StringField(6,required=True) 
    branch = messages.StringField(7,required=True)
    follows = messages.StringField(8,required=True,repeated=True)
    clubsJoined = messages.StringField(9,required=True,repeated=True)



class Club(ndb.Model):
	name = ndb.StringProperty(required=True)
	clubId = ndb.StringProperty(required=True)
	admin = ndb.StringProperty(required=True)
	description = ndb.StringProperty(required=True)
	members = ndb.StringProperty(repeated=True)
	followers = ndb.StringProperty(repeated=True) # Only includes the set of people apart from members. By default a member of a club follows it.
	abbreviation = ndb.StringProperty()
	photo = ndb.BlobProperty()
	isAlumni = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
	id = clubId

class ClubMiniForm(messages.Message):
    """ClubMiniForm -- What's shown on the UI for a club"""
    name = messages.StringField(1,required=True)
    abbreviation = messages.StringField(2,required=True)
    '''photo =''' 

class Post(ndb.Model):
	title = ndb.StringProperty(required=True)
	description = ndb.StringProperty()
	photo = ndb.BlobProperty()
	clubId = ndb.StringProperty(required=True)
	likes = ndb.IntegerProperty()
	postId = ndb.StringProperty(required=True)
	views = ndb.StringProperty()
	post_creator = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
 	id = postId
 
class PostMiniForm(messages.Message):
    """PostMiniForm -- What's shown on the UI for a post"""
    title = messages.StringField(1,required=True)
    description = messages.StringField(2,required=True)
    clubId = messages.StringField(3,required=True)
    likes = messages.IntegerField(4,required=True)
    views = messages.StringField(5,required=True)
    post_creator =messages.StringField(6,required=True) 
    '''photo ='''     
    
class Event(ndb.Model):
	title = ndb.StringProperty(required=True)
	description = ndb.StringProperty()
	photo = ndb.BlobProperty()
	clubId = ndb.StringProperty(required=True)
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
	id = eventId
	
class EventMiniForm(messages.Message):
    """EventMiniForm -- What's shown on the UI for an event"""
    title = messages.StringField(1,required=True)
    description = messages.StringField(2,required=True)
    clubId = messages.StringField(3,required=True)
    views = messages.StringField(4,required=True)
    event_creator =messages.StringField(5,required=True)
    venue = messages.StringField(6,required=True)
    date = messages.DateTimeField(7,required=True)
    start_time = messages.DateTimeField(8,required=True)
    end_time = messages.DateTimeField(9,required=True)
    '''photo ='''

class Post_Request(ndb.Model):
	from_pid = ndb.StringProperty(required=True)
	to_pid = ndb.StringProperty(required=True)
	club_id = ndb.StringProperty(required=True)
	description = ndb.StringProperty(required=True)
	status = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
	post_request_id = ndb.StringProperty(required=True)
	id = post_request_id
 
class PostRequestMiniForm(messages.Message):
    """PostRequestMiniForm -- What's shown on the UI for an post request"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    description = messages.StringField(3,required=True)
    

class Club_Creation(ndb.Model):
	from_pid = ndb.StringProperty(required=True)
	to_pid = ndb.StringProperty(required=True)
	club_id = ndb.StringProperty(required=True)
	club_name = ndb.StringProperty(required=True)
	abbreviation = ndb.StringProperty(required=True)
	isAlumni = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
	club_creation_id = ndb.StringProperty(required=True)
	id = club_creation_id

class ClubRequestMiniForm(messages.Message):
    """ClubRequestMiniForm -- What's shown on the UI for an club request"""
    from_pid = messages.StringField(1,required=True)
    club_name = messages.StringField(2,required=True)
    abbreviation = messages.StringField(3,required=True)



class Join_Request(ndb.Model):
	from_pid = ndb.StringProperty(required=True)
	to_pid = ndb.StringProperty(required=True)
	club_id = ndb.StringProperty(required=True)
	status = ndb.StringProperty(required=True)
	collegeId = ndb.StringProperty(required=True)
	join_request_id = ndb.StringProperty(required=True)
	id = join_request_id

class JoinRequestMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    


class Comments(ndb.Model):
	pid = ndb.StringProperty(required=True)
	postId = ndb.StringProperty(required=True)
	comment_body = ndb.StringProperty()
	timestamp = ndb.TimeProperty()
	likes = ndb.IntegerProperty()
	collegeId = ndb.StringProperty(required=True)
	commentId = ndb.StringProperty()
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
