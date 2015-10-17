__author__ = 'rohit'
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from Models import Profile,ProfileMiniForm,CollegeDb

def _copyProfileToForm(prof):
        pf = ProfileMiniForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                if field.name=='collegeId':
                    collegeId=getattr(prof,field.name).get().collegeId
                    setattr(pf,field.name,collegeId)
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
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
        
        if save_request:
            pf = ProfileMiniForm()
            for field in pf.all_fields():
                collegeLocation=getattr(save_request,'collegeLocation')
                print collegeLocation,"is location"
                if hasattr(save_request, field.name):
                    val = getattr(save_request, field.name)
                    if field.name is 'collegeLocation':
                        continue
                    if field.name is 'collegeName':
                        college=CollegeDb.query(CollegeDb.name==val,CollegeDb.location==collegeLocation).fetch()
                        setattr(prof,'collegeId',college[0].key)
                    else:
                        setattr(prof,field.name,val)
            prof.put()

        return _copyProfileToForm(prof)

