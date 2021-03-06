# -*- coding: utf-8 -*-

"""
.. module:: api
"""

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets

from apps.volontulo import models
from apps.volontulo import permissions
from apps.volontulo import serializers
from apps.volontulo.authentication import CsrfExemptSessionAuthentication
from apps.volontulo.views import logged_as_admin


@api_view(['POST'])
@authentication_classes((CsrfExemptSessionAuthentication,))
@permission_classes((AllowAny,))
def login_view(request):
    """REST API login view."""
    if not request.user.is_authenticated():
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is None or not user.is_active:
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        return Response(
            serializers.UserSerializer(user).data,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializers.UserSerializer(request.user).data,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
@permission_classes((AllowAny,))
def logout_view(request):
    """REST API logout view."""
    if request.user.is_authenticated():
        logout(request)
        return Response(None, status=status.HTTP_200_OK)
    return Response(None, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
def current_user(request):
    """REST API view for current user."""
    if request.user.is_authenticated():
        return Response(
            serializers.UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )

    return Response(None, status=status.HTTP_200_OK)


class OfferViewSet(viewsets.ModelViewSet):

    """REST API offers viewset."""

    serializer_class = serializers.OfferSerializer
    permission_classes = (permissions.OfferPermission,)

    def get_queryset(self):
        """Queryset depends on user role."""
        if logged_as_admin(self.request):
            return models.Offer.objects.get_for_administrator()
        return models.Offer.objects.get_weightened()


class OrganizationViewSet(viewsets.ModelViewSet):

    """REST API organizations viewset."""

    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    permission_classes = (permissions.OrganizationPermission,)
