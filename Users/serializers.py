from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import  LoginSerializer
from rest_framework import serializers




class RegisterSerailizer(RegisterSerializer):
    username=serializers.CharField(max_length=70, required=False, read_only=True)
    email=serializers.EmailField()
    last_name= serializers.CharField(max_length=70)
    first_name=serializers.CharField(max_length=70)



    def save(self, request):
        user= super().save(request)
        user.first_name= self.data.get("first_name")
        user.last_name= self.data.get("last_name")
        user.save()
        return user



class LoginSerailizer(LoginSerializer):
    username = serializers.CharField(required=False, allow_blank=True, read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})


