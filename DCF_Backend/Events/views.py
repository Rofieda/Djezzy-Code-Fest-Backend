from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Event , User , UserTask , Task
from django.http import Http404
from rest_framework.permissions import AllowAny ,IsAuthenticated

from rest_framework import generics
# Create your views here.
from rest_framework import viewsets
from .serializers import EventSerializer , CharitySerializer , ProductSerializer , StockSerializer , EventStockAllocationSerializer , TaskSerializer
from accounts.models import Charity , Product , Stock , EventStockAllocation
import math 


class EventListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [AllowAny]

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
    





class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all existing products"""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Add a new product"""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class StockAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Crée un nouvel enregistrement de stock ou met à jour la quantité existante.
        """
        charity_id = request.data.get('charity_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 0)

        if not charity_id or not product_id:
            return Response({"error": "charity et product sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            charity = Charity.objects.get(id=charity_id)
            product = Product.objects.get(id=product_id)
        except Charity.DoesNotExist:
            return Response({"error": "Charity introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier si le stock existe déjà pour ce produit et cette association
        stock, created = Stock.objects.get_or_create(charity=charity, product=product)

        if created:
            stock.quantity = quantity
        else:
            stock.quantity += int(quantity)  # Ajoute à la quantité existante

        stock.save()
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def patch(self, request):
        """
        Met à jour la quantité d'un stock existant en fonction de l'ID de l'association et du produit.
        """
        charity_id = request.data.get("charity_id")
        product_id = request.data.get("product_id")
       # quantity = request.data.get("quantity")

        if not charity_id :
            return Response({"error": "L'ID de l'association (charity_id) est requis."}, status=status.HTTP_400_BAD_REQUEST)
        if not product_id :
            return Response({"error": "L'ID de le produit (product_id) est requis."}, status=status.HTTP_400_BAD_REQUEST)
        if not Stock.objects.filter(charity_id=charity_id).exists():
            return Response({"error": f"Aucune association trouvée avec l'ID {charity_id}."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            stock = Stock.objects.get(charity_id=charity_id, product_id=product_id)
        except Stock.DoesNotExist:
            return Response(
                {"error": f"Aucun produit trouvé avec l'ID {product_id} pour l'association {charity_id}."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        
        
           
        quantity = request.data.get("quantity")
        if quantity is None:
            return Response({"error": "La quantité est requise."}, status=status.HTTP_400_BAD_REQUEST)

        stock.quantity = int(quantity)
        stock.save()
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def get(self, request, charity_id):
        """
        Récupérer le stock liée à une charit.
        """
        stocks = Stock.objects.filter(charity_id=charity_id)
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  




class AllocateStockToEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

  
    def post(self, request):
        serializer = EventStockAllocationSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data['event']
            product = serializer.validated_data['product']
            quantity_to_allocate = serializer.validated_data['allocated_quantity']

            try:
                stock_item = Stock.objects.get(charity=event.charity, product=product)
            except Stock.DoesNotExist:
                return Response(
                    {"error": "No stock record found for this product in the charity's inventory."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if stock_item.quantity < quantity_to_allocate:
                return Response(
                    {"error": "Insufficient stock available for this product."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            stock_item.quantity -= quantity_to_allocate
            stock_item.save()

            allocation, created = EventStockAllocation.objects.get_or_create(
                event=event,
                product=product,
                defaults={'allocated_quantity': quantity_to_allocate}
            )
            if not created:
                allocation.allocated_quantity += quantity_to_allocate
                allocation.save()

            response_serializer = EventStockAllocationSerializer(allocation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EventStockAllocationListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = EventStockAllocationSerializer

    def get_queryset(self):
        # Get the event id from URL keyword arguments
        event_id = self.kwargs.get('event_id')
        return EventStockAllocation.objects.filter(event__id=event_id)
    

class TaskCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from django.db import transaction



class AssignUserToTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve parameters from request data
            user_id = request.data.get("user_id")
            event_id = request.data.get("event_id")
            task_id = request.data.get("task_id")

            # Check for missing parameters
            if not all([user_id, event_id, task_id]):
                return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

            
            # Fetch user, event, and task from database
            user = User.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            task = Task.objects.get(id=task_id)

            if not user.role=="volunteer": 
                return Response({"error": "User must be a volunteer to register for this task"}, status=status.HTTP_403_FORBIDDEN)

            # Ensure task belongs to the event
            if task.event_id != event.id:
                return Response({"error": "Task does not belong to this event"}, status=status.HTTP_400_BAD_REQUEST)

            # Get task date (default to event date if task has no specific date)
            task_date = getattr(task, 'date', event.date)

         
            user_tasks_on_date = UserTask.objects.filter(
                user=user, assigned_date=task_date
            ).exclude(task__event=event)

            if user_tasks_on_date.exists():
                return Response({"error": "User already has a task in another event on this date"}, status=status.HTTP_400_BAD_REQUEST)

            # Assign user to task with database transaction
            with transaction.atomic():
                UserTask.objects.create(user=user, task=task, event=event, assigned_date=task_date)

                if task.volunteer_limit > 0:
                    task.volunteer_limit -= 1
                    if task.volunteer_limit == 0:
                        task.delete()  # Delete the task when volunteer limit reaches 0
                        
                    else:
                        task.save()


            return Response({"message": "User successfully assigned to the task"}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckStockThresholdAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, charity_id, *args, **kwargs):
        stocks = Stock.objects.filter(charity_id=charity_id)
        alerts = []

        for stock in stocks:
            if stock.quantity < stock.product.seil:
                alerts.append({
                    'product_id': stock.product.id,
                    'product_name': stock.product.name,
                    'current_quantity': stock.quantity,
                    'threshold': stock.product.seil,
                    'alert': f"Low stock for {stock.product.name}: {stock.quantity} available (threshold: {stock.product.seil}).",
                    'status': 0 
                })


        if alerts:
            # Use a 409 Conflict status (or another appropriate code) to indicate an issue
            return Response({'alerts': alerts}, status=status.HTTP_409_CONFLICT)
        else:
            # Everything is fine
            return Response({'message': 'All products are stocked in good quantities.'}, status=status.HTTP_200_OK)
        