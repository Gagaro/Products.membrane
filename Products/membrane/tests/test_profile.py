"""Test the generic setup profile."""

from unittest import main, makeSuite

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import ISetupTool

from Products.membrane.interfaces import ICategoryMapper
from Products.membrane.utils import generateCategorySetIdForType

from base import MembraneTestCase

class TestProfile(MembraneTestCase):
    """Test the generic setup profile."""

    def test_archetypetool(self):
        """
        Check interaction with archetypetool.xml

        Verify that the statusmapper stuff gets run even if the type
        is already registered in the catalog map.

        If archetypetool.xml registers a type for the catalog map
        and membranetool.xml is run after archetypetool.xml, then
        membranetool.xml still needs to register the types with the
        status map.

        This problem only surfaces when the archetypetool step is run
        before the membranetool step and since the order is
        unpredictable this test exposes the bug.

        """
        attool = getToolByName(self.portal, 'archetype_tool')
        catalog_map = getattr(attool, 'catalog_map', {})
        if 'TestMember' not in catalog_map:
            catalog_map['TestMember'] = ('portal_catalog',
                                     'membrane_tool')
        cat_set = generateCategorySetIdForType('TestMember')
        mapper = ICategoryMapper(self.portal.membrane_tool)
        if mapper.hasCategorySet(cat_set):
            mapper.delCategorySet(cat_set)
        setup_tool = getToolByName(self.portal, 'portal_setup')
        setup_tool.setImportContext('profile-membrane:test')
        setup_tool.runImportStep('membranetool')

def test_suite():
    return makeSuite(TestProfile)

if __name__ == "__main__":
    main(defaultTest='test_suite')
