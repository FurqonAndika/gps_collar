from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import PermissionDenied

from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import LoginSerializer
from .token import create_jwt_pair_for_user
from .models import Instancy

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
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # ← Blacklist token
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"message": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"message": f"Token error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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

        data = []
        for u in users:
            data.append({
                "id": u.id,
                "username": u.username,
                "role": u.get_role_display(),
                "instancy": {
                    "id": u.instancy.id,
                    "balai_name": u.instancy.balai_name
                } if u.instancy else None
            })

        return Response({"message": "success", "data": data}, status=status.HTTP_200_OK)


    def post(self, request):
        user = request.user
        data = request.data

        if user.role == User.GUEST:
            raise PermissionDenied("Guest is not allowed to create users.")

        new_role = int(data.get('role', User.GUEST))

        if user.role == User.ADMIN and new_role == User.SUPERADMIN:
            raise PermissionDenied("Admin cannot create SuperAdmin.")

        instancy = None
        if user.role == User.ADMIN:
            if str(user.instancy.id) != str(data.get('instancy')):
                raise PermissionDenied("Admin can only assign users to their own instancy.")
            instancy = user.instancy
        elif user.role == User.SUPERADMIN:
            if not data.get("instancy"):
                return Response({"message": "Instancy is required."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                instancy = Instancy.objects.get(id=data["instancy"])
            except Instancy.DoesNotExist:
                return Response({"message": "Instancy not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_user = User.objects.create_user(
                username=data["username"],
                password=data["password"],
                role=new_role,
                instancy=instancy,
                created_by=user
            )
        except IntegrityError as e:
            if "username" in str(e).lower():
                return Response({"message": "Username sudah digunakan."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Gagal membuat user."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"message": "Terjadi kesalahan saat membuat user."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "User berhasil dibuat."}, status=status.HTTP_201_CREATED)

    def put(self, request):
        user = request.user
        data = request.data
        target_id = data.get("user_id")

        if user.role == User.GUEST:
            raise PermissionDenied("Guest tidak boleh mengedit user.")

        if not target_id:
            return Response({"message": "User ID wajib disertakan."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return Response({"message": "User tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

        # ADMIN tidak boleh edit SUPERADMIN
        if user.role == User.ADMIN:
            if target_user.role == User.SUPERADMIN:
                raise PermissionDenied("Admin tidak boleh mengedit SuperAdmin.")
            if target_user.instancy != user.instancy:
                raise PermissionDenied("Admin hanya boleh mengedit user di instansinya sendiri.")

        # Validasi instansi (hanya SUPERADMIN boleh ubah instansi)
        if "instancy" in data and user.role == User.SUPERADMIN:
            try:
                target_user.instancy = Instancy.objects.get(id=data["instancy"])
            except Instancy.DoesNotExist:
                return Response({"message": "Instansi tidak ditemukan."}, status=status.HTTP_400_BAD_REQUEST)
        elif "instancy" in data:
            # ADMIN tidak boleh ubah instansi
            pass  # diamkan, tidak ubah

        if "username" in data:
            # Pastikan username baru tidak duplikat
            if User.objects.exclude(id=target_user.id).filter(username=data["username"]).exists():
                return Response({"message": "Username sudah digunakan."}, status=status.HTTP_400_BAD_REQUEST)
            target_user.username = data["username"]

        if "password" in data and data["password"]:
            target_user.set_password(data["password"])

        if "role" in data:
            new_role = int(data["role"])
            if user.role == User.ADMIN and new_role == User.SUPERADMIN:
                raise PermissionDenied("Admin tidak boleh mengubah role menjadi SuperAdmin.")
            target_user.role = new_role

        target_user.save()

        return Response({"message": "User berhasil diubah."}, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        target_id = request.data.get("user_id")

        try:
            target_user = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.role == User.GUEST:
            raise PermissionDenied("Guest is not allowed to delete users.")

        if user.role == User.ADMIN:
            if target_user.role == User.SUPERADMIN:
                raise PermissionDenied("Admin cannot delete SuperAdmin.")
            if target_user.instancy != user.instancy:
                raise PermissionDenied("Admin can only delete users from their own instancy.")

        target_user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
