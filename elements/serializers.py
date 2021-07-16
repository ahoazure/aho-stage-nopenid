from rest_framework.serializers import (ReadOnlyField, Serializer,
    DecimalField,ModelSerializer,HyperlinkedModelSerializer,)
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from elements.models import (StgDataElement, FactDataElement)

class StgDataElementSerializer(TranslatableModelSerializer,HyperlinkedModelSerializer):
    translations = TranslatedFieldsField(shared_model=StgDataElement)
    class Meta:
        model = StgDataElement
        fields = ['dataelement_id','code','aggregation_type','translations']


# This class overrides the decimal field in order to round off the decimal places.
class RoundedDecimalField(DecimalField):
    def validate_precision(self, value):
        return value

# Force import wizard to ignore the decimal places and required validation to allow null
class FactDataElementSerializer(ModelSerializer,):
    location_name = ReadOnlyField(source='location.name')
    value = RoundedDecimalField(
        max_digits=20, decimal_places=3,required=True,allow_null=False)
    target_value = RoundedDecimalField(
        max_digits=20,decimal_places=3,required=False,allow_null=True)

    class Meta:
        model = FactDataElement
        fields = [
            'uuid','fact_id','dataelement','location','location_name',
            'categoryoption','datasource','valuetype','value','target_value',
            'start_year','end_year','period','comment']
