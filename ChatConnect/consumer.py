import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from groupchat.models import Message
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async


class GroupChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_message(self, group_id, sender_id, data):
        message = Message.objects.create(
                        group_id=group_id,
                        sender_id=sender_id,
                        content=data
                    )
        sender_username=message.sender.username
        return sender_username

    async def connect(self):
        path = self.scope['path']
        parts = path.split('/')
        self.group_id = parts[1] if len(parts) > 1 else None

        self.group_name = f'group_{self.group_id}'
        
        try:
            # Authenticate the user
            await self.authenticate()

            # If authentication is successful, accept the WebSocket connection
            await self.accept()
            # Join the group
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            
        except Exception as e:
            # If authentication fails, reject the WebSocket connection
            await self.close()
            new_message = "Error message: " + str(e)
            raise Exception(new_message) from e
            
    async def authenticate(self):
        try: 
            # Retrieve the JWT token from the WebSocket headers
            access_token=self.scope['headers'][0][1].split(' ')[1]

            # Decode and validate the JWT token
            access_token =  AccessToken(access_token)

            # Check if the token is valid and not expired
            access_token.verify()

            decoded_token = access_token.payload
            is_admin = decoded_token['is_admin']
            self.user_id = decoded_token['user_id']


            if is_admin:
                raise Exception("You are not authorized to perform this action")
        except Exception as e:
            new_message = "Error message: " + str(e)
            raise Exception(new_message) from e

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data['content']
            group_id= self.group_id

            try: 
                sender_username=await self.save_message(group_id,self.user_id,message_content)
                
                # Broadcast the message to the group
                await self.channel_layer.group_send(self.group_name, {
                    "type":"group_message",
                    "message":message_content,
                    "sender_username":sender_username
                })
                
            except asyncio.TimeoutError as e:
                return {"results": f"timeout error on {e}"}
            except Exception as e:
                return {"results": f"error on {e}"}
            
        except Exception as e:
            print(e)

    async def group_message(self, event):
        message = event['message']
        sender_username = event['sender_username']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username
        }))
