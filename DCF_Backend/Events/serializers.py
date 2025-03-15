
from rest_framework import serializers
from accounts.models import Event , Charity , Product , Stock , EventStockAllocation , Task
import math



class EventSerializer(serializers.ModelSerializer):
    charity_name = serializers.CharField(source='charity.name', read_only=True)
    class Meta:
        model = Event
        fields = '__all__'


class CharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ('id', 'name', 'description', 'category', 'location', 'latitude', 'longitude')



class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = '__all__'  # Includes all fields: name, description, categor



class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Stock
        fields = ['id', 'charity', 'product', 'quantity'] 




class EventStockAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStockAllocation
        fields = ('id', 'event', 'product', 'allocated_quantity')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'  # Includes all fields in the model