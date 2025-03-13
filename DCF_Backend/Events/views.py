from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Event
from django.http import Http404

# Create your views here.
from rest_framework import viewsets
from .serializers import EventSerializer , CharitySerializer
from accounts.models import Charity
import math


class EventListCreateAPIView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EventDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        event = self.get_object(pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    def put(self, request, pk):
        event = self.get_object(pk)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        event = self.get_object(pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        event = self.get_object(pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (specified in decimal degrees).
    Returns the distance in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


class CharitySearchAPIView(APIView):
    def get(self, request):
        # Extract query parameters
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius',5)
        category = request.query_params.get('category')
        event_date = request.query_params.get('event_date')

        # Start with all charities
        events = Event.objects.all()

        # Filter by proximity if latitude and longitude are provided
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                nearby_events = []
                for event in events:
                    if event.latitude and event.longitude:
                        distance = haversine(lat, lng, event.latitude, event.longitude)
                        if distance <= radius:
                            nearby_events.append(event.id)
                events = events.filter(id__in=nearby_events)
            except ValueError:
                return Response({"error": "Invalid latitude, longitude, or radius."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by category if provided
        if category:
            events = events.filter(charity__category=category)

        # Filter by event date if provided
        if event_date:
            events = events.filter(date=event_date)

        # Serialize the filtered charities
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)