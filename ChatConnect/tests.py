import json
import random
import string
from channels.testing import WebsocketCommunicator
from django.urls import reverse
from ChatConnect.consumer import GroupChatConsumer
from rest_framework.test import APIClient
from unittest import IsolatedAsyncioTestCase
from asgiref.sync import sync_to_async


class GroupChatConsumerTestCase(IsolatedAsyncioTestCase):
    
    client = APIClient()

    def generate_random_username(self, length=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

    def generate_random_email(self, length=8):
        letters = string.ascii_lowercase
        domain = '@chatconnect.com'
        return ''.join(random.choice(letters) for _ in range(length)) + domain

    def get_user(self):
        
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        self.login_url = reverse('login')
        response = self.client.post(self.login_url, login_data, format='json')
        content = json.loads(response.content)
        access_token = content['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        username= self.generate_random_username()
        email= self.generate_random_email()

        # Create a test user
        testuser={
                    'username': username,
                    'password':'testuser',
                    'email': email,
                }
        response = self.client.post(reverse('create-user'), testuser)

        # login as testuser
        response = self.client.post(self.login_url, testuser)
        content = json.loads(response.content)
        access_token = content['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        return access_token

    def create_group(self):
        # Create a group 
        request = {
            'name': 'testgroup',
            'description': 'testdescription'
        }
        response = self.client.post(reverse('create-group'), request)
        id = json.loads(response.content)['group_id']

        # Add a member to the group
        # request = {
        #     'username': 'testuser'
        # }
        # response = self.client.post(reverse('add-member-to-group', args=[id]), request)
        # content = json.loads(response.content)
        return id


    async def test_group_chat_consumer(self):
        access_token= await sync_to_async(self.get_user)()
        # access_token = "access_token"

        group_id = await sync_to_async(self.create_group)()

        try:
            # This is the frontend Logic to communicate with the websocket

            # Create a WebSocket communicator for the consumer
            communicator = WebsocketCommunicator(GroupChatConsumer.as_asgi(), f"send-message/{group_id}/")

            # Set the JWT token in the communicator's scope
            communicator.scope['headers'] = [
                (b'authorization', f'Bearer {access_token}'),#.encode()
            ]

            # Connect to the WebSocket
            connected, _ = await communicator.connect()

            self.assertTrue(connected)

        
            # Send a message to the consumer
            await communicator.send_json_to({
                "content": "Hello, World!"
            })

            # Receive the response from the consumer
            response = await communicator.receive_json_from()
            # print(response)

            # Assert the received response
            self.assertEqual(response["message"], "Hello, World!")
        
        except Exception as e:
            print(e)

        finally:
            # Disconnect from the WebSocket
            await communicator.disconnect()
            
            


    async def test_realtime_communication(self):
        access_token_user1= await sync_to_async(self.get_user)()
        access_token_user2= await sync_to_async(self.get_user)()

        group_id = await sync_to_async(self.create_group)()

        # Connect user1 to the group
        try:
            

            communicator_user1 = WebsocketCommunicator(
                GroupChatConsumer.as_asgi(),
                f"send-message/{group_id}/",
                headers=[(b'authorization', f'Bearer {access_token_user1}')]
            )
            connected, _ = await communicator_user1.connect()
            self.assertTrue(connected)

            # Connect user2 to the group
            communicator_user2 = WebsocketCommunicator(
                GroupChatConsumer.as_asgi(),
                f"send-message/{group_id}/",
                headers=[(b'authorization', f'Bearer {access_token_user2}')]
            )
            connected, _ = await communicator_user2.connect()
            self.assertTrue(connected)

            # Send a message from user1
            await communicator_user1.send_json_to({'content': 'Hello from user1'})

            # Receive the message on user2's side
            response = await communicator_user2.receive_json_from()
            self.assertEqual(response['message'], 'Hello from user1')

            
            response = await communicator_user1.receive_json_from()
            self.assertEqual(response['message'], 'Hello from user1')

            # Send a message from user2
            await communicator_user2.send_json_to({'content': 'Hi from user2'})

            # Receive the message on user1's side
            response = await communicator_user1.receive_json_from() 
            self.assertEqual(response['message'], 'Hi from user2')

            # Disconnect both users
            await communicator_user1.disconnect()
            await communicator_user2.disconnect()
        except Exception as e:
            print(e)
            self.assertTrue(False)
