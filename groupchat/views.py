import json
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from groupchat.models import Group, Message
from groupchat.serializers import GroupSerializer, MessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from users.models import CustomUser
from users.views import is_user_admin

# Create your views here.

def get_logged_in_user(request):
    """
    Get the logged in user

    :param request: request object

    :return: user id
    """
    token = AccessToken(request.headers.get('Authorization', None).split(' ')[1])
    decoded_token = token.payload
    user_id = decoded_token['user_id']
    return user_id

from rest_framework_simplejwt.authentication import JWTAuthentication
class CreateGroupView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: 'OK',
        }
    )
    def post(self, request):
        """
        Create a new group
        
        :param request: request object
        
        :return: JSON response
        """
        # print(request.headers.get('Authorization', None).split(' ')[1])
        # token = AccessToken(request.headers.get('Authorization', None).split(' ')[1])
        # # print(token)
        # authentication = JWTAuthentication()
        # user, _ = authentication.authenticate(request)
        # print(user)

        if not is_user_admin(request):
            try:
                owner = get_logged_in_user(request)
                serializer = GroupSerializer(data=request.data)
                if serializer.is_valid():
                    group_owner = CustomUser.objects.get(pk=owner)
                    group = serializer.save(owner=group_owner, members=[group_owner])
                    return JsonResponse({'message': 'Group created successfully', 'group_id':group.id, 'group_name': group.name}, status=status.HTTP_201_CREATED)
                return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        
class DeleteGroupView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def delete(self, request, group_id):
        """
        Delete a group

        :param request: request object
        :param group_id: group id

        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                group = Group.objects.get(id=group_id)
                # Delete the group
                group.delete()
            except Group.DoesNotExist:
                return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'detail': 'Group deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        
class SearchGroupView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, group_id):
        """
        Searches for a group

        :param request: request object
        :param group_id: group id

        :return: JSON response
        """
        
        if not is_user_admin(request):
            try:
                group = Group.objects.get(id=group_id)
                serializer = GroupSerializer(group)
                groups = Group.objects.filter(id=group_id).values(
                    'id',
                    'name',
                    'owner__username',
                    'members__username',
                )
                
                # Convert the queryset to a list
                group_list = list(groups)

                # Return the serialized data as a JSON response
                serialized_data = json.dumps(group_list)
                
                return HttpResponse(serialized_data, status=status.HTTP_200_OK)
            except Group.DoesNotExist:
                return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        
class AddMemberView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=
        openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: 'OK',
        }
    )
    def post(self, request, group_id):
        """
        Add a member to a group
        
        :param request: request object
        :param group_id: group id
        
        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                # add memmber to group
                group = Group.objects.get(id=group_id)
                user = CustomUser.objects.get(username=request.data['username'])

                group.members.add(user.id)
                group.save()
                return JsonResponse({'message': 'Member added successfully','member_id': user.id,'member_name': user.username}, status=status.HTTP_201_CREATED)
            except Group.DoesNotExist:
                return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
            except CustomUser.DoesNotExist:
                return JsonResponse({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        
class SearchMemberView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, group_id):
        """
        Searches for a member in a group
        
        :param request: request object
        :param group_id: group id

        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                group = Group.objects.get(id=group_id)
                groups = Group.objects.filter(id=group_id).values(
                    'members__username',
                )
                
                # Convert the queryset to a list
                group_list = list(groups)

                # Return the serialized data as a JSON response
                serialized_data = json.dumps(group_list)
                
                return HttpResponse(serialized_data, status=status.HTTP_200_OK)
            except Group.DoesNotExist:
                return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)


# class SendMessageView(APIView):
#     permission_classes = (IsAuthenticated,)
    
#     @swagger_auto_schema(request_body=
#         openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'content': openapi.Schema(type=openapi.TYPE_STRING),
#             }
#         ),
#         responses={
#             200: 'OK',
#         }
#     )
#     def post(self, request, group_id):
#         """
#         Send a message to a group

#         :param request: request object
#         :param group_id: group id

#         :return: JSON response
#         """
#         if not is_user_admin(request):
#             try:
#                 sender_id = get_logged_in_user(request)
                
#                 serializer = MessageSerializer(data=request.data, context={'group_id': group_id, 'sender': sender_id})
#                 if serializer.is_valid():
#                     message=serializer.save()
#                     return JsonResponse({'message': 'Message sent successfully', 'message_id':message.id,'message':request.data['content']}, status=status.HTTP_201_CREATED)
#                 else:
#                     return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             except Group.DoesNotExist:
#                 return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
#             except CustomUser.DoesNotExist:
#                 return JsonResponse({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#             except Exception as e:
#                 return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)

class GetGroupMessagesView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, group_id):
        """
        Get all messages in a group

        :param request: request object
        :param group_id: group id

        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                messages = Message.objects.filter(group=group_id).values(
                    'sender__username',
                    'content',
                    'timestamp',
                )
                
                # Convert the queryset to a list
                message_list = list(messages)

                # Convert datetime objects to strings
                for message in message_list:
                    message['timestamp'] = message['timestamp'].isoformat()

                # Return the serialized data as a JSON response
                serialized_data = json.dumps(message_list)
                
                return HttpResponse(serialized_data, status=status.HTTP_200_OK)
            except Group.DoesNotExist:
                return JsonResponse({'detail': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        

class LikeMessageView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, message_id):
        """
        Like a message in a group

        :param request: request object
        :param message_id: message id

        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                message = Message.objects.get(id=message_id)
                user_id = get_logged_in_user(request)
                if message.likes.filter(id=user_id).exists():
                    return JsonResponse({'message': 'Message already liked','message_id':message_id}, status=400)
                message.likes.add(user_id)
                message.save()
                return JsonResponse({'message': 'Message liked successfully','message_id':message_id}, status=status.HTTP_201_CREATED)
            except Message.DoesNotExist:
                return JsonResponse({'detail': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        

class ListMessageLikesView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, message_id):
        """
        Lists all likes in a message

        :param request: request object
        :param message_id: message id

        :return: JSON response
        """
        if not is_user_admin(request):
            try:
                message = Message.objects.get(id=message_id)
                likes = message.likes.values(
                    'username',
                )
                
                # Convert the queryset to a list
                like_list = list(likes)

                # Return the serialized data as a JSON response
                serialized_data = json.dumps(like_list)
                
                return HttpResponse(serialized_data, status=status.HTTP_200_OK)
            except Message.DoesNotExist:
                return JsonResponse({'detail': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message":"401"},status=status.HTTP_401_UNAUTHORIZED)
        
