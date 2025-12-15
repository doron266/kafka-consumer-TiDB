from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

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
    responses={
        200: "One or all users in JSON format",
        400: "Bad request",
        404: "User not found",
        500: "Internal server error",
    },
)
@api_view(["GET"])
def get_users(request):
    if "email" in request.GET:
        email = request.GET["email"]
        if not email:
            return Response(
                {"result": "error", "message": "Email parameter is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = get_object_or_404(User, email=email)
            return Response(UserSerializer(user).data)
        except Http404:
            return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new user",
    operation_description="Create a new user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password (store hashed in production)"),
            "auth_token": openapi.Schema(type=openapi.TYPE_STRING, description="Optional auth token"),
        },
        required=["username", "email", "password"],
    ),
    responses={
        201: "Created user",
        400: "Bad request",
        500: "Internal server error",
    },
)
@api_view(["POST"])
def add_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="put",
    operation_summary="Updates existing user",
    operation_description="Update an existing user by email. Email itself cannot be changed.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Update username"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Update password"),
            "auth_token": openapi.Schema(type=openapi.TYPE_STRING, description="Update auth token"),
        },
        required=[],
    ),
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email of the user to update", type=openapi.TYPE_STRING)
    ],
    responses={
        200: "Updated user",
        400: "Bad request",
        404: "User not found",
        500: "Internal server error",
    },
)
@api_view(["PUT"])
def update_user(request):
    email = request.query_params.get("email")

    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(User, email=email)
        request_data = request.data.copy()
        request_data["email"] = email  # prevent changing email
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        serializer = UserSerializer(user, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes existing user",
    operation_description="Delete an existing user by email.",
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email of the user to be deleted", type=openapi.TYPE_STRING)
    ],
    responses={
        204: "User deleted",
        400: "Bad request",
        404: "User not found",
        500: "Internal server error",
    },
)
@api_view(["DELETE"])
def delete_user(request):
    email = request.query_params.get("email")

    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(User, email=email)
        user.delete()
        return Response({"result": "success", "message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# LOGINS
# ----------------------------

@swagger_auto_schema(
    method="get",
    operation_summary="Lists all logins or a single login by email",
    operation_description="Retrieve all login records or a single login record by email.",
    manual_parameters=[
        openapi.Parameter(
            "email",
            openapi.IN_QUERY,
            description="Optional. If provided, returns login records filtered by this email.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: "One or all logins in JSON format",
        400: "Bad request",
        500: "Internal server error",
    },
)
@api_view(["GET"])
def get_logins(request):
    email = request.query_params.get("email")

    try:
        if email is not None:
            if not email:
                return Response(
                    {"result": "error", "message": "Email parameter is missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logins = Login.objects.filter(email=email).order_by("-created_at")
            return Response(LoginSerializer(logins, many=True).data)

        logins = Login.objects.all().order_by("-created_at")
        return Response(LoginSerializer(logins, many=True).data)

    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new login record",
    operation_description="Create a new login record (audit/log). Timestamp is auto-created.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
        },
        required=["username", "email"],
    ),
    responses={
        201: "Created login record",
        400: "Bad request",
        500: "Internal server error",
    },
)
@api_view(["POST"])
def add_login(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # created_at auto_now_add
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes login records by email",
    operation_description="Delete login records by email (bulk delete).",
    manual_parameters=[
        openapi.Parameter("email", openapi.IN_QUERY, description="Email of login records to delete", type=openapi.TYPE_STRING)
    ],
    responses={
        204: "Deleted login records",
        400: "Bad request",
        500: "Internal server error",
    },
)
@api_view(["DELETE"])
def delete_logins_by_email(request):
    email = request.query_params.get("email")

    if not email:
        return Response({"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        deleted_count, _ = Login.objects.filter(email=email).delete()
        return Response(
            {"result": "success", "message": f"Deleted {deleted_count} login records"},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
