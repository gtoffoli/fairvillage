# from django.conf.urls.defaults import patterns, include, url
# MMR old version - from django.conf.urls import patterns, include, url
from django.conf.urls import include, url

from django.conf import settings
from django.views.generic import TemplateView

from fairvillage import views as fairvillage_views
from pois import views as pois_views
from roma import views as roma_views

from fairvillage.api import get_components, server_version, search_keys, radial_search, street_search, bbox_search, zone_search, get_pois
# Routers provide an easy way of automatically determining the URL conf.
from fairvillage.api import fv_router

# Add before admin.autodiscover() and any form import for that matter:
"""
MMR
import autocomplete_light
autocomplete_light.autodiscover()
"""

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
from django.contrib.gis import admin
admin.autodiscover()

#urlpatterns = patterns('',
urlpatterns = [
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(fv_router.urls)),
    url(r'^server_version/$', server_version),
    url(r'^search_keys/$', search_keys),
    url(r'^radial_search/$', radial_search),
    url(r'^rest/bbox_search/$', bbox_search),
    url(r'^bbox_search/$', bbox_search),
    url(r'^get_pois/$', get_pois),
    url(r'^zone_search/$', zone_search),
    url(r'^street_search/$', street_search),
    # url(r'^fv/$', 'fairvillage.views.home', name='fv_home'),
    url(r'^$', fairvillage_views.home, name='fv_home'),
    url(r'^', include(fv_router.urls)),
    url(r'^indice-zona/(?P<zone_slug>.+)/$', fairvillage_views.zone_category_index_by_slug, name='zona-category'),
    url(r'^zona/(?P<zone_slug>.+)/$', fairvillage_views.zone_detail_by_slug, name='zona'),
    url(r'^rete/(?P<poi_slug>[\w-]+)/zona/(?P<zone_slug>.+)/$', fairvillage_views.poi_network_zone_by_slug, name='rete-zona'),
    url(r'^risorsa/(?P<poi_slug>[\w-]+)/rete/$', fairvillage_views.poi_network_by_slug, name='risorsa-rete'),
    url(r'^risorsa/(?P<poi_slug>[\w-]+)/mappa/$', fairvillage_views.resource_map_by_slug, name='risorsa-mappa'),
    url(r'^risorsa/(?P<poi_slug>.+)/$', fairvillage_views.poi_detail_by_slug, name='risorsa'),
    url(r'^categoria/(?P<klass_slug>[\w-]+)/zona/(?P<zone_slug>.+)/$', fairvillage_views.poitype_zone_detail_by_slugs, name='categoria-zona'),
    url(r'^categoria/(?P<klass_slug>.+)/$', fairvillage_views.poitype_detail_by_slug, name='categoria'),
    url(r'^toponimo/(?P<street_slug>.+)/$', fairvillage_views.street_detail_by_slug, name='toponimo'),
    url(r'^viewport$', fairvillage_views.viewport, name='refresh viewport'),
    url(r'^categorie$', fairvillage_views.category_index),
    url(r'^macrozone', fairvillage_views.zone_index_map, {'zonetype_id': 0, 'prefix': 'RM.'}, name='macrozone'),
    url(r'^province', fairvillage_views.zone_index_map, {'zonetype_id': 0, 'prefix': 'PR.'}, name='province'),
    url(r'^municipi$', fairvillage_views.zone_index_map, {'zonetype_id': 7, 'prefix': 'M.'}, name='municipi'),
    url(r'^reti-di-risorse$', fairvillage_views.resource_networks),
    url(r'^annota-risorsa/(?P<poi_slug>.+)/$', fairvillage_views.poi_add_note_by_slug, name='feedback'),
    url(r'^', include('roma.urls')),
]

# urlpatterns += patterns('',
urlpatterns += [
    url (r'^accounts/signup/$', roma_views.signup, name='account_signup'), # 131015 GT
    url (r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', TemplateView.as_view(template_name='account/profile.html'), name='welcome',),
]   
