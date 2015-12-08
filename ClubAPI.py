__author__ = 'Siddharth'

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Club_Creation,CollegeDb,Profile,Club,ClubMiniForm

def createClub(request=None):

        #When createClubRequest is called

        print("Request Entity for Create Club ", request)
        clubRequest = Club_Creation()


        collegeId = ndb.Key('CollegeDb',int(request.college_id))
        college = CollegeDb.query(CollegeDb.key == collegeId).fetch(1)

        college_key = college[0].key



        if request and college :

            for field in ('abbreviation','club_name','from_pid','to_pid','isAlumni','collegeId','description','approval_status','photoUrl'):


                if field == "abbreviation":
                    clubRequest.abbreviation = request.abbreviation
                elif field == "club_name":
                    clubRequest.club_name = request.club_name
                elif field == "description":
                    clubRequest.description = request.description

                elif field == "from_pid":
                     profile_key = ndb.Key('Profile',int(request.from_pid))
                     print("Finished frompid")
                     setattr(clubRequest, field, profile_key)
                elif field == "to_pid":
                     '''print("Entered To PID")
                     profile =  Profile(
                               name = 'SiddharthRec',
                               email = 'sid.tiger183@gmail.com',
                               phone = '7760531994',
                               isAlumni='N',
                               collegeId=college_key
                               )'''
                     #get the college of the from_pid guy
                     #Get the email of the college
                     #correspond it to the SUP profile
                     #get his key and save it

                     from_pid_key = ndb.Key('Profile',int(request.from_pid))
                     from_profile = from_pid_key.get()

                     print("From Profile is",from_profile)
                     college_key = from_profile.collegeId
                     college = college_key.get()

                     email = college.sup_emailId

                     print("Email is",email)

                     query = Profile.query(Profile.email == email).fetch(1)

                     if(query[0]):
                         to_pid_key = query[0].key
                         print("to_pid_key",to_pid_key)
                         setattr(clubRequest, field, to_pid_key)
                elif field == "isAlumni":
                     setattr(clubRequest, field, "N")
                elif field == "collegeId":
                     setattr(clubRequest, field, college_key)
                elif field == "approval_status":
                     setattr(clubRequest, field, "N")
                elif field == "photoUrl":
                     if(request.photoUrl):
                         setattr(clubRequest, field, str(request.photoUrl))

            clubRequest.put()

        return clubRequest

def approveClub(requestentity = None):
    ''' In this, first check who the request's to pid is for. If its for SUP of college then change approval status to Y
     else keeep it as it is and flag error'''

    if(requestentity):
        sup_profile = requestentity.to_pid.get()
        college = requestentity.collegeId.get()

        if(sup_profile.email == college.sup_emailId):
            requestentity.approval_status = "Y"
            requestentity.put()
            return "Y"
        else :
            requestentity.approval_status ="N"
            requestentity.put()
            return "N"
    print("Modified Request Entity is",requestentity)
    #requestentity.put()




def createClubAfterApproval(requestentity=None):

        if requestentity:
            newClub = Club()
            newClub.abbreviation = requestentity.abbreviation
            newClub.admin = requestentity.from_pid
            newClub.collegeId = requestentity.collegeId
            newClub.name = requestentity.club_name
            newClub.isAlumni = requestentity.isAlumni
            newClub.description = requestentity.description
            newClub.members.append(requestentity.from_pid)
            newClub.follows.append(requestentity.from_pid)
            newClub.photoUrl = requestentity.photoUrl
            clubkey = newClub.put()

            profile = requestentity.from_pid.get()

            print("To check if profile retrieval is correct ", profile)
            profile.clubsJoined.append(clubkey)

            print("Checking if the  guy has joined the club",profile.clubsJoined)

            profile.follows.append(clubkey)
            print("Check if the profile has folowed the club",profile.follows)

            profile.put()

            college = newClub.collegeId.get()


            if(college):
              college.group_list.append(newClub.key)


              college.put()

        print("finished appending college list")

        return newClub


def getClub(request=None):

        retClub = ClubMiniForm()
        clubKey = ndb.Key('Club',int(request.club_id))
        club = clubKey.get()

        print("The retrieved club is",club)

        collegeidret = club.collegeId
        adminret = club.admin
        print("Admin ret",adminret)

        if club:
             college = CollegeDb.query(CollegeDb.collegeId == collegeidret.get().collegeId).fetch(1)

             print("Club id is",club.key.id())
             retClub.club_id = str(club.key.id())
             retClub.admin = adminret.get().name
             retClub.abbreviation = club.abbreviation
             retClub.name = club.name
             retClub.collegeName = college[0].name
             retClub.description = club.description
             retClub.photoUrl = club.photoUrl
        return retClub

def unfollowClub(request):
        ''' steps that need to be done
        Get the profile and the club
        If the profile matches that of the club admin then disallow

        Check if the profile is a follower of a club. If true remove from each other's lists


        '''
        print("Request for unfollow is ",request)

        from_pid = ndb.Key('Profile',int(request.from_pid))
        club_id = ndb.Key('Club',int(request.club_id))


        profile = from_pid.get()
        club = club_id.get()

        print("Profile",profile)
        print("Club",profile)

        if(club.admin == from_pid):
            return False

        if(from_pid in club.follows):

         #remove club id from profile followers list
         #remove profile id from clubs followers list
         club.follows.remove(from_pid)
         profile.follows.remove(club_id)

         club.put()
         profile.put()
         return True

        else:
         return False




