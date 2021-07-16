from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from rest_framework.serializers import (ModelSerializer, ReadOnlyField)
from .models import (StgHealthFacility,StgFacilityType,StgFacilityOwnership,
    StgServiceDomain,FacilityServiceAvailability,FacilityServiceProvision,
    FacilityServiceReadiness,)



class StgFacilityTypeSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgFacilityType)

    class Meta:
        model = StgFacilityType
        fields = ['uuid','code','translations']


class StgFacilityOwnershipSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgFacilityOwnership)

    class Meta:
        model = StgFacilityOwnership
        fields = ['uuid', 'code','location','translations']


class StgServiceDomainSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgServiceDomain)

    class Meta:
        model = StgServiceDomain
        fields = ['uuid', 'code','category','level','parent','translations']


class StgHealthFacilitySerializer(ModelSerializer):
    location_name = ReadOnlyField(source='location.location.name')
    class Meta:
        model = StgHealthFacility

        fields = ('uuid','code','type','location','location_name','owner','name',
                    'shortname','admin_location', 'description','latitude',
                    'longitude','altitude','url','status',)

        data_wizard = {
        'header_row': 0,
        'start_row': 1,
        'show_in_list': True,
    }


class FacilityServiceAvailabilitySerializer(ModelSerializer):

    class Meta:
        model = FacilityServiceAvailability

        fields = ('uuid','code','facility','domain','intervention','service',
        'provided','specialunit','staff','infrastructure','supplies',
        'date_assessed',)

        data_wizard = {
        'header_row': 0,
        'start_row': 1,
        'show_in_list': True,
    }


class FacilityServiceProvisionSerializer(ModelSerializer):

    class Meta:
        model = FacilityServiceProvision

        fields = ('uuid','code','facility','domain','units','available',
        'functional','date_assessed',)

        data_wizard = {
        'header_row': 0,
        'start_row': 1,
        'show_in_list': True,
    }


class FacilityServiceReadinessSerializer(ModelSerializer):

    class Meta:
        model = FacilityServiceReadiness

        fields = ('uuid','code','facility','domain','units','available',
        'require','date_assessed',)


        data_wizard = {
        'header_row': 0,
        'start_row': 1,
        'show_in_list': True,
    }
