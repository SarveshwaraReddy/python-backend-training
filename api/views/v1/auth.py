from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth import get_user_model
from api.responses.custom_response import SuccessResponse, ErrorResponse

User = get_user_model()

class LoginView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                user_logged_in.send(sender=user.__class__, request=request, user=user)
            except User.DoesNotExist:
                pass
        return response

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            # Blacklist app might not be installed or token invalid, continue logout
            pass
            
        user = request.user
        user_logged_out.send(sender=user.__class__, request=request, user=user)
        return SuccessResponse(message="Logged out successfully.")

class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]
