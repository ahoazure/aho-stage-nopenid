from django.contrib import admin
from parler.admin import TranslatableAdmin
from django.utils.translation import gettext_lazy as _ #For translating imported verbose_name
from regions.models import StgLocation
from data_wizard.admin import ImportActionModelAdmin
from data_wizard.sources.models import FileSource,URLSource #customize import sourece
from django.forms import TextInput,Textarea #for customizing textarea row and column size
from commoninfo.admin import OverideImportExport, OverideExport
from .models import (StgCategoryParent,StgCategoryoption,StgMeasuremethod,
    StgValueDatatype,StgDatasource)
from .resources import(DisaggregateCategoryExport,DataSourceExport,
    DisaggregateOptionExport,MeasureTypeExport,DataTypeExport)
from import_export.admin import (ImportExportModelAdmin,
    ImportExportActionModelAdmin,)
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter,
    RelatedOnlyDropdownFilter) #custom import
from .filters import TranslatedFieldFilter #Danile solution to duplicate filters

@admin.register(StgCategoryParent)
class DisaggregateCategoryAdmin(TranslatableAdmin,OverideExport):
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':100})},
    }

    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()
        return qs

    resource_class = DisaggregateCategoryExport #for export only
    list_display=['name','code','shortname','description',]
    list_display_links = ('code', 'name',)
    search_fields = ('translations__name', 'translations__shortname','code',)
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated','code',)


@admin.register(StgCategoryoption)
class DisaggregationAdmin(TranslatableAdmin,OverideExport):
    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()
        return qs

    fieldsets = (
        ('Disaggregation Attributes', {
                'fields': ('name','shortname','category',)
            }),
            ('Detailed Description', {
                'fields': ('description',),
            }),
        )
    resource_class = DisaggregateOptionExport #for export only
    list_display=['name','code','shortname','description','category',]
    list_display_links = ('code', 'name',)
    search_fields = ('translations__name', 'translations__shortname',)
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated',)
    list_filter = (
        ('category',TranslatedFieldFilter,), #Use the comma for inheritance
    )


@admin.register(StgValueDatatype)
class DatatypeAdmin(TranslatableAdmin,OverideExport):
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':100})},
    }

    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()
        return qs

    resource_class = DataTypeExport
    list_display=['name','code','description',]
    list_display_links = ('code', 'name',)
    search_fields = ('translations__name','translations__shortname','code',)
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated','code',)

@admin.register(StgDatasource)
class DatasourceAdmin(TranslatableAdmin,OverideExport):
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':100})},
    }

    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()
        return qs

    fieldsets = (
        ('Data source Attributes', {
                'fields': ('name','shortname','level',)
            }),
            ('Detailed Description', {
                'fields': ('description',),
            }),
        )
    resource_class = DataSourceExport #for export only
    list_display=['name','shortname','code','description','level']
    list_display_links = ('code', 'name',)
    search_fields = ('translations__name', 'translations__shortname',
        'code','translations__level') #display search field
    list_per_page = 50 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated',)
    list_filter = (
        ('translations__level',DropdownFilter,), #Use the comma for inheritance
    )


@admin.register(StgMeasuremethod)
class MeasuredAdmin(TranslatableAdmin,OverideExport):
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':100})},
    }

    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__name').distinct()
        return qs

    resource_class = MeasureTypeExport
    list_display=['name','code','measure_value','description',]
    list_display_links = ('code', 'name',)
    search_fields = ('translations__name','code',) #display search field
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated','code',)

# ------------------------------------------------------------------------------
# The following two admin classes are used to customize the Data_Wizard page.
# The classes overrides admin.py in site-packages/data_wizard/sources/
# ------------------------------------------------------------------------------
class FileSourceAdmin(ImportActionModelAdmin):
    menu_title = _("Import Data File... ")

    """
    Serge requested that the form for data input be restricted to user's location.
    Thus, this function is for filtering location to display country level.
    The location is used to filter the dropdownlist based on the request
    object's USER, If the user has superuser privileges or is a member of
    AFRO-DataAdmins, he/she can enter data for all the AFRO member countries
    otherwise, can only enter data for his/her country.===modified 02/02/2021
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Get a query of groups the user belongs and flatten it to list object
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        # Returns data for all the locations to the lowest location level
        if request.user.is_superuser:
            return qs
        # returns data for AFRO and member countries
        elif user in groups and user_location==1:
            qs_admin=db_locations.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2)
        # return data based on the location of the user logged/request location
        elif user in groups and user_location>1:
            qs=qs.filter(location=user_location)
        else: # return own data if not member of a group
            qs=qs.filter(location=user_location) #to be reconsidered for privacy
        return qs


    """
    Serge requested that the form for input be restricted to user's location.
    Thus, this function is for filtering location to display country level.
    The location is used to filter the dropdownlist based on the request
    object's USER, If the user has superuser privileges or is a member of
    AFRO-DataAdmins, he/she can enter data for all the AFRO member countries
    otherwise, can only enter data for his/her country.=== modified 02/02/2021
    """
    def formfield_for_foreignkey(self, db_field, request =None, **kwargs):
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        language = request.LANGUAGE_CODE
        if db_field.name == "location":
            if request.user.is_superuser:
                kwargs["queryset"] = StgLocation.objects.all().order_by(
                'location_id')
                # Looks up for the location level upto the country level
            elif user in groups:
                kwargs["queryset"] = StgLocation.objects.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2).order_by(
                'location_id')
            else:
                kwargs["queryset"] = StgLocation.objects.filter(
                location_id=request.user.location_id).translated(
                language_code=language)
        return super().formfield_for_foreignkey(db_field, request,**kwargs)
    fields = ('location','name','file',)
    list_display=('name','location','date')
    list_select_related = ('location',)
admin.site.register(FileSource, FileSourceAdmin)


# This class admin class is used to customize change page for the URL data source
class URLSourceAdmin(ImportActionModelAdmin):
    menu_title = _("Import via URL...")
    """
    Serge requested that the form for data input be restricted to user's location.
    Thus, this function is for filtering location to display country level.
    The location is used to filter the dropdownlist based on the request
    object's USER, If the user has superuser privileges or is a member of
    AFRO-DataAdmins, he/she can enter data for all the AFRO member countries
    otherwise, can only enter data for his/her country.===modified 02/02/2021
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Get a query of groups the user belongs and flatten it to list object
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        # Returns data for all the locations to the lowest location level
        if request.user.is_superuser:
            return qs
        # returns data for AFRO and member countries
        elif user in groups and user_location==1:
            qs_admin=db_locations.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2)
        # return data based on the location of the user logged/request location
        elif user in groups and user_location>1:
            qs=qs.filter(location=user_location)
        else: # return own data if not member of a group
            qs=qs.filter(location=user_location) #to be reconsidered for privacy
        return qs


    """
    Serge requested that the form for input be restricted to user's location.
    Thus, this function is for filtering location to display country level.
    The location is used to filter the dropdownlist based on the request
    object's USER, If the user has superuser privileges or is a member of
    AFRO-DataAdmins, he/she can enter data for all the AFRO member countries
    otherwise, can only enter data for his/her country.=== modified 02/02/2021
    """
    def formfield_for_foreignkey(self, db_field, request =None, **kwargs):
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        language = request.LANGUAGE_CODE
        if db_field.name == "location":
            if request.user.is_superuser:
                kwargs["queryset"] = StgLocation.objects.all().order_by(
                'location_id')
                # Looks up for the location level upto the country level
            elif user in groups:
                kwargs["queryset"] = StgLocation.objects.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2).order_by(
                'location_id')
            else:
                kwargs["queryset"] = StgLocation.objects.filter(
                location_id=request.user.location_id).translated(
                language_code=language)
        return super().formfield_for_foreignkey(db_field, request,**kwargs)

    fields = ('location','name','url',)
    list_display=('name','location','url','date',)
    list_select_related = ('location',)
admin.site.register(URLSource,URLSourceAdmin)
