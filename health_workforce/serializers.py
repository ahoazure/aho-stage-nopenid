from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from rest_framework.serializers import (ModelSerializer, ReadOnlyField)
from .models import (StgInstitutionProgrammes,StgTrainingInstitution,
    StgHealthCadre,StgHealthWorkforceFacts,StgInstitutionType,)



class StgInstitutionProgrammesSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgInstitutionProgrammes)

    class Meta:
        model = StgInstitutionProgrammes
        fields = ['uuid','code','translations']


class StgInstitutionTypeSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgInstitutionType)

    class Meta:
        model = StgInstitutionType
        fields = ['uuid','code','translations']


class StgTrainingInstitutionSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgTrainingInstitution)

    class Meta:
        model = StgTrainingInstitution
        fields = ['uuid', 'code','location','type','programmes','translations']


class StgHealthCadreSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgHealthCadre)

    class Meta:
        model = StgHealthCadre
        fields = ['uuid', 'code','parent','translations']


class StgHealthWorkforceFactsSerializer(ModelSerializer):
    location_name = ReadOnlyField(source='location.name')
    class Meta:
        model = StgHealthWorkforceFacts

        fields = ('uuid','cadre','location','location_name','categoryoption',
                    'datasource','measuremethod','value', 'start_year',
                    'end_year','period','status',)

        data_wizard = {
        'header_row': 0,
        'start_row': 1,
        'show_in_list': True,
    }
