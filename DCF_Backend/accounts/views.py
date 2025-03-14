# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


from .serializers import   LoginSerializer , UserRegistrationSerializer , LogoutUserSerializer , VolunteerRegistrationSerializer , CharityRegistrationSerializer
from .models import Volunteer , Charity
from datetime import timedelta
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

#from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.exceptions import APIException
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class RegisterUserView(APIView):
   


    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():

            user = serializer.save()
            user_data = UserRegistrationSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################
# Custom Login View
class LoginView(TokenObtainPairView):
    """
    Custom login view that returns JWT access and refresh tokens along with basic user details.
    The refresh token is stored in an HttpOnly cookie for secure client-side access.
    """

    serializer_class = LoginSerializer  # Custom serializer for login

    def post(self, request, *args, **kwargs):
        # Validate email and password using the custom serializer
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Create access and refresh tokens using Simple JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Get user role
            role = user.role  # Assuming there is a `role` field in User model
            volunteer_id = None
            charity_id = None

            # Check if the user is a student
            if role == 'volunteer':
                volunteer = Volunteer.objects.filter(user=user).first()
                if volunteer:
                    volunteer_id = volunteer.id

            # Check if the user is an enterprise
            elif role == 'charity':
                charity = Charity.objects.filter(user=user).first()
                if charity:
                    charity_id = charity.id

            # Prepare the response data with user details
            response_data = {
               #'access': access_token,
                'refresh': refresh_token,
                'userID': user.id,
                'role': role,
                'volenteer_id': volunteer_id,
                'charity_id': charity_id,
                
                'email': user.email,
            }

            # Set the refresh token as a cookie
            response = Response(response_data)
            response.set_cookie(
                
                'refreshToken',
                refresh_token,
                max_age=timedelta(days=7),  # Set cookie expiration
                httponly=True,  # Prevent JavaScript access
                secure=True,  # Only send the cookie over HTTPS
                samesite='Strict',  # Strict mode to prevent CSRF issues
            )
            response = Response(response_data)
            response.set_cookie(
                "accessToken",
                access_token,
                max_age=timedelta(minutes=15),
                httponly=True,
                secure=True,
                samesite='Strict',
)
            
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################

class LogoutAPIView(APIView):

   
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Logs out the user by invalidating the provided refresh token.
        """
        # Ensure the refresh token is included in the request body
        serializer = self.serializer_class(data=request.data)

        # Validate the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If valid, save (perform logout logic)
        serializer.save()

        # Return a response indicating successful logout
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)

###########################################################################################################################################
""""
class CreateUserView(APIView):
    permission_classes = [AllowAny]
   
    API view to create a user with email, password, and role.
   

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            # Save the user
            user = serializer.save()
            return Response({
                'message': 'User created successfully.',
                'email': user.email,
                'role': user.role
            }, status=status.HTTP_201_CREATED)

        # Return errors if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

"""


from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterVolunteerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VolunteerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            volunteer = serializer.save()
            tokens = get_tokens_for_user(volunteer.user)
            response_data = serializer.data
            response_data.update(tokens)
            response = Response(response_data, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key="accessToken",
                value=tokens.get("accessToken"),
                max_age=int(timedelta(minutes=15).total_seconds()),  # 15 minutes in seconds
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            
            # Set the refresh token as a cookie
            response.set_cookie(
                key="refreshToken",
                value=tokens.get("refreshToken"),
                max_age=int(timedelta(days=7).total_seconds()),  # 7 days in seconds
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterCharityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CharityRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            charity = serializer.save()
            tokens = get_tokens_for_user(charity.user)
            response_data = serializer.data
            response_data.update(tokens)
            response = Response(response_data, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key="accessToken",
                value=tokens.get("accessToken"),
                max_age=int(timedelta(minutes=15).total_seconds()),  # 15 minutes in seconds
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            
            # Set the refresh token as a cookie
            response.set_cookie(
                key="refreshToken",
                value=tokens.get("refreshToken"),
                max_age=int(timedelta(days=7).total_seconds()),  # 7 days in seconds
                httponly=True,
                secure=True,
                samesite='Strict'
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)