# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from plone import api

class IRemoveLocalrolesView(Interface):
    """Marker Interface for IOutputDemoView"""


@implementer(IRemoveLocalrolesView)
class RemoveLocalrolesView(BrowserView):
    def __call__(self):
        # Implement your own actions:
        self.submitted = False

        form = self.request.form

        if "Submit" in form:
            self.submitted = True

            # Alle Inhalte innerhalb des aktuellen Unterordners
            brains = api.content.find(context=self.context)
            for brain in brains:
                obj = brain.getObject()
                # Rollen des aktuellen Objekts ermitteln
                roles = obj.get_local_roles()
                print(brain.id)
                print(roles)
                for role in roles:
                    name = role[0] # eine Gruppe oder ein User
                    rolelist = role[1] # ein Tuple mit Rollen

                    # Löschen aller lokalen Rollen    
                    obj.manage_delLocalRoles([name])

                    # ein User hat immer die Owner-Rolle, die muss bleiben - also wieder gesetzt werden
                    if "Owner" in rolelist:
                        owner = name
                        obj.manage_setLocalRoles(name, ["Owner"])
                # Kontrolle
                roles = obj.get_local_roles()                        
                print(roles)
           

            self.response_text = f"Die lokalen Rollen wurden zurückgesetzt."

        return self.index()