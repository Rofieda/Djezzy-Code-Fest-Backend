
from rest_framework import serializers
from accounts.models import Event , Charity , Product , Stock , EventStockAllocation , Task , UserTask , Volunteer , User
from accounts.serializers import UserSerializer
import math




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
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())    
    class Meta:
        model = EventStockAllocation
        fields = ('id', 'event', 'product', 'allocated_quantity')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'  # Includes all fields in the model


    

class EventSerializer(serializers.ModelSerializer):
    charity_name = serializers.CharField(source='charity.name', read_only=True)
    tasks = TaskSerializer(many=True, read_only=True) # reponse should contient the tasks in this event , so the volenteer choose one of them
    class Meta:
        model = Event
        fields = '__all__'




class UserTaskSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    task = TaskSerializer()
    

    class Meta:
        model = UserTask
        fields = ['user', 'task', 'assigned_date']



    
class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = '__all__'

