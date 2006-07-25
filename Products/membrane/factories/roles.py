from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.membrane.interfaces import IMembraneUserRoles
from Products.membrane.interfaces import IGroup
from Products.membrane.config import TOOLNAME
from userrelated import UserRelated


class Roles(UserRelated):
    """
    Adapts from IRolesProvider to IMembraneUserRoles, simply returns
    the roles from the context object.
    """
    security = ClassSecurityInfo()

    implements(IMembraneUserRoles)

    #
    #   IRolesPlugin implementation
    #
    security.declarePrivate('getRolesForPrincipal')
    def getRolesForPrincipal(self, principal, request=None):
        return self.context.getRoles()

class GroupAwareRoles(UserRelated):
    """
    Adapts from IGroupAwareRolesProvider to
    IMembraneUserRoles. Returns the roles from the roles provider and
    from any groups associated with the principal.
    """
    security = ClassSecurityInfo()

    implements(IMembraneUserRoles)

    #
    #   IRolesPlugin implementation
    #
    security.declarePrivate('getRolesForPrincipal')
    def getRolesForPrincipal(self, principal, request=None):
        roles = dict.fromkeys(self.context.getRoles())

        getGroups = getattr(principal, 'getGroups', lambda: tuple())
        group_ids = getGroups()
        if group_ids:
            mbtool = getToolByName(self.context, TOOLNAME)
            uSR = mbtool.unrestrictedSearchResults
            groups = uSR(exact_getGroupId=group_ids,
                         object_implements=IGroup.__identifier__)
            for g in groups:
                group = IGroup(g._unrestrictedGetObject())
                roles.update(dict.fromkeys(group.getRoles()))

        return roles.keys()
