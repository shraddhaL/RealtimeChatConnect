from django.urls import path

from groupchat.views import AddMemberView, CreateGroupView, DeleteGroupView, GetGroupMessagesView, LikeMessageView, ListMessageLikesView, SearchGroupView, SearchMemberView#, SendMessageView

urlpatterns = [
    path('create-group/', CreateGroupView.as_view(), name='create-group'),
    path('delete-group/<int:group_id>/', DeleteGroupView.as_view(), name='delete-group'),
    path('search-group/<int:group_id>/', SearchGroupView.as_view(), name='search-group'),
    path('create-member/<int:group_id>/', AddMemberView.as_view(), name='add-member-to-group'),
    path('search-members/<int:group_id>/', SearchMemberView.as_view(), name='search-members-in-group'),
    # path('send-message/<int:group_id>/', SendMessageView.as_view(), name='send-message'),
    path('list-messages/<int:group_id>/', GetGroupMessagesView.as_view(), name='list-messages'),
    path('message/<int:message_id>/like/', LikeMessageView.as_view(), name='like-message'),
    path('message/<int:message_id>/likes/', ListMessageLikesView.as_view(), name='list-message-likes'),
]
