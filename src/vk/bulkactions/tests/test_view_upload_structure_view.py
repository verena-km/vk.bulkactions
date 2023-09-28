# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from vk.bulkactions.testing import VK_BULKACTIONS_FUNCTIONAL_TESTING
from vk.bulkactions.testing import VK_BULKACTIONS_INTEGRATION_TESTING
from vk.bulkactions.views.upload_structure_view import IUploadStructureView
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = VK_BULKACTIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.content.create(self.portal, "Folder", "other-folder")
        api.content.create(self.portal, "Document", "front-page")

    def test_uploadstructure_is_registered(self):
        view = getMultiAdapter(
            (self.portal["other-folder"], self.portal.REQUEST), name="uploadstructure"
        )
        self.assertTrue(IUploadStructureView.providedBy(view))

    def test_uploadstructure_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal["front-page"], self.portal.REQUEST), name="uploadstructure"
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = IUploadStructureView.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):

    layer = VK_BULKACTIONS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
