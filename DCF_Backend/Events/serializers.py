
from rest_framework import serializers
from accounts.models import Event , Charity , Product , Stock
import math



class EventSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Stock
        fields = ['id', 'charity', 'product', 'quantity'] 
