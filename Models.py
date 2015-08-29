class Profile(ndb.Model):
    """Profile -- User profile object"""
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    phone = ndb.StringProperty()
    userHash = ndb.StringProperty()
    picture = ndb.BlobProperty()
    batch = ndb.StringProperty()
    branch = ndb.StringProperty()
    follows = ndb.StringProperty(repeated=True)
    tags = ndb.StringProperty(repeated=True)
    clubsJoined = ndb.StringProperty(repeated=True)
    pid = ndb.StringProperty()
    gcmId = ndb.StringProperty()
    isAlumni = ndb.StringProperty()
    company = ndb.StringProperty()
    location = ndb.StringProperty()
    collegeId = ndb.StringProperty()

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
	name = ndb.StringProperty()
	clubId = ndb.StringProperty()
	admin = ndb.StringProperty()
	description = ndb.StringProperty()
	members = ndb.StringProperty(repeated=True)
	followers = ndb.StringProperty(repeated=True) # Only includes the set of people apart from members. By default a member of a club follows it.
	abbreviation = ndb.StringProperty()
	photo = ndb.BlobProperty()
	isAlumni = ndb.StringProperty()
	collegeId = ndb.StringProperty()

class ClubMiniForm(messages.Message):
    """ClubMiniForm -- What's shown on the UI for a club"""
    name = messages.StringField(1,required=True)
    abbreviation = messages.StringField(2,required=True)
    '''photo =''' 

class Post(ndb.Model):
	title = ndb.StringProperty()
	description = ndb.StringProperty()
	photo = ndb.BlobProperty()
	clubId = ndb.StringProperty()
	likes = ndb.IntegerProperty()
	postId = ndb.StringProperty()
	views = ndb.StringProperty()
	post_creator = ndb.StringProperty()
	collegeId = ndb.StringProperty()
 
 
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
	title = ndb.StringProperty()
	description = ndb.StringProperty()
	photo = ndb.BlobProperty()
	clubId = ndb.StringProperty()
	eventId = ndb.StringProperty()
	venue = ndb.StringProperty()
	date = ndb.DateProperty()
	start_time = ndb.TimeProperty()
	end_time = ndb.TimeProperty()
	attendees = ndb.StringProperty(repeated=True)
	completed = ndb.IntegerProperty()
	views = ndb.StringProperty()
	isAlumni = ndb.StringProperty()
	event_creator = ndb.StringProperty()
	collegeId = ndb.StringProperty()
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
	from_pid = ndb.StringProperty()
	to_pid = ndb.StringProperty()
	club_id = ndb.StringProperty()
	description = ndb.StringProperty()
	status = ndb.StringProperty()
	collegeId = ndb.StringProperty()
 
class PostRequestMiniForm(messages.Message):
    """PostRequestMiniForm -- What's shown on the UI for an post request"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    description = messages.StringField(3,required=True)
    

class Club_Creation(ndb.Model):
	from_pid = ndb.StringProperty()
	to_pid = ndb.StringProperty()
	club_id = ndb.StringProperty()
	club_name = ndb.StringProperty()
	abbreviation = ndb.StringProperty()
	isAlumni = ndb.StringProperty()
	collegeId = ndb.StringProperty()

class ClubRequestMiniForm(messages.Message):
    """ClubRequestMiniForm -- What's shown on the UI for an club request"""
    from_pid = messages.StringField(1,required=True)
    club_name = messages.StringField(2,required=True)
    abbreviation = messages.StringField(3,required=True)



class Join_Request(ndb.Model):
	from_pid = ndb.StringProperty()
	to_pid = ndb.StringProperty()
	club_id = ndb.StringProperty()
	status = ndb.StringProperty()
	collegeId = ndb.StringProperty()

class JoinRequestMiniForm(messages.Message):
    """JoinRequestMiniForm -- What's shown on the UI for an join request"""
    from_pid = messages.StringField(1,required=True)
    club_id = messages.StringField(2,required=True)
    


class Comments(ndb.Model):
	pid = ndb.StringProperty()
	postId = ndb.StringProperty()
	comment_body = ndb.StringProperty()
	timestamp = ndb.TimeProperty()
	likes = ndb.IntegerProperty()
	collegeId = ndb.StringProperty()

class CollegeDb(ndb.Model):
	name = ndb.StringProperty()
	abbreviation = ndb.StringProperty()
	location = ndb.StringProperty()
	student_count = ndb.IntegerProperty()
	group_count = ndb.IntegerProperty()
	group_list = ndb.StringProperty(repeated=True)
	student_sup = ndb.StringProperty() 
	alumni_sup = ndb.StringProperty()
	collegeId = ndb.StringProperty()
