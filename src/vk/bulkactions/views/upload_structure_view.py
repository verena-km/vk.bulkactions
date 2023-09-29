# -*- coding: utf-8 -*-

# from vk.bulkactions import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage
from zipfile import ZipFile
from json import loads
from plone import api


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IUploadStructureView(Interface):
    """Marker Interface for IUploadStructureView"""


@implementer(IUploadStructureView)
class UploadStructureView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('upload_structure_view.pt')

    def __call__(self):
        # Implement your own actions:
        self.valid = False  # valid Upload file
        self.message = ""

        self.number = 0

        form = self.request.form

        if "form.button.Upload" in form and "mindmap_file" in form:
            file = form["mindmap_file"]  # ZPublisher.HTTPRequest.FileUpload
            self.read_structure(file)

            if self.valid:
                self.create_structure(self.mindmap_list)
                IStatusMessage(self.request).add(self.message)
                self.request.response.redirect(
                    "{0}".format(api.portal.get().absolute_url()))

            else:
                IStatusMessage(self.request).add(self.message, type="error")

        if "form.button.Cancel" in form:
            IStatusMessage(self.request).add(("Vorgang abgebrochen"))
            self.request.response.redirect(
                "{0}".format(api.portal.get().absolute_url()))
            return False

        return self.index()

    def read_structure(self, file):

        if file.filename == "":
            self.message = "Datei fehlt."
            return

        try:
            with ZipFile(file, 'r') as zip_ref:
                with zip_ref.open('content.json') as json_file:
                    json_content = json_file.read()
                    self.mindmap_list = loads(json_content)
                    self.valid = True
        except:
            self.message = "Keine gültige X-Mind-Datei."

    def create_structure(self, file):

        root_topic = self.mindmap_list[0]['rootTopic']
        portal = api.portal.get()

        for child in root_topic["children"]["attached"]:
            self.create_tree(child, portal)

        self.message = str(self.number)+" Verzeichnisse wurden erzeugt."

    def create_tree(self, element, container):

        folder = api.content.create(
            type='Folder',
            title=element["title"],
            container=container)

        if "notes" in element:
            print(element["notes"]["plain"])
            folder.description = element["notes"]["plain"]["content"]

        self.number = self.number + 1

        if "children" in element:
            for child in element["children"]["attached"]:
                self.create_tree(child, folder)
