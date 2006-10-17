from Products.PluggableAuthService.interfaces.plugins import \
     IUserAdderPlugin

import base

class TestUserAdder(base.MembraneTestCase):
    """
    Tests the IUserAdder utility that is included in the 'example'
    profile.
    """
    def afterSetUp(self):
        setup_tool = self.portal.portal_setup
        setup_tool.setImportContext('profile-membrane:examples')
        setup_tool.runAllImportSteps()
        plugins = self.portal.acl_users.plugins
        plugins.movePluginsUp(IUserAdderPlugin, ['membrane_users'])

    def testUserFolderCreatesUser(self):
        uf = self.portal.acl_users
        userid = 'test_utility'
        pwd = 'secret'
        self.loginAsPortalOwner()
        uf._doAddUser(userid, pwd, [], [])
        self.failUnless(userid in self.portal.objectIds())
        req = self.portal.REQUEST
        self.failIf(uf.authenticate(userid, pwd, req) is None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUserAdder))
    return suite
