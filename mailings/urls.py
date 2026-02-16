from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('', views.home, name='home'),
    path('statistics/', views.user_statistics, name='statistics'),

    # Message URLs
    path('messages/', views.message_list, name='message_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/<int:pk>/update/', views.message_update, name='message_update'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),

    # Recipient URLs
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/create/', views.recipient_create, name='recipient_create'),
    path('recipients/<int:pk>/', views.recipient_detail, name='recipient_detail'),
    path('recipients/<int:pk>/update/', views.recipient_update, name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),

    # Mailing URLs
    path('mailings/', views.mailing_list, name='mailing_list'),
    path('mailings/create/', views.mailing_create, name='mailing_create'),
    path('mailings/<int:pk>/', views.mailing_detail, name='mailing_detail'),
    path('mailings/<int:pk>/update/', views.mailing_update, name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.mailing_delete, name='mailing_delete'),
]
