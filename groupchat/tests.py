import json
from unittest import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import CustomUser

class ManageGroupTestCase(TestCase):
    
    client = APIClient()

    def setUp(self):
        # Authenticate the client with the admin user
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        self.login_url = reverse('login')
        response = self.client.post(self.login_url, login_data, format='json')
        content = json.loads(response.content)
        access_token = content['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Create a test user
        testuser={
                    'username':'testuser',
                    'password':'testpassword',
                    'email':'testuser@chatconnect.com'
                }
        response = self.client.post(reverse('create-user'), testuser)

        # login as testuser
        response = self.client.post(self.login_url, testuser)
        content = json.loads(response.content)
        access_token = content['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

# test for creating a group
    def test_user_creates_group(self):
        request = {
            'name': 'testgroup'
        }

        response = self.client.post(reverse('create-group'), request)
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the group details in the response match the expected values
        self.assertEqual(content['group_name'], request['name'])


# test for deleting a group
    def test_user_deletes_group(self):
        request = {
            'name': 'testgroup',
            'description': 'testdescription'
        }

        response = self.client.post(reverse('create-group'), request)
        id = json.loads(response.content)['group_id']

        response = self.client.delete(reverse('delete-group', args=[id]))

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

# test for searching a group
    def test_user_searches_group(self):
        request = {
            'name': 'testgroup'
        }

        response = self.client.post(reverse('create-group'), request)
        id = json.loads(response.content)['group_id']

        response = self.client.get(reverse('search-group', args=[id]))
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the group details in the response match the expected values
        self.assertEqual(content[0]['name'], request['name'])
    
# test for adding a user to a group
    def test_user_adds_user_to_group(self):

        request = {
            'name': 'testgroup',
            'description': 'testdescription'
        }

        response = self.client.post(reverse('create-group'), request)
        id = json.loads(response.content)['group_id']

        request = {
            'username': 'admin'
        }

        response = self.client.post(reverse('add-member-to-group', args=[id]), request)
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the group details in the response match the expected values
        self.assertEqual(content['member_name'], request['username'])
        # GroupMembership.objects.get(username=request['name']).delete()


# test for searching a member in a group
    def test_user_searches_member_in_group(self):
        request = {
            'name': 'testgroup',
            'description': 'testdescription'
        }

        response = self.client.post(reverse('create-group'), request)
        id = json.loads(response.content)['group_id']

        request = {
            'username': 'testuser'
        }

        response = self.client.post(reverse('add-member-to-group', args=[id]), request)
        content = json.loads(response.content)

        response = self.client.get(reverse('search-members-in-group', args=[id]))
        content = json.loads(response.content)

        # Assert that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the group details in the response match the expected values
        self.assertEqual(content[0]['members__username'], request['username'])

# # test for sending a message in a group
#     def test_user_sends_message_in_group(self):
#         request = {
#             'name': 'testgroup',
#             'description': 'testdescription'
#         }

#         response = self.client.post(reverse('create-group'), request)
#         id = json.loads(response.content)['group_id']

#         request = {
#             'username': 'testuser'
#         }

#         response = self.client.post(reverse('add-member-to-group', args=[id]), request)
#         content = json.loads(response.content)

#         request = {
#             'content': 'testmessage'
#         }

#         response = self.client.post(reverse('send-message', args=[id]), request)
#         content = json.loads(response.content)

#         # Assert that the response has a status code of 200 (OK)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         # Assert that the group details in the response match the expected values
#         self.assertEqual(content['message'], request['content'])

# # test for listing all messages in a group
#     def test_user_lists_all_messages_in_group(self):
#         request = {
#             'name': 'testgroup',
#             'description': 'testdescription'
#         }

#         response = self.client.post(reverse('create-group'), request)
#         id = json.loads(response.content)['group_id']

#         request = {
#             'username': 'testuser'
#         }

#         response = self.client.post(reverse('add-member-to-group', args=[id]), request)
#         content = json.loads(response.content)

#         request = {
#             'message': 'testmessage'
#         }

#         response = self.client.post(reverse('send-message', args=[id]), request)
#         content = json.loads(response.content)

#         response = self.client.get(reverse('list-messages', args=[id]))
#         content = json.loads(response.content)

#         # Assert that the response has a status code of 200 (OK)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

# # test for liking a message in a group
#     def test_user_likes_message_in_group(self):
#         request = {
#             'name': 'testgroup',
#             'description': 'testdescription'
#         }

#         response = self.client.post(reverse('create-group'), request)
#         id = json.loads(response.content)['group_id']

#         request = {
#             'username': 'testuser'
#         }

#         response = self.client.post(reverse('add-member-to-group', args=[id]), request)
#         content = json.loads(response.content)

#         request = {
#             'content': 'testmessage'
#         }

#         response = self.client.post(reverse('send-message', args=[id]), request)
#         content = json.loads(response.content)

#         response = self.client.post(reverse('like-message', args=[content['message_id']]))
#         content = json.loads(response.content)

#         # Assert that the response has a status code of 200 (OK)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# # test for listing all likes for a message in a group
#     def test_user_lists_all_likes_for_message_in_group(self):
#         request = {
#             'name': 'testgroup',
#             'description': 'testdescription'
#         }

#         response = self.client.post(reverse('create-group'), request)
#         id = json.loads(response.content)['group_id']

#         request = {
#             'username': 'testuser'
#         }

#         response = self.client.post(reverse('add-member-to-group', args=[id]), request)
#         content = json.loads(response.content)

#         request = {
#             'content': 'testmessage'
#         }

#         response = self.client.post(reverse('send-message', args=[id]), request)
#         content = json.loads(response.content)

#         response = self.client.post(reverse('like-message', args=[content['message_id']]))
#         content = json.loads(response.content)

#         response = self.client.get(reverse('list-message-likes', args=[content['message_id']]))
#         content = json.loads(response.content)

#         # Assert that the response has a status code of 200 (OK)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


    def tearDown(self) -> None:
        super().tearDown()
        CustomUser.objects.get(username='testuser').delete()

