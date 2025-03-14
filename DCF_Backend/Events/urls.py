from django.urls import path
from .views import EventListCreateAPIView, EventDetailAPIView , CharitySearchAPIView , ProductAPIView ,StockAPIView 

urlpatterns = [
    path('Creat_List/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('event/<int:pk>/', EventDetailAPIView.as_view(), name='event-detail'),
    path('nearbySearchcharities/', CharitySearchAPIView.as_view(), name='nearby-charities'),
    path('products/', ProductAPIView.as_view(), name='product-list-create'),
    
    path('api/stocks/', StockAPIView.as_view(), name='create_or_update_stock'),
    path('api/stocks/<int:charity_id>/', StockAPIView.as_view(), name='create_or_update_stock'),
    path('api/stocks/update/', StockAPIView.as_view(), name='update_stock_quantity'),
    path('api/stocks/add/', StockAPIView.as_view(), name='add_product_to_stock'),

]