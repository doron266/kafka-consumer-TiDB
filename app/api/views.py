from django.http import Http404
from django.shortcuts import get_object_or_404

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import User, Login
from .serializers import UserSerializer, LoginSerializer


# ----------------------------
# USERS
# ----------------------------

@swagger_auto_schema(
    method="get",
    operation_summary="Lists all users or a single user by email",
    operation_description="Retrieve all users or a single user by email.",
    manual_parameters=[
        openapi.Parameter(
            "email",
            openapi.IN_QUERY,
            description="Optional. If provided, returns the user matching this email. Otherwise returns all users.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={200: "User(s)", 400: "Bad request", 404: "Not found", 500: "Server error"},
)
@api_view(["GET"])
def get_users(request):
    if "email" in request.GET:
        email = request.GET["email"]
        if not email:
            return Response({"result": "error", "message": "Email parameter is missing"}, status=400)

        try:
            user = get_object_or_404(User, email=email)
            return Response(UserSerializer(user).data)
        except Http404:
            return Response({"result": "error", "message": "User not found"}, status=404)

    try:
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new user",
    operation_description="Create a new user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "auth_token": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username", "email", "password"],
    ),
    responses={201: "Created", 400: "Bad request", 500: "Server error"},
)
@api_view(["POST"])
def add_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=400)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


@swagger_auto_schema(
    method="put",
    operation_summary="Updates existing user",
    operation_description="Update an existing user by email. Email cannot be changed.",
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email of the user to update", type=openapi.TYPE_STRING)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "auth_token": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={200: "Updated", 400: "Bad request", 404: "Not found", 500: "Server error"},
)
@api_view(["PUT"])
def update_user(request):
    email = request.query_params.get("email")
    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=400)

    try:
        user = get_object_or_404(User, email=email)
        request_data = request.data.copy()
        request_data["email"] = email  # prevent changing email
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=404)

    try:
        serializer = UserSerializer(user, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=200)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=400)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes existing user",
    operation_description="Delete an existing user by email.",
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email of the user to delete", type=openapi.TYPE_STRING)
    ],
    responses={204: "Deleted", 400: "Bad request", 404: "Not found", 500: "Server error"},
)
@api_view(["DELETE"])
def delete_user(request):
    email = request.query_params.get("email")
    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=400)

    try:
        user = get_object_or_404(User, email=email)
        user.delete()
        return Response({"result": "success", "message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=404)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


# ----------------------------
# LOGINS
# ----------------------------

@swagger_auto_schema(
    method="get",
    operation_summary="Lists all logins or filter by email",
    operation_description="Retrieve all login records, or filter by email.",
    manual_parameters=[
        openapi.Parameter(
            "email",
            openapi.IN_QUERY,
            description="Optional. If provided, returns login records for this email.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={200: "Login(s)", 400: "Bad request", 500: "Server error"},
)
@api_view(["GET"])
def get_logins(request):
    email = request.query_params.get("email")

    try:
        if email is not None:
            if not email:
                return Response({"result": "error", "message": "Email parameter is missing"}, status=400)
            logins = Login.objects.filter(email=email).order_by("-created_at")
            return Response(LoginSerializer(logins, many=True).data)

        logins = Login.objects.all().order_by("-created_at")
        return Response(LoginSerializer(logins, many=True).data)

    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new login record",
    operation_description="Create a login record (audit log). Timestamp is auto-generated.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username", "email"],
    ),
    responses={201: "Created", 400: "Bad request", 500: "Server error"},
)
@api_view(["POST"])
def add_login(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=400)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes login records by email",
    operation_description="Delete login records (bulk) by email.",
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email to delete login records for", type=openapi.TYPE_STRING)
    ],
    responses={204: "Deleted", 400: "Bad request", 500: "Server error"},
)
@api_view(["DELETE"])
def delete_logins_by_email(request):
    email = request.query_params.get("email")
    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=400)

    try:
        deleted_count, _ = Login.objects.filter(email=email).delete()
        return Response(
            {"result": "success", "message": f"Deleted {deleted_count} login records"},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=500)
