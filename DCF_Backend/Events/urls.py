from django.urls import path
from .views import EventListCreateAPIView, EventDetailAPIView , CharitySearchAPIView

urlpatterns = [
    path('Creat_List/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('event/<int:pk>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('nearbySearchcharities/', CharitySearchAPIView.as_view(), name='nearby-charities'),

]