from django.urls import path 
from .views import EventListCreateAPIView, EventDetailAPIView , CharitySearchAPIView , ProductAPIView ,StockAPIView  , AllocateStockToEventAPIView ,EventStockAllocationListAPIView , TaskCreateAPIView , AssignUserToTaskView , CheckStockThresholdAPIView , TaskUpdateAPIView

urlpatterns = [
    path('Creat_ListEvent/', EventListCreateAPIView.as_view(), name='event-list-create'), 
    path('event/<int:pk>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('nearbySearchcharities/', CharitySearchAPIView.as_view(), name='nearby-charities'),
    path('products/', ProductAPIView.as_view(), name='product-list-create'),
    
    path('stocks/', StockAPIView.as_view(), name='create_or_update_stock'), 
    path('stocks/<int:charity_id>/', StockAPIView.as_view(), name='create_or_update_stock'),
    path('stocks/update/', StockAPIView.as_view(), name='update_stock_quantity'),
    path('stocks/add/', StockAPIView.as_view(), name='add_product_to_stock'),
    path('event-allocate-stock/', AllocateStockToEventAPIView.as_view(), name='event-allocate-stock'),

    path('eventAllocations/<int:event_id>/', EventStockAllocationListAPIView.as_view(), name='event-allocations'),
    path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/<int:event_id>/list/', TaskCreateAPIView.as_view(), name='task-list-by-event'),
    path('tasks/<int:id>/update/', TaskUpdateAPIView.as_view(), name='task-update'), 
       
    path('assign-task/', AssignUserToTaskView.as_view(), name='assign-task'),
    path('stock-alert/<int:charity_id>/', CheckStockThresholdAPIView.as_view(), name='check-stock-threshold'),
    path('tasks/<int:task_id>/', TaskCreateAPIView.as_view(), name='task-update'),

]