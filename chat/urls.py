from django.urls import path
from chat import views

app_name = "chat"

urlpatterns = [
    path("", views.ChatView.as_view(), name="chat"),
    path("new/", views.NewConversationView.as_view(), name="new_conversation"),
    path("send/", views.SendMessageView.as_view(), name="send_message"),
    path("recommend/", views.RecommendView.as_view(), name="recommend"),
    path("agent/send/", views.AgentSendMessageView.as_view(), name="agent_send_message"),
]
