# -*- coding: utf-8 -*-

# from vk.bulkactions import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from Products.statusmessages.interfaces import IStatusMessage
from zipfile import ZipFile
from plone import api
import json
import xmltodict


class IUploadStructureView(Interface):
    """Marker Interface for IUploadStructureView"""

@implementer(IUploadStructureView)
class UploadStructureView(BrowserView):

    def __call__(self):
        self.valid = False  # valid Upload file
        self.message = ""
        self.number = 0

        form = self.request.form

        if "form.button.Upload" in form and "mindmap_file" in form:
            file = form["mindmap_file"]  # ZPublisher.HTTPRequest.FileUpload
            self.read_structure(file)

            # TODO Refactoring 
            if self.valid:
                if self.format == "from_json": # xmind 23 format
                    self.create_structure_json()
                if self.format == "from_xml": # xmind-8 format
                    self.create_structure_xml()

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
                files = zip_ref.namelist()
                if 'content.json' in files:  # XMind 23
                    with zip_ref.open('content.json') as json_file:
                        json_content = json_file.read()
                        self.mindmap_list = json.loads(json_content)
                        self.valid = True
                        self.format = "from_json"
                else:
                    if 'content.xml' in files: #  XMind 8 Update 6 (R3.7.6.201711210129)
                        with zip_ref.open('content.xml') as xml_file:
                            xml_content = xml_file.read()
                            self.mindmap_list = xmltodict.parse(xml_content)
                            self.valid = True
                            self.format = "from_xml"
        except:
            self.message = "Keine gültige X-Mind-Datei."

    def create_structure_json(self):

        root_topic = self.mindmap_list[0]['rootTopic']
        portal = api.portal.get()

        for child in root_topic["children"]["attached"]:
            self.create_tree_json(child, portal)

        self.message = str(self.number)+" Verzeichnisse wurden erzeugt."

    def create_tree_json(self, element, container):

        folder = api.content.create(
            type='Folder',
            title=element["title"],
            container=container)

        if "notes" in element:
            folder.description = element["notes"]["plain"]["content"]

        self.number = self.number + 1

        if "children" in element:
            for child in element["children"]["attached"]:
                self.create_tree_json(child, folder)

    def create_structure_xml(self):

        root_topic = self.mindmap_list['xmap-content']['sheet']['topic']
        portal = api.portal.get()
        topic = root_topic["children"]["topics"]["topic"]

        if isinstance(topic, dict):  # bei nur einem Knoten haben wir ein Dict im Dict
            self.create_tree_xml(topic, portal)
        else: # eine Liste mit Dicts
            for child in topic:
                self.create_tree_xml(child, portal)

        self.message = str(self.number)+" Verzeichnisse wurden erzeugt."

    def create_tree_xml(self, element, container):

        folder = api.content.create(
            type='Folder',
            title=element["title"],
            container=container)

        if "notes" in element:
            folder.description = element["notes"]["plain"]

        self.number = self.number + 1

        if "children" in element:
            topic = element["children"]["topics"]["topic"]
           
            if isinstance(topic, dict):  # bei nur einem Knoten haben wir ein Dict im Dict
                self.create_tree_xml(topic, folder)
            else: # eine Liste mit Dicts
                for child in topic:
                    self.create_tree_xml(child, folder)