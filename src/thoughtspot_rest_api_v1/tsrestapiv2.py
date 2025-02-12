from collections import OrderedDict
from typing import Optional, Dict, List, Union
import json

import requests


class ReportTypes:
    PDF = 'PDF'
    XLSX = 'XLSX'
    CSV = 'CSV'
    PNG = 'PNG'


class TSTypesV2:
    LIVEBOARD = 'LIVEBOARD'
    ANSWER = 'ANSWER'
    DATAOBJECT = 'DATAOBJECT'
    COLUMN = 'COLUMN'


#
# Very simple implementation of V2 REST API
# There will eventually be a standard Python SDK
# Only intended for features in V2 that are not in V1, while the V2 API is being finalized
#

class TSRestApiV2:
    """
    The TSRestApiV2 implementation is a simple implementation to provide access to methods that
    do not exist in V1 at this time, as well as providing a requests.Session object to issue any other
    V2 call the user desires. It is meant as a bridge until the official V2 SDKs are available, and a companion
    to the existing TSRestApiV1 library here
    """
    def __init__(self, server_url: str):
        # Protect from extra end slash on URL
        if server_url[-1] == '/':
            server_url = server_url[0:-1]

        self.server = server_url
        self.api_version = '2.0'

        # REST API uses cookies to maintain the session, so you need to create an open Session
        self.requests_session = requests.Session()

        # X-Requested-By             is necessary for all calls.
        # Accept: application/json   isn't necessary with requests (default: Accept: */*) but might be in other frameworks
        #
        # This sets the header on any subsequent call
        self.api_headers = {'X-Requested-By': 'ThoughtSpot', 'Accept': 'application/json', 'Accept-Language': 'en_US'}
        self.requests_session.headers.update(self.api_headers)

        # Will be set after initial request
        self.__bearer_token = None

        # TS documentation shows the /tspublic/v2/ portion but it is always preceded by {server}/callosum/v2/
        self.base_url = '{server}/api/rest/{version}/'.format(server=self.server, version=self.api_version)
        # self.non_public_base_url = '{server}/callosum/v1/'.format(server=self.server)

    @property
    def bearer_token(self):
        return self.__bearer_token

    @bearer_token.setter
    def bearer_token(self, bearer_token):
        self.__bearer_token = bearer_token
        self.api_headers['Authorization'] = 'Bearer {}'.format(bearer_token)
        self.requests_session.headers.update(self.api_headers)

    #
    # Session management calls
    # - up here vs. in the SESSION section below (because these two are required)
    #
    def auth_session_login(self,  username: Optional[str] = None, password: Optional[str] = None,
                           remember_me: bool = True,
                           bearer_token: Optional[str] = None) -> requests.Session:
        endpoint = 'auth/session/login'

        url = self.base_url + endpoint

        if bearer_token is not None:
            response = self.requests_session.post(url=url,
                                                  headers={"Authorization": "Bearer {}".format(bearer_token)},
                                                  json={'remember_me': str(remember_me).lower()})
        elif username is not None and password is not None:
            json_post_data = {
                'username': username,
                'password': password,
                'remember_me': str(remember_me).lower()
            }
            response = self.requests_session.post(url=url, json=json_post_data)
        else:
            raise Exception("If using username/password, must include both")

        # HTTP 204 - success, no content
        response.raise_for_status()
        return self.requests_session

    def auth_session_logout(self) -> bool:
        endpoint = 'auth/session/logout'

        url = self.base_url + endpoint
        response = self.requests_session.post(url=url)

        # HTTP 204 - success, no content
        response.raise_for_status()
        return True

    # V2 API Bearer token can be used with V1 /session/login/token for Trusted Auth flow
    # or used with each API call (no session object) or used with V2 /auth/session/login to create session
    def auth_token_full(self, username: str, password: Optional[str] = None, org_id: Optional[int] = None,
                        secret_key: Optional[str] = None, validity_time_in_sec: int = 300,
                        auto_create: bool = False, display_name: Optional[str] = None,
                        email: Optional[str] = None, group_identifiers: Optional[List[str]] = None) -> Dict:
        endpoint = 'auth/token/full'

        url = self.base_url + endpoint

        json_post_data = {
            'username': username,
            'validity_time_in_sec': validity_time_in_sec
        }

        if secret_key is not None:
            json_post_data['secret_key'] = secret_key

        elif username is not None and password is not None:
            json_post_data['password'] = password
        else:
            raise Exception("If using username/password, must include both")

        if org_id is not None:
            json_post_data['org_id'] = org_id

        # User provisioning options
        if auto_create is True:
            if display_name is not None and email is not None:
                json_post_data['auto_create'] = True
                json_post_data['display_name'] = display_name
                json_post_data['email'] = email
                if group_identifiers is not None:
                    json_post_data['group_identifiers'] = group_identifiers
            else:
                raise Exception("If using auto_create=True, must include display_name and email")

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def auth_token_object(self, username: str, object_id: str, password: Optional[str] = None,
                          org_id: Optional[int] = None,
                          secret_key: Optional[str] = None, validity_time_in_sec: int = 300,
                          auto_create: bool = False, display_name: Optional[str] = None,
                           email: Optional[str] = None, group_identifiers: Optional[List[str]] = None) -> Dict:
        endpoint = 'auth/token/object'

        url = self.base_url + endpoint

        json_post_data = {
            'username': username,
            'object_id': object_id,
            'validity_time_in_sec': validity_time_in_sec
        }

        if secret_key is not None:
            json_post_data['secret_key'] = secret_key

        elif username is not None and password is not None:
            json_post_data['password'] = password
        else:
            raise Exception("If using username/password, must include both")

        if org_id is not None:
            json_post_data['org_id'] = org_id

        # User provisioning options
        if auto_create is True:
            if display_name is not None and email is not None:
                json_post_data['auto_create'] = True
                json_post_data['display_name'] = display_name
                json_post_data['email'] = email
                if group_identifiers is not None:
                    json_post_data['group_identifiers'] = group_identifiers
            else:
                raise Exception("If using auto_create=True, must include display_name and email")

        response = self.requests_session.post(url=url, json=json_post_data)

        response.raise_for_status()
        return response.json()

    def auth_token_revoke(self) -> bool:
        endpoint = 'auth/token/revoke'

        url = self.base_url + endpoint
        response = self.requests_session.post(url=url)

        # HTTP 204 - success, no content
        response.raise_for_status()
        return True

    #
    # Generic wrappers for the basic HTTP methods
    # Theoretically, you can just get bearer token and issue any command with endpoint and request
    # vs. using any of the other endpoint wrapper methods
    #
    def get_request(self, endpoint):
        url = self.base_url + endpoint
        response = self.requests_session.get(url=url)
        response.raise_for_status()
        return response.json()

    def post_request(self, endpoint, request=None):
        url = self.base_url + endpoint
        if request is not None:
            response = self.requests_session.post(url=url, json=request)
        else:
            response = self.requests_session.post(url=url)

        response.raise_for_status()
        # Most should return a JSON response, but things like deletes may just be 204s
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return True

    def post_request_binary(self, endpoint, request=None):
        url = self.base_url + endpoint
        if request is not None:
            response = self.requests_session.post(url=url, json=request,
                                                  headers={'Accept': 'application/octet-stream'})
        else:
            response = self.requests_session.post(url=url, headers={'Accept': 'application/octet-stream'})

        response.raise_for_status()
        return response.content

    #
    # Principles of individual endpoint implementations:
    # Naming follows the endpoint with _ replacing /
    # Endpoint is embedded within the method
    # If the endpoint URL itself takes an id, the id will be second argument
    # If the POST request takes simple required arguments, they will be made arguments of the method
    # If the possible arguments take complex structures or are highly variable, there will be a requestt argument
    #

    #
    # /users/ endpoints
    #
    def users_search(self, request: Dict):
        endpoint = 'users/search'
        return self.post_request(endpoint=endpoint, request=request)

    def users_create(self, request: Dict):
        endpoint = 'users/create'
        return self.post_request(endpoint=endpoint, request=request)

    def users_update(self, user_identifier: str, request: Dict):
        endpoint = 'users/{}/update'.format(user_identifier)
        return self.post_request(endpoint=endpoint, request=request)

    def users_delete(self, user_identifier: str):
        endpoint = 'users/{}/delete'.format(user_identifier)
        return self.post_request(endpoint=endpoint)

    def users_import(self, request: Dict):
        endpoint = 'users/import'
        return self.post_request(endpoint=endpoint, request=request)

    def users_change_password(self, user_identifier: str, current_password: str, new_password: str):
        endpoint = 'users/change-password'
        request = {
            'user_identifier': user_identifier,
            'current_password': current_password,
            'new_password': new_password
        }
        return self.post_request(endpoint=endpoint, request=request)

    def users_reset_password(self, user_identifier: str, new_password: str):
        endpoint = 'users/reset-password'
        request = {
            'user_identifier': user_identifier,
            'new_password': new_password
        }
        return self.post_request(endpoint=endpoint, request=request)

    def users_force_logout(self, user_identifiers: List[str]):
        endpoint = 'users/force-logout'
        request = {
            'user_identifiers': user_identifiers
        }
        return self.post_request(endpoint=endpoint, request=request)

    #
    # /system/ endpoints
    #

    def system(self):
        endpoint = 'system'
        return self.get_request(endpoint=endpoint)

    def system_config(self):
        endpoint = 'system/config'
        return self.get_request(endpoint=endpoint)

    def system_config_overrides(self):
        endpoint = 'system/config-overrides'
        return self.get_request(endpoint=endpoint)

    def system_config_update(self, configuration: Dict):
        endpoint = 'system/config-update'
        request = {
            'configuration': configuration
        }
        return self.post_request(endpoint=endpoint, request=request)

    #
    # /orgs/ endpoints
    #
    def orgs_search(self, request: Dict):
        endpoint = 'orgs/search'
        return self.post_request(endpoint=endpoint, request=request)

    def orgs_create(self, name: str, description: Optional[str] = None):
        endpoint = 'orgs/create'
        request = {
            'name': name
        }
        if description is not None:
            request['description'] = description
        return self.post_request(endpoint=endpoint, request=request)

    def orgs_update(self, org_identifier: str, request: Dict):
        endpoint = 'orgs/{}/update'.format(org_identifier)
        return self.post_request(endpoint=endpoint, request=request)

    def orgs_delete(self, org_identifier: str):
        endpoint = 'orgs/{}/delete'.format(org_identifier)
        return self.post_request(endpoint=endpoint)
    #
    #
    # /metadata/ endpoints
    #
    #

    #
    # /metadata/tag endpoints
    #
    def tags_search(self, tag_identifier: Optional[str] = None, color: Optional[str] = None):
        endpoint = 'tags/search'
        if tag_identifier is None and color is None:
            raise Exception("Must provide tag_identifier or color")
        request = {}
        if tag_identifier is not None:
            request['tag_identifier'] = tag_identifier
        if color is not None:
            request['color'] = color
        return self.post_request(endpoint=endpoint, request=request)

    def tags_create(self, name: str, color: str):
        endpoint = 'tags/create'
        request = {
            'name': name,
            'color': color
        }
        return self.post_request(endpoint=endpoint, request=request)

    def tags_update(self, tag_identifier: str, name: str, color: str):
        endpoint = 'tags/{}/update'.format(tag_identifier)
        request = {
            'name': name,
            'color': color
        }
        return self.post_request(endpoint=endpoint, request=request)

    def tags_delete(self, tag_identifier: str):
        endpoint = 'tags/{}/delete'.format(tag_identifier)
        return self.post_request(endpoint=endpoint)

    def tags_assign(self, request: Dict):
        endpoint = 'tags/assign'
        return self.post_request(endpoint=endpoint, request=request)

    def tags_unassign(self, request: Dict):
        endpoint = 'tags/unassign'
        return self.post_request(endpoint=endpoint, request=request)

#
# /groups/ endpoints
#
    def groups_search(self, request: Dict):
        endpoint = 'groups/search'
        return self.post_request(endpoint=endpoint, request=request)

    def groups_create(self, request: Dict):
        endpoint = 'groups/create'
        return self.post_request(endpoint=endpoint, request=request)

    def groups_update(self, group_identifier: str, request: Dict):
        endpoint = 'groups/{}/update'.format(group_identifier)
        return self.post_request(endpoint=endpoint, request=request)

    def groups_delete(self, group_identifier: str):
        endpoint = 'groups/{}/delete'.format(group_identifier)
        return self.post_request(endpoint=endpoint)

    def groups_import(self, request: Dict):
        endpoint = 'groups/import'
        return self.post_request(endpoint=endpoint, request=request)

#
# /metadata/ endpoints
#
    def metadata_search(self, request: Dict):
        endpoint = 'metadata/search'
        return self.post_request(endpoint=endpoint, request=request)

    def metadata_liveboard_sql(self, liveboard_identifier: str, visualization_identifiers: Optional[List[str]] = None):
        endpoint = 'metadata/liveboard/sql'
        request = {
            'metadata_identifier': liveboard_identifier
        }
        if visualization_identifiers is not None:
            request['visualization_identifiers'] = visualization_identifiers
        return self.post_request(endpoint=endpoint, request=request)

    def metadata_answer_sql(self, answer_identifier: str):
        endpoint = 'metadata/answer/sql'
        request = {
            'metadata_identifier': answer_identifier
        }
        return self.post_request(endpoint=endpoint, request=request)

    def metadata_tml_import(self, metadata_tmls: List[str], import_policy: str = 'PARTIAL', create_new: bool = False):
        endpoint = 'metadata/tml/import'
        request = {
            'metadata_tmls': metadata_tmls,
            'import_policy': import_policy,
            'create_new': create_new
        }
        return self.post_request(endpoint=endpoint, request=request)

    # Out of convenience, providing a simple List[str] input for getting these by GUID. metadata_request will override
    # if you need the deeper functionality with names / types
    def metadata_tml_export(self, metadata_ids: List[str], export_associated: bool = False, export_fqn: bool = False,
                            metadata_request: Optional[List[Dict]] = None):
        endpoint = 'metadata/tml/export'
        request = {
            'export_associated': export_associated,
            'export_fqn': export_fqn
        }
        if metadata_request is not None:
            request['metadata'] = metadata_request
        else:
            metadata_list = []
            for i in metadata_ids:
                metadata_list.append({'identifier': i})
            request['metadata'] = metadata_list
        return self.post_request(endpoint=endpoint, request=request)

    # Out of convenience, providing a simple List[str] input for getting these by GUID. metadata_request will override
    # if you need the deeper functionality with names / types
    def metadata_delete(self, metadata_ids: List[str], delete_disabled_objects: bool = False,
                        metadata_request: Optional[List[Dict]] = None):
        endpoint = 'metadata/delete'
        request = {
            'delete_disabled_objects': delete_disabled_objects
        }
        if metadata_request is not None:
            request['metadata'] = metadata_request
        else:
            metadata_list = []
            for i in metadata_ids:
                metadata_list.append({'identifier': i})
            request['metadata'] = metadata_list
        return self.post_request(endpoint=endpoint, request=request)

#
# /reports/ endpoints
#

    def report_liveboard(self, request: Dict):
        endpoint = 'report/liveboard'
        return self.post_request_binary(endpoint=endpoint, request=request)

    def report_answer(self, request: Dict):
        endpoint = 'report/answer'
        return self.post_request_binary(endpoint=endpoint, request=request)

#
# /security/ endpoints
#
    def security_principals_fetch_permissions(self, request: Dict):
        endpoint = 'security/principals/fetch-permissions'
        return self.post_request(endpoint=endpoint, request=request)

    def security_metadata_fetch_permissions(self, request: Dict):
        endpoint = 'security/metadata/fetch-permissions'
        return self.post_request(endpoint=endpoint, request=request)

    def security_metadata_assign(self, request: Dict):
        endpoint = 'security/metadata/assign'
        return self.post_request(endpoint=endpoint, request=request)

    def security_metadata_share(self, request: Dict):
        endpoint = 'security/metadata/share'
        return self.post_request(endpoint=endpoint, request=request)

#
# /data/
#
    def searchdata(self, request: Dict):
        endpoint = 'searchdata'
        return self.post_request(endpoint=endpoint, request=request)

    def metadata_liveboard_data(self, request: Dict):
        endpoint = 'metadata/liveboard/data'
        return self.post_request(endpoint=endpoint, request=request)

    def metadata_answer_data(self, request: Dict):
        endpoint = 'metadata/answer/data'
        return self.post_request(endpoint=endpoint, request=request)

#
# /logs/ endpoints
#
    def logs_fetch(self, log_type: str, start_epoch_time_in_millis: int,
                   end_epoch_time_in_millis: int):
        endpoint = 'logs/fetch'
        request = {
            'log_type': log_type,
            'start_epoch_time_in_millis': start_epoch_time_in_millis,
            'end_epoch_time_in_millis': end_epoch_time_in_millis
        }
        return self.post_request(endpoint=endpoint, request=request)

#
# /connection/ endpoints
#
    def connection_search(self, request: Dict):
        endpoint = 'connection/search'
        return self.post_request(endpoint=endpoint, request=request)

    def connection_create(self, request: Dict):
        endpoint = 'connection/create'
        return self.post_request(endpoint=endpoint, request=request)

    def connection_delete(self, connection_identifier: str):
        endpoint = 'connection/delete'
        request = {'connection_identifier': connection_identifier}
        return self.post_request(endpoint=endpoint, request=request)

    def connection_update(self, request: Dict):
        endpoint = 'connection/update'
        return self.post_request(endpoint=endpoint, request=request)
