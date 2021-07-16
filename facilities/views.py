from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import (generics,permissions,renderers,)

from commoninfo.permissions import IsOwnerOrReadOnly,CustomDjangoModelPermissions
from .models import (StgFacilityType,StgFacilityOwnership,StgHealthFacility,
    StgServiceDomain,StgLocationCodes,FacilityServiceAvailability,
    FacilityServiceProvision,FacilityServiceReadiness,)

from .serializers import (StgFacilityTypeSerializer,StgFacilityOwnershipSerializer,
    StgServiceDomainSerializer,StgHealthFacilitySerializer,
    FacilityServiceAvailabilitySerializer,FacilityServiceProvisionSerializer,
    FacilityServiceReadinessSerializer,)

class StgFacilityTypeViewSet(viewsets.ModelViewSet):
    serializer_class = StgFacilityTypeSerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,)

    def get_queryset(self):
        language = self.request.LANGUAGE_CODE # get the en, fr or pt from the request
        return StgFacilityType.objects.filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()


class StgFacilityOwnershipViewSet(viewsets.ModelViewSet):
    serializer_class = StgFacilityOwnershipSerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,)

    def get_queryset(self):
        language = self.request.LANGUAGE_CODE # get the en, fr or pt from the request
        return StgFacilityOwnership.objects.filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()


class StgServiceDomainViewSet(viewsets.ModelViewSet):
    serializer_class = StgServiceDomainSerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,IsOwnerOrReadOnly)

    def get_queryset(self):
        language = self.request.LANGUAGE_CODE # get the en, fr or pt from the request
        return StgServiceDomain.objects.filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()


class StgHealthFacilityViewSet(viewsets.ModelViewSet):
    serializer_class = StgHealthFacilitySerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,IsOwnerOrReadOnly)

    def get_queryset(self):
        language = self.request.LANGUAGE_CODE # get the en, fr or pt from the request
        queryset = StgHealthFacility.objects.filter(
            location__location__translations__language_code=language).order_by(
            'location__translations__name').distinct()

        user = self.request.user.id
        groups = list(self.request.user.groups.values_list('user', flat=True))
        location = self.request.user.location_id
        if self.request.user.is_superuser:
            qs=queryset
        elif user in groups: # Match fact location field to that of logged user
            qs=queryset.filter(location=location)
        else:
            qs=queryset.filter(user=user)
        return qs



class  FacilityServiceAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = FacilityServiceAvailabilitySerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,IsOwnerOrReadOnly)

    def get_queryset(self):
        queryset = FacilityServiceAvailability.objects.all().order_by(
                    'facility').distinct()
        user = self.request.user.id
        groups = list(self.request.user.groups.values_list('user', flat=True))
        location = self.request.user.location_id
        if self.request.user.is_superuser:
            qs=queryset
        else:
            qs=queryset.filter(user=user)
        return qs


class  FacilityServiceCapacityViewSet(viewsets.ModelViewSet):
    serializer_class = FacilityServiceProvisionSerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,IsOwnerOrReadOnly)

    def get_queryset(self):
        queryset = FacilityServiceProvision.objects.all().order_by(
                    'facility').distinct()
        user = self.request.user.id
        groups = list(self.request.user.groups.values_list('user', flat=True))
        location = self.request.user.location_id
        if self.request.user.is_superuser:
            qs=queryset
        else:
            qs=queryset.filter(user=user)
        return qs



class  FacilityServiceReadinessViewSet(viewsets.ModelViewSet):
    serializer_class = FacilityServiceReadinessSerializer
    permission_classes = (permissions.IsAuthenticated,
        CustomDjangoModelPermissions,IsOwnerOrReadOnly)

    def get_queryset(self):
        queryset = FacilityServiceReadiness.objects.all().order_by(
                    'facility').distinct()
        user = self.request.user.id
        groups = list(self.request.user.groups.values_list('user', flat=True))
        location = self.request.user.location_id
        if self.request.user.is_superuser:
            qs=queryset
        else:
            qs=queryset.filter(user=user)
        return qs
