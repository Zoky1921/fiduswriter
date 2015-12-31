#
# This file is part of Fidus Writer <http://www.fiduswriter.org>
#
# Copyright (C) 2013 Takuto Kojima, Johannes Wilm
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uuid

from ws.base import BaseWebSocketHandler
from logging import info, error
from tornado.escape import json_decode
from tornado.websocket import WebSocketClosedError
from document.models import AccessRight, Document
from document.views import get_accessrights
from avatar.templatetags.avatar_tags import avatar_url

def save_document(document_id,changes):
    document = DocumentWS.sessions[document_id]['document']
    document.title = changes["title"]
    document.contents = changes["contents"]
    document.metadata = changes["metadata"]
    document.settings = changes["settings"]
    document.version = changes["version"]
    document.save()

class DocumentWS(BaseWebSocketHandler):
    sessions = dict()

    def open(self, document_id):
        print 'Websocket opened'
        can_access = False
        self.user = self.get_current_user()
        if int(document_id) == 0:
            can_access = True
            self.is_owner = True
            self.access_rights = 'w'
            self.is_new = True
            document = Document.objects.create(owner_id=self.user.id)
            self.document_id = document.id
        else:
            self.is_new = False
            document = Document.objects.filter(id=int(document_id))
            if len(document) > 0:
                document = document[0]
                self.document_id = document.id
                if document.owner == self.user:
                    self.access_rights = 'w'
                    self.is_owner = True
                    can_access = True
                else:
                    self.is_owner = False
                    access_rights = AccessRight.objects.filter(document=document, user=self.user)
                    if len(access_rights) > 0:
                        self.access_rights = access_rights[0].rights
                        can_access = True
        if can_access:
            if document.id not in DocumentWS.sessions:
                DocumentWS.sessions[document.id]=dict()
                self.id = 0
                DocumentWS.sessions[document.id]['participants']=dict()
                DocumentWS.sessions[document.id]['document'] = document
                # The document may have received more diffs that what were
                # present in the last full version of the document. The
                # difference should not be more than a handful of changes, so we
                # discard these when opening the document again.
                # OBS! This also means that the list of last_diffs will need to 
                # remove those extra diffs.
                document.diff_version = document.version
                DocumentWS.sessions[document.id]['in_control'] = self.id
            else:
                self.id = max(DocumentWS.sessions[document.id]['participants'])+1
            DocumentWS.sessions[document.id]['participants'][self.id] = self
            print DocumentWS.sessions[document.id]
            response = dict()
            response['type'] = 'welcome'
            self.write_message(response)

            #DocumentWS.send_participant_list(self.document.id)

    def confirm_diff(self, request_id):
        response = dict()
        response['type'] = 'confirm_diff'
        response['request_id'] = request_id
        self.write_message(response)

    def get_document(self):
        response = dict()
        response['type'] = 'document_data'
        response['document'] = dict()
        document = DocumentWS.sessions[self.document_id]['document']
        response['document']['id']=document.id
        response['document']['version']=document.version
        response['document']['title']=document.title
        response['document']['contents']=document.contents
        response['document']['metadata']=document.metadata
        response['document']['settings']=document.settings
        response['document']['access_rights'] = get_accessrights(AccessRight.objects.filter(document__owner=document.owner))
        response['document']['owner'] = dict()
        response['document']['owner']['id']=document.owner.id
        response['document']['owner']['name']=document.owner.readable_name
        response['document']['owner']['avatar']=avatar_url(document.owner,80)
        response['document']['owner']['team_members']=[]
        for team_member in document.owner.leader.all():
            tm_object = dict()
            tm_object['id'] = team_member.member.id
            tm_object['name'] = team_member.member.readable_name
            tm_object['avatar'] = avatar_url(team_member.member,80)
            response['document']['owner']['team_members'].append(tm_object)
        response['document_values'] = dict()
        response['document_values']['is_owner']=self.is_owner
        response['document_values']['rights'] = self.access_rights
        if self.is_new:
            response['document_values']['is_new'] = True
        if not self.is_owner:
            response['user']=dict()
            response['user']['id']=self.user.id
            response['user']['name']=self.user.readable_name
            response['user']['avatar']=avatar_url(self.user,80)
        if DocumentWS.sessions[self.document_id]['in_control'] == self.id:
            response['document_values']['control']=True
        response['document_values']['session_id']= self.id
        self.write_message(response)

    def get_document_update(self):
        document = DocumentWS.sessions[self.document_id]['document']
        response = dict()
        response['type'] = 'document_data_update'
        response['document'] = dict()
        response['document']['id']=document.id
        response['document']['version']=document.version
        response['document']['title']=document.title
        response['document']['contents']=document.contents
        response['document']['metadata']=document.metadata
        response['document']['settings']=document.settings
        self.write_message(response)

    def on_message(self, message):
        parsed = json_decode(message)
        print parsed["type"]
        if parsed["type"]=='get_document':
            self.get_document()
        elif parsed["type"]=='get_document_update':
            self.get_document_update()
        elif parsed["type"]=='participant_update':
            DocumentWS.send_participant_list(self.document_id)
        elif parsed["type"]=='save' and self.access_rights == 'w' and DocumentWS.sessions[self.document_id]['in_control'] == self.id:
            save_document(self.document_id, parsed["document"])
        elif parsed["type"]=='chat':
            chat = {
                "id": str(uuid.uuid4()),
                "body": parsed["body"],
                "from": self.user.id,
                "type": 'chat'
                }
            if self.document_id in DocumentWS.sessions:
                DocumentWS.send_updates(chat, self.document_id)
        elif parsed["type"]=='transform' or parsed["type"]=='hash':
            if self.document_id in DocumentWS.sessions:
                DocumentWS.send_updates(message, self.document_id, self.id)
        elif parsed["type"]=='diff':
            if self.document_id in DocumentWS.sessions:
                document = DocumentWS.sessions[self.document_id]["document"]
                if parsed["version"] == document.diff_version:
                    print "DIFFS"
                    print parsed["diff"]
                    print len(parsed["diff"])
                    document.diff_version += len(parsed["diff"])
                    self.confirm_diff(parsed["request_id"])
                    DocumentWS.send_updates(message, self.document_id, self.id)

    def on_close(self):
        print "Websocket closing"
        if hasattr(self, 'document_id') and self.document_id in DocumentWS.sessions and self.id in DocumentWS.sessions[self.document_id]['participants']:
            del DocumentWS.sessions[self.document_id]['participants'][self.id]
            if DocumentWS.sessions[self.document_id]['in_control']==self.id:
                if len(DocumentWS.sessions[self.document_id]['participants'].keys()) > 0:
                    chat = {
                        "type": 'take_control'
                        }
                    new_controller = DocumentWS.sessions[self.document_id]['participants'][min(DocumentWS.sessions[self.document_id]['participants'])]
                    DocumentWS.sessions[self.document_id]['in_control'] = new_controller.id
                    new_controller.write_message(chat)
                    DocumentWS.send_participant_list(self.document_id)
                    print DocumentWS.sessions[self.document_id]
                else:
                    DocumentWS.sessions[self.document_id]['document'].save()
                    del DocumentWS.sessions[self.document_id]
                    print "noone left"

    @classmethod
    def send_participant_list(cls, document_id):
        if document_id in DocumentWS.sessions:
            participant_list = []
            for waiter in cls.sessions[document_id]['participants'].keys():
                participant_list.append({
                    'key':waiter,
                    'id':cls.sessions[document_id]['participants'][waiter].user.id,
                    'name':cls.sessions[document_id]['participants'][waiter].user.readable_name,
                    'avatar':avatar_url(cls.sessions[document_id]['participants'][waiter].user,80)
                    })
            chat = {
                "participant_list": participant_list,
                "type": 'connections'
                }
            DocumentWS.send_updates(chat, document_id)

    @classmethod
    def send_updates(cls, chat, document_id, sender_id=None):
        info("sending message to %d waiters", len(cls.sessions[document_id]))
        for waiter in cls.sessions[document_id]['participants'].keys():
            if cls.sessions[document_id]['participants'][waiter].id != sender_id:
                try:
                    cls.sessions[document_id]['participants'][waiter].write_message(chat)
                except WebSocketClosedError:
                    error("Error sending message", exc_info=True)
