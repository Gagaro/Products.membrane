#
# MembraneTestCase Membrane
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.membrane.tests import base
from Products.membrane.config import TOOLNAME, INSTALL_TEST_TYPES
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

# To catch syntax errors in Install
from Products.membrane.Extensions import Install


class TestFailing(base.MembraneTestCase):

    def afterSetUp(self):
        pass

    # Encountered a bug where on Zope 2.8.1 + Plone 2 after Membrane has
    # been installed on a site, it co no longer be renamed.  
    def testSiteRename(self):
        top = self.portal.aq_parent
        id = self.portal.getId()
        newId = id + '_testing_rename'
        
        # Basically we need to become a manager to perform a plone site rename.
        sm = getSecurityManager()
        self.loginAsPortalOwner()
        try:
            top.manage_renameObjects([id], [newId])
            top.manage_renameObjects([newId], [id])
        finally:
            setSecurityManager(sm)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFailing))
    return suite

if __name__ == '__main__':
    framework()
