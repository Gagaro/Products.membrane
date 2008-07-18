from AccessControl import ClassSecurityInfo

from zope.interface import implements
from zope.component import implementedBy

from Products.PluggableAuthService.utils import createViewName
from Products.PluggableAuthService.utils import classImplements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList

from Products.membrane.interfaces import IUserAuthProvider
from Products.membrane.interfaces import IUserAuthentication
from Products.membrane.interfaces import IPropertiesProvider
from Products.membrane.interfaces import ISchemataPropertiesProvider
from Products.membrane.interfaces import IGroupsProvider
from Products.membrane.interfaces import ISelectedGroupsProvider
from Products.membrane.interfaces import IGroupAwareRolesProvider
from Products.membrane.interfaces import IUserRoles
from Products.membrane.interfaces import IMembraneUserAuth
from Products.membrane.interfaces import IMembraneUserManagement
from Products.membrane.interfaces import IMembraneUserChanger
from Products.membrane.interfaces import IMembraneUserDeleter
from Products.membrane.interfaces import IUserDeleter
from Products.membrane.interfaces import IGroup
from Products.membrane.factories.authentication import Authentication
from Products.membrane.factories.properties import Properties
from Products.membrane.factories.properties import SchemataProperties
from Products.membrane.config import PROJECTNAME, TOOLNAME


GROUP_RELATIONSHIP = 'participatesInProject'

group = BaseSchema.copy() + Schema((
    ReferenceField(
        name='manager',
        relationship='managesProject',
        allowed_types=('Member','TestMember',),
        vocabulary='listUsers',
        languageIndependent = 1,),
    ReferenceField(
        name="members",
        relationship=GROUP_RELATIONSHIP,
        multiValued=1,
        languageIndependent = 1,
        allowed_types=('Member','TestMember',),
        vocabulary='listUsers',),
    LinesField(
        name="roles_",
        accessor='getRoles',
        mutator='setRoles',
        ),
    ))

# Make the group title and description user properties
group['title'].user_property = True
group['description'].user_property = True

class TestGroup(BaseFolder):
    """A group archetype for testing"""
    schema = group

    security = ClassSecurityInfo()

    implements(IGroup, IPropertiesProvider)

    def getGroupName(self):
        return self.getId()

    def getGroupId(self):
        return self.getId()

    def getGroupMembers(self):
        # All references and all subobjects that are members
        mems = self.getRefs(GROUP_RELATIONSHIP)
        mem_dict = dict.fromkeys([IMembraneUserAuth(m).getUserId()
                                  for m in mems])
        mbtool = getToolByName(self, TOOLNAME)
        mems = mbtool.unrestrictedSearchResults(
            object_implements=IMembraneUserAuth.__identifier__,
            path='/'.join(self.getPhysicalPath()))
        for m in mems:
            mem_dict[m.getUserId] = 1
        return tuple(mem_dict.keys())

    def listUsers(self):
        """
        Return a DisplayList of users
        """
        catalog = getToolByName(self, TOOLNAME)
        results = catalog(object_implements=IMemberUserAuth.__identifier__)

        value = []
        for r in results:
            key = r.getUserName is not None and r.getUserName.strip() \
                  or r.getUserId
            value.append((key.lower(), (r.UID, key)))
        value.sort()
        value = [r for throwaway, r in value]
        value.insert(0, ('', '<no reference>'))
        return DisplayList(value)

registerType(TestGroup, PROJECTNAME)


user = BaseSchema + Schema((
    StringField('userName',
                languageIndependent = 1,),
    StringField('password',
                languageIndependent = 1,),
    StringField('title',
                languageIndependent = 1,
                user_property='fullname',
                accessor='Title'),
    StringField('mobilePhone',
                languageIndependent = 1,
                user_property=True,),
    StringField('homePhone',
                languageIndependent = 1,
                schemata='userinfo',),
    LinesField('roles_',
               languageIndependent = 1,
               accessor='getRoles',
               mutator='setRoles',
               default=('Member',)),
    ))

extra = BaseSchema + Schema((
    StringField('extraProperty',
                user_property=True,),
    StringField('extraPropertyFromSchemata',
                schemata='userinfo',),
    ))

class BaseMember:
    schema = user
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    # use the object id as our userid

    def getUserId(self):
        return self.getId()

    # getUserName is autogenerated

    def verifyCredentials(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')
        if self.getUserName() == login and self.getPassword() == password:
            return True

    # IMembraneUserManagement methods

    def doChangeUser(self, login, password, **kwargs):
        self.setPassword(password)
        if kwargs:
            self.edit(**kwargs)

    # IMembraneUserDeleter method

    def doDeleteUser(self, login):
        parent = self.aq_inner.aq_parent
        parent.manage_delObjects([self.getId()])


class TestMember(BaseMember, BaseContent):
    """A member archetype for testing"""
    implements(IUserAuthProvider, IUserAuthentication, 
               IPropertiesProvider, IGroupsProvider, 
               IGroupAwareRolesProvider, IUserRoles,
               IMembraneUserChanger, IMembraneUserManagement,
               IMembraneUserDeleter)

registerType(TestMember, PROJECTNAME)


class AlternativeTestMember(BaseMember, BaseContent):
    """A member archetype for testing"""

    security = ClassSecurityInfo()

    implements(IUserAuthProvider, IUserAuthentication, 
               ISchemataPropertiesProvider, ISelectedGroupsProvider)

    # For IPropertiesPlugin implementation/Property mixin
    security.declarePrivate('getUserPropertySchematas')
    def getUserPropertySchemata(self):
        return ['userinfo']

    # For IGroupsPlugin implementation/Group mixin
    security.declarePrivate( 'getGroupRelationships' )
    def getGroupRelationships(self):
        return [GROUP_RELATIONSHIP]

registerType(AlternativeTestMember, PROJECTNAME)

class TestPropertyProvider(BaseContent):
    """Tests externally provided properties"""
    schema = extra
    _at_rename_after_creation = True
    security = ClassSecurityInfo()
    implements(IPropertiesProvider)

registerType(TestPropertyProvider, PROJECTNAME)

class TestAlternatePropertyProvider(BaseContent):
    """
    Tests externally provided properties w/ properties coming from
    schemata
    """
    schema = extra
    _at_rename_after_creation = True
    security = ClassSecurityInfo()
    implements(ISchemataPropertiesProvider)

    def getUserPropertySchemata(self):
        return ('userinfo',)

registerType(TestAlternatePropertyProvider, PROJECTNAME)