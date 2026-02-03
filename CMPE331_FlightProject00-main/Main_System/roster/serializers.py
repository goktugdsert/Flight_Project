from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        groups = list(user.groups.values_list('name', flat=True))
        token['groups'] = groups
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['groups'] = list(self.user.groups.values_list('name', flat=True))
        data['username'] = self.user.username
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer