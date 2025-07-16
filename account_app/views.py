from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import PermissionDenied

from .serializers import LoginSerializer
from .token import create_jwt_pair_for_user

User = get_user_model()

# Create your views here.
class LoginView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
        else:
            return Response({"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        user_exist = User.objects.filter(username=username).exists()
        if user_exist is not True:     
            return Response({"message": "username is not exist"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(username=username, password=password)
    
        if user is not None:
            tokens = create_jwt_pair_for_user(user)
            update_last_login(None, user)
            return Response(data={"message": "Login Successfull", 
                "tokens": tokens,
                "role":user.role,
                "role_name":user.get_role_display(),
                "is_staff":user.is_staff},
            status=status.HTTP_200_OK)

        else:
            return Response(data={"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
        


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == User.GUEST:
            users = User.objects.filter(role=User.GUEST)
        elif user.role == User.ADMIN:
            users = User.objects.exclude(role=User.SUPERADMIN)
        elif user.role == User.SUPERADMIN:
            users = User.objects.all()
        else:
            raise PermissionDenied("Unknown role.")

        data = [{
            "id": u.id,
            "username": u.username,
            "role": u.get_role_display(),
            "instancy": u.instancy.balai_name if u.instancy else None
        } for u in users]
        return Response(data)

    def post(self, request):
        user = request.user
        new_role = int(request.data.get('role', User.GUEST))

        if user.role == User.GUEST:
            raise PermissionDenied("Guest is not allowed to create users.")

        if user.role == User.ADMIN and new_role == User.SUPERADMIN:
            raise PermissionDenied("Admin cannot create SuperAdmin.")

        # Admin hanya boleh membuat user dari instansinya sendiri
        if user.role == User.ADMIN:
            request_instancy_id = request.data.get('instancy')
            if str(user.instancy.id) != str(request_instancy_id):
                raise PermissionDenied("Admin can only assign users to their own instancy.")

        instancy = None
        if request.data.get("instancy"):
            try:
                instancy = Instancy.objects.get(id=request.data["instancy"])
            except Instancy.DoesNotExist:
                return Response({"message": "Instancy not found"}, status=status.HTTP_400_BAD_REQUEST)

        new_user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            role=new_role,
            instancy=instancy,
            created_by=user
        )

        return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        
    def delete(self, request):
        user = request.user
        target_id = request.data.get("user_id")

        try:
            target_user = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.role == User.GUEST:
            raise PermissionDenied("Guest is not allowed to delete users.")

        if user.role == User.ADMIN:
            if target_user.role == User.SUPERADMIN:
                raise PermissionDenied("Admin cannot delete SuperAdmin.")
            if target_user.instancy != user.instancy:
                raise PermissionDenied("Admin can only delete users from their own instancy.")

        target_user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)


