
from rest_framework import serializers
from accounts.models import Event , Charity
import math



class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class CharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ('id', 'name', 'description', 'category', 'location', 'latitude', 'longitude')