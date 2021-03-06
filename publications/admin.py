from django.contrib import admin
from parler.admin import TranslatableAdmin
from django.utils.html import format_html
import data_wizard # Solution to data import madness that had refused to go
from django.forms import TextInput,Textarea #customize textarea row and column size
from import_export.formats import base_formats
from .models import (StgProductDomain,StgKnowledgeProduct,StgResourceType,
    StgResourceCategory)
from commoninfo.admin import OverideImportExport,OverideExport
from regions.models import StgLocation
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter,
    RelatedOnlyDropdownFilter) #custom
from .resources import (StgKnowledgeProductResourceExport,
    StgKnowledgeProductResourceImport,ProductDomainResourceExport,
    ProductTypeResourceExport,ProductCategoryResourceExport,)
from import_export.admin import (ImportExportModelAdmin, ExportMixin,
    ExportActionModelAdmin)
from authentication.models import CustomUser, CustomGroup
from .filters import TranslatedFieldFilter #Danile solution to duplicate filters

#Methods used to register global actions performed on data. See actions listbox
def transition_to_pending (modeladmin, request, queryset):
    queryset.update(comment = 'pending')
transition_to_pending.short_description = "Mark selected as Pending"

def transition_to_approved (modeladmin, request, queryset):
    queryset.update (comment = 'approved')
transition_to_approved.short_description = "Mark selected as Approved"

def transition_to_rejected (modeladmin, request, queryset):
    queryset.update (comment = 'rejected')
transition_to_rejected.short_description = "Mark selected as Rejected"


@admin.register(StgResourceType)
class ResourceTypeAdmin(TranslatableAdmin,OverideExport):
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
        groups = list(request.user.groups.values_list('user',flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        if request.user.is_superuser:
            return qs
        elif user in groups:
            qs_admin=db_locations.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2)
        return qs

    def get_export_resource_class(self):
        return ProductTypeResourceExport

    list_display=['name','code','shortname','description']
    list_display_links =('code', 'name',)
    search_fields = ('translations__name','translations__shortname','code',) #display search field
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated','code',)


@admin.register(StgResourceCategory)
class ResourceCategoryAdmin(TranslatableAdmin,OverideExport):
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
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        if request.user.is_superuser:
            return qs
        elif user in groups:
            qs_admin=db_locations.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2)
        return qs

    def get_export_resource_class(self):
        return ProductCategoryResourceExport

    fieldsets = (
        ('Resource Categorization', {
                'fields':('name','shortname','category','description')
        }),
    )
    list_display=['name','code','shortname','category','description']
    list_display_links =('code', 'name',)
    search_fields = ('translations__name','translations__shortname','code')
    list_per_page = 15 #limit records displayed on admin site to 15
    exclude = ('date_created','date_lastupdated','code',)


# data_wizard.register(StgKnowledgeProduct)
#     "Import Knowledge Resource List",StgKnowledgeProductSerializer)
@admin.register(StgKnowledgeProduct)
class ProductAdmin(TranslatableAdmin,OverideExport,ExportActionModelAdmin):
    from django.db import models
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':100})},
    }

    """
    Serge requested that the form for data input be restricted to user's location.
    Thus, this function is for filtering location to display country level.
    The location is used to filter the dropdownlist based on the request
    object's USER, If the user has superuser privileges or is a member of
    AFRO-DataAdmins, he/she can enter data for all the AFRO member countries
    otherwise, can only enter data for his/her country.===modified 02/02/2021
    """
    def get_queryset(self, request):
        language = request.LANGUAGE_CODE
        qs = super().get_queryset(request).filter(
            translations__language_code=language).order_by(
            'translations__title').filter(
            location__translations__language_code=language).order_by(
            'location__translations__name').distinct()

        # Get a query of groups the user belongs and flatten it to list object
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        # Returns data for all the locations to the lowest location level
        if request.user.is_superuser:
            qs
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
        user = request.user.username
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
                language_code='en')

        if db_field.name == "type":
                kwargs["queryset"] = StgResourceType.objects.filter(
                translations__language_code='en').distinct()

        if db_field.name == "categorization":
                kwargs["queryset"] = StgResourceCategory.objects.filter(
                translations__language_code='en').distinct()

        if db_field.name == "user":
                kwargs["queryset"] = CustomUser.objects.filter(
                username=user)
        return super().formfield_for_foreignkey(db_field, request,**kwargs)

    #to make URl clickable, I changed show_url to just url in the list_display tuple
    def show_external_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.external_url)

    def show_url(self, obj):
        return obj.url if obj.url else 'None'

    show_external_url.allow_tags = True
    show_external_url.short_description= 'External File Link'

    """
    Returns available export formats.
    """
    def get_import_formats(self):
        formats = (
              base_formats.CSV,
              base_formats.XLS,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_import()]

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
              base_formats.CSV,
              base_formats.XLS,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]

    def get_export_resource_class(self):
        return StgKnowledgeProductResourceExport

    def get_import_resource_class(self):
        return StgKnowledgeProductResourceImport

     #This function is used to register permissions for approvals. See signals,py
    def get_actions(self, request):
        actions = super(ProductAdmin, self).get_actions(request)
        if not request.user.has_perm('resources.approve_stgknowledgeproduct'):
           actions.pop('transition_to_approved', None)
        if not request.user.has_perm('resources.reject_stgknowledgeproduct'):
            actions.pop('transition_to_rejected', None)
        if not request.user.has_perm('resources.delete_stgknowledgeproduct'):
            actions.pop('delete_selected', None)
        return actions

    def get_export_resource_class(self):
        return StgKnowledgeProductResourceExport

    def get_import_resource_class(self):
        return StgKnowledgeProductResourceImport

    fieldsets = (
        ('Publication Attributes', {
                'fields':('title','type','categorization','location',)
            }),
            ('Description & Abstract', {
                'fields': ('description', 'abstract',),
            }),
            ('Attribution, Access and Approval Details', {
                'fields': ('author','year_published','internal_url',
                    'external_url','cover_image','comment'),
            }),
            ('Logged Admin/Staff', {
                'fields': ('user',)
            }),
        )

    def get_location(obj):
           return obj.location.name
    get_location.short_description = 'Publication Place'

    def get_type(obj):
           return obj.type.name
    get_type.short_description = 'Type'

    # Format date created to disply only the day, month and year
    def date_created (obj):
        return obj.date_created.strftime("%d-%b-%Y")
    date_created.admin_order_field = 'date_created'
    date_created.short_description = 'Date Created'


    # To display the choice field values use the helper method get_foo_display
    list_display=['title','code',get_type,'author','year_published',get_location,
        'internal_url','show_external_url','get_comment_display',date_created]
    list_select_related = ('user','type','categorization','location',)
    list_display_links = ['code','title',]
    readonly_fields = ('comment',)
    search_fields = ('translations__title','type__translations__name',
        'location__translations__name',) #display search field
    list_per_page = 50 #limit records displayed on admin site to 30
    actions = ExportActionModelAdmin.actions + [transition_to_pending,
        transition_to_approved,transition_to_rejected]
    exclude = ('date_created','date_lastupdated','code','comment')
    list_filter = (
        ('location',TranslatedFieldFilter),
        ('type',TranslatedFieldFilter),
        ('comment',DropdownFilter),
    )


@admin.register(StgProductDomain)
class ProductDomainAdmin(TranslatableAdmin,OverideExport):
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
        groups = list(request.user.groups.values_list('user', flat=True))
        user = request.user.id
        user_location = request.user.location.location_id
        db_locations = StgLocation.objects.all().order_by('location_id')
        if request.user.is_superuser:
            return qs
        elif user in groups:
            qs_admin=db_locations.filter(
                locationlevel__locationlevel_id__gte=1,
                locationlevel__locationlevel_id__lte=2)
        return qs

    def get_export_resource_class(self):
        return ProductDomainResourceExport

    fieldsets = (
        ('Resource Attributes', {
                'fields':('name','shortname','description','parent','level')
            }),
        ('Resource Publications', {
                'fields':('publications',) #afrocode may be null
            }),
        )

    list_select_related = ('parent',)
    list_display=['name','code','shortname','parent','level']
    list_display_links =('name','shortname','code',)
    search_fields = ('translations__name','translations__shortname','code',)

    filter_horizontal = ('publications',) # should display multiselect records
    exclude = ('date_created','date_lastupdated','code',)
    list_per_page = 50 #limit records displayed on admin site to 15
    list_filter = (
        ('parent',TranslatedFieldFilter),
        ('publications',TranslatedFieldFilter,),#Added 16/12/2019 for lookup
    )
