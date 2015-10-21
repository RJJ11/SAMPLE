__author__ = 'rohit'
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Profile,ProfileMiniForm,CollegeDb,Club

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
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
            else:
                if field.name=='club_names':
                    pylist=[]
                    for x in prof.clubsJoined:
                        clubs = x.get()
                        pylist.append(clubs.name)
                    setattr(pf, field.name, pylist)

                if field.name=='follows_names':
                    pylist=[]
                    for x in prof.follows:
                        clubs = x.get()
                        pylist.append(clubs.name)
                    setattr(pf, field.name, pylist)
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
        prof = _getProfileFromEmail(email)
        flag=0
        if save_request:
            pf = ProfileMiniForm()
            for field in pf.all_fields():
                #collegeLocation=getattr(save_request,'collegeLocation')
                #print collegeLocation,"is location"
                if hasattr(save_request, field.name):
                    val = getattr(save_request, field.name)

                    if field.name is 'collegeId':
                        #college=CollegeDb.query(CollegeDb.name==val,CollegeDb.location==collegeLocation).fetch()
                        collegeId = ndb.Key('CollegeDb',int(val))
                        pylist = [x.key for x in CollegeDb.query()]
                        if(collegeId in pylist):
                            flag = 1
                            setattr(prof,'collegeId',collegeId)
                        else:
                            flag =0
                    else:
                        setattr(prof,field.name,val)
            if flag==1:
                prof.put()

        return _copyProfileToForm(prof)

