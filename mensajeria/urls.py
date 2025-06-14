# mensajeria/urls.py

from django.urls import path
from . import views

app_name = 'mensajeria'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    # URL para iniciar nueva conversación (con o sin username en la URL)
    path('new/', views.start_new_conversation, name='start_new_conversation'), # <-- ¡Añadida o modificada!
    path('new/<str:username>/', views.start_new_conversation, name='start_new_conversation_with_user'), # <-- Nueva URL para iniciar directamente con un user
    path('toggle_archive/', views.toggle_archive_conversation, name='toggle_archive_conversation'),
]