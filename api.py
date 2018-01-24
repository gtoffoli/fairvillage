'''
Created on 15/ott/2015
@author: giovanni
'''

"""
try:
    from django.utils import simplejson
except:
    import json as simplejson
"""
import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import get_object_or_404
# from django.db.models import Q
from rest_framework import status
from rest_framework import routers, serializers, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from django.contrib.gis.geos import Polygon, fromstr

from pois.models import Zone, Odonym, Poitype, Poi

# zonetype_ids = [3, 7,]
zonetype_ids = [7,]
# poitype_slugs = ['assistenza-a-stranieri-e-immigrati', 'biblioteche-comunali', 'rilascio-tessera-sanitaria-stp', 'case-della-salute', 'consultori-familiari', 'italiano-per-stranieri', 'uffici-di-collocamento', 'centri-per-limmigrazione', 'ethnic-communities',]
# poitype_slugs = ['assistenza-a-stranieri-e-immigrati', 'biblioteche-comunali', 'rilascio-tessera-sanitaria-stp', 'case-della-salute', 'consultori-familiari', 'italiano-per-stranieri', 'asili-nido', 'scuole-dell-infanzia','scuole-primarie-elementari',]
from fairvillage.settings import POITYPE_SLUGS as poitype_slugs

poitypes = Poitype.objects.filter(slug__in=poitype_slugs)
poi_klasses = [poitype.klass for poitype in poitypes]

SERVER_VERSION = 4
VERSION_MAP = {
   0: '2015-10-01 00:00',
   1: '2015-10-31 00:00',
   2: '2015-11-01 17:00',
   3: '2015-11-12 12:00',
   4: '2015-12-11 12:00',
}
CLEAR_MAP = {
   2: ['categories'],
   3: ['zones'],
   4: ['categories'],
}
FIRST_SERVER_TIME = VERSION_MAP[0]
LAST_SERVER_TIME = VERSION_MAP[SERVER_VERSION]

DEFAULT_COLOR = 'yellow'
COLOR_MAP = {
  'black': 'violet',
  'blue': 'azure',
  'blueviolet': 'purple',
  'brown': 'yellow',
  'firebrick': 'yellow',
  'green': 'green',
  'orange': 'orange',
  'red': 'red',
  'other': DEFAULT_COLOR, 
}

# Routers provide an easy way of automatically determining the URL conf.
fv_router = routers.DefaultRouter()

"""
from django.contrib.auth.models import User
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
fv_router.register(r'users', UserViewSet)
"""

def JsonResponse(request, serializer):
    if request.path.count('/api/'):
        return Response(serializer.data)
    else:
        # return HttpResponse(simplejson.dumps(serializer.data), content_type='application/json')
        return HttpResponse(json.dumps(serializer.data), content_type='application/json')

class ZoneSerializer(serializers.Serializer):
    zones = serializers.DictField(label='zones')
class ZoneDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID')
    code = serializers.CharField(label='klass', max_length=8)
    zonetype = serializers.IntegerField(label='zonetype')
    name = serializers.CharField(label='name', max_length=100)
class ZoneViewSet(viewsets.ViewSet):
    queryset = Zone.objects.filter(zonetype_id__in=zonetype_ids)
    def retrieve(self, request, pk=None):
        zone = Zone.objects.get(pk=pk)
        zone_dict = {'id': pk, 'name': zone.name, 'zonetype': zone.zonetype.id, 'code': zone.code,}
        serializer = ZoneDetailSerializer(zone_dict)
        return JsonResponse(request, serializer)
    def list(self, request):
        zones = {}
        for zone in self.queryset:
            zones[zone.id] = {'name': zone.name, 'code': zone.code,}
        serializer = ZoneSerializer({'zones': zones,})
        return JsonResponse(request, serializer)
fv_router.register(r'zones', ZoneViewSet)

class ZoneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ('id', 'name')
class ZoneListViewSet(viewsets.ViewSet):
    queryset = Zone.objects.filter(zonetype_id__in=zonetype_ids)
    def list(self, request):
        serializer = ZoneListSerializer(self.queryset, many=True)
        return JsonResponse(request, serializer)
fv_router.register(r'zone_list', ZoneListViewSet)

class StreetsSerializer(serializers.Serializer):
    streets = serializers.DictField(label='streets')
class StreetDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID')
    name = serializers.CharField(label='name', max_length=100)
    location = serializers.DictField(label='location')
class StreetViewSet(viewsets.ViewSet):
    queryset = Odonym.objects.filter(poi_street__isnull=False).distinct().order_by('id')
    def retrieve(self, request, pk=None):
        odonym = Odonym.objects.get(pk=pk)
        street = {'id': pk, 'name': odonym.name, 'location': odonym.fw_core_location(),}
        serializer = StreetDetailSerializer(street)
        return JsonResponse(request, serializer)
    def list(self, request):
        streets = {}
        for odonym in self.queryset:
            streets[odonym.id] = {'name': odonym.name, 'location': odonym.fw_core_location(),}
        serializer = StreetsSerializer({'streets': streets,})
        return JsonResponse(request, serializer)
fv_router.register(r'streets', StreetViewSet)

class StreetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Odonym
        fields = ('id', 'name')
class StreetListViewSet(viewsets.ViewSet):
    queryset = Odonym.objects.filter(poi_street__isnull=False).distinct().order_by('id')
    def list(self, request):
        serializer = StreetListSerializer(self.queryset, many=True)
        return JsonResponse(request, serializer)
fv_router.register(r'street_list', StreetListViewSet)

class CategorySerializer(serializers.Serializer):
    categories = serializers.DictField(label='categories')
class CategoryDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID')
    icon = serializers.CharField(label='icon', max_length=20)
    slug = serializers.CharField(label='name', max_length=50)
    name = serializers.DictField(label='name')
class CategoryViewSet(viewsets.ViewSet):
    queryset = Poitype.objects.filter(slug__in=poitype_slugs)
    def retrieve(self, request, pk=None):
        poitype = Poitype.objects.get(pk=pk)
        category = {'id': pk, 'icon': poitype.icon, 'name': poitype.get_names(),}
        serializer = CategoryDetailSerializer(category)
        return JsonResponse(request, serializer)
    def list(self, request):
        categories = {}
        for poitype in self.queryset:
            # categories[poitype.klass] = {'name': poitype.slug, 'label': poitype.get_names(),}
            categories[poitype.klass] = {'color': poitype.color, 'label': poitype.get_names(),}
        serializer = CategorySerializer({'categories': categories,})
        return JsonResponse(request, serializer)

fv_router.register(r'categories', CategoryViewSet)

def get_components(request):
    components = ['fw_core', 'fw_contact', 'fw_fairvillage',]
    # return HttpResponse(simplejson.dumps({'components': components,}), content_type='application/json')
    return HttpResponse(json.dumps({'components': components,}), content_type='application/json')

class SearchKeySerializer(serializers.Serializer):
    search_keys = serializers.DictField(label='search_keys')
def search_keys(request):
    client_version = int(request.GET.get('client_version', 0))
    LAST_CLIENT_TIME = VERSION_MAP[client_version]
    packed = request.GET.get('packed', '')
    search_keys = { 'server_version': SERVER_VERSION }
    clear_keys = []
    if SERVER_VERSION > client_version:
        for i in range(client_version+1, SERVER_VERSION+1):
            for key in CLEAR_MAP.get(i, []):
                if key not in clear_keys:
                    clear_keys.append(key)
    if clear_keys:
        search_keys["clear"] = clear_keys
    print (client_version, LAST_CLIENT_TIME, SERVER_VERSION, LAST_SERVER_TIME, clear_keys)
    if 'zones' in clear_keys:
        queryset = Zone.objects.filter(zonetype_id__in=zonetype_ids)
    else:
        queryset = Zone.objects.filter(zonetype_id__in=zonetype_ids, modified__gt=LAST_CLIENT_TIME)
    n_zones = queryset.count()
    if packed:
        zones = '|'.join(['%s %s' % (zone.id, zone.name) for zone in queryset])
    else:
        zones = {}
        for zone in queryset:
            zones[zone.id] = {'name': zone.name, 'code': zone.code,}
    if zones:
        search_keys["zones"] = zones
    if 'streets' in clear_keys:
        queryset = Odonym.objects.filter(poi_street__isnull=False).distinct()
    else:
        queryset = Odonym.objects.filter(poi_street__isnull=False, modified__gt=LAST_CLIENT_TIME).distinct()
    n_streets = queryset.count()
    if packed:
        streets =  '|'.join(['%s %s' % (odonym.id, odonym.name) for odonym in queryset])
    else:
        streets = {}
        for odonym in queryset:
            streets[odonym.id] = {'name': odonym.name, 'location': odonym.fw_core_location(),}
    if streets:
        search_keys["streets"] = streets
    if 'categories' in clear_keys:
        queryset = Poitype.objects.filter(slug__in=poitype_slugs)
    else:
        queryset = Poitype.objects.filter(slug__in=poitype_slugs, modified__gt=LAST_CLIENT_TIME)
    n_categories = queryset.count()
    categories = {}
    for poitype in queryset:
        color = poitype.color or 'other'
        color =  COLOR_MAP.get(color.lower(), DEFAULT_COLOR)
        label = poitype.get_names()
        label['_def'] = 'it'
        categories[poitype.klass] = {'color': color, 'label': label}
    if categories:
        search_keys["categories"] = categories
    print (n_zones, n_streets, n_categories)
    serializer = SearchKeySerializer({'search_keys': search_keys,})
    return JsonResponse(request, serializer)

def poi_dict(poi, components=['fw_core']):
    poi_dict = {}
    for component in components:
        c_dict = {}
        if component in ['fw_core', 'fw_core_min',]:
            c_dict['category'] = poi.fw_core_category()
            c_dict['name'] = poi.fw_core_name()
            c_dict['location'] = poi.fw_core_location()
        if component in ['fw_core',]:
            c_dict['description'] = poi.fw_core_description()
            # c_dict['last_update'] = poi.fw_core_last_update()
            c_dict['source'] = poi.source or ''
        if component == 'fw_contact':
            c_dict['postal'] = poi.fw_contact_postal()
            mailto = poi.fw_contact_mailto()
            if mailto:
                c_dict['mailto'] = mailto
            phone = poi.fw_contact_phone()
            if phone:
                c_dict['phone'] = phone
        if component == 'fw_fairvillage':
            web = poi.fw_fairvillage_web()
            if web:
                c_dict['web'] = web
            text = poi.fw_fairvillage_text()
            if text:
                c_dict['text'] = text
            video = poi.fw_fairvillage_video()
            if video:
                c_dict['video'] = video
            hosted_by = poi.fw_fairvillage_hosted_by()
            if hosted_by:
                c_dict['hosted_by'] = hosted_by
            c_dict['state'] = poi.state
            c_dict['notes'] = ''
        if c_dict:       
            poi_dict[component] = c_dict
    return poi_dict

class PoiSerializer(serializers.Serializer):
    pois = serializers.DictField(label='pois')
class PoiDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID')
    name = serializers.CharField(label='name', max_length=100)
    category = serializers.CharField(label='category')
    description = serializers.CharField(label='description', max_length=200)
    location = serializers.DictField(label='location')
class PoiViewSet(viewsets.ViewSet):
    queryset = Poi.objects.filter(poitype_id__in=poi_klasses)
    def list(self, request):
        pois = {}
        for poi in self.queryset:
            pois[poi.id] = { 'name': poi.name, 'category': poi.poitype.slug, }
        serializer = PoiSerializer({'pois': pois,})
        return JsonResponse(request, serializer)
    def retrieve(self, request, pk=None):
        poi = Poi.objects.get(pk=pk)
        resource = {'id': pk}
        resource['name'] = poi.name
        resource['category'] = poi.poitype.slug
        resource['description'] = poi.fw_core_description()
        resource['location'] = poi.fw_core_location()
        serializer = PoiDetailSerializer(resource)
        return JsonResponse(request, serializer)
fv_router.register(r'pois', PoiViewSet)

def radial_search(request):
    latitude = request.GET.get('lat', '')
    longitude = request.GET.get('lon', '')
    if not latitude or not longitude:
        pass
    pnt = fromstr('POINT(%s %s)' % (longitude, latitude))
    radius = float(request.GET.get('radius', 1))
    # queryset = Poi.objects.filter(point__distance_lt=(pnt, radius*1000), state=1)
    queryset = Poi.objects.filter(point__distance_lt=(pnt, radius*1000), state__in=[0, 1])
    category = request.GET.get('category', '')
    if category:
        klasses = category.split(',')
    else:
        klasses = poi_klasses
    components = request.GET.get('component', '')
    if components:
        components = components.split(',')
    else:
        components = ['fw_core_min',]
    queryset = queryset.filter(poitype_id__in=klasses)
    pois = {}
    for poi in queryset.all():
        pois[poi.id] = poi_dict(poi, components=components)
    print (len(pois.keys()))
    serializer = PoiSerializer({'pois': pois,})
    # return HttpResponse(simplejson.dumps(serializer.data), content_type='application/json')
    return HttpResponse(json.dumps(serializer.data), content_type='application/json')

def street_search(request):
    street = request.GET.get('street', '')
    if not street:
        pass
    street = get_object_or_404(Odonym, pk=int(street))
    position = street.position()
    request.GET = request.GET.copy()
    request.GET['lat'] = position['latitude']
    request.GET['lon'] = position['longitude']
    return radial_search(request)

def bbox_search(request):
    north = request.GET.get('north', '')
    south = request.GET.get('south', '')
    east = request.GET.get('east', '')
    west = request.GET.get('west', '')
    if not north or not south or not east or not west:
        pass
    north = float(north)
    south = float(south)
    east = float(east)
    west = float(west)
    bbox = (west, south, east, north)
    geom = Polygon.from_bbox(bbox)
    # queryset = Poi.objects.filter(point__within=geom, state=1)
    queryset = Poi.objects.filter(point__within=geom, state__in=[0, 1])
    category = request.GET.get('category', '')
    if category:
        klasses = category.split(',')
    else:
        klasses = poi_klasses
    components = request.GET.get('component', '')
    if components:
        components = components.split(',')
    else:
        components = ['fw_core_min',]
    queryset = queryset.filter(poitype_id__in=klasses)
    pois = {}
    for poi in queryset.all():
        pois[poi.id] = poi_dict(poi, components=components)
    print (len(pois.keys()))
    serializer = PoiSerializer({'pois': pois,})
    # return HttpResponse(simplejson.dumps(serializer.data), content_type='application/json')
    return HttpResponse(json.dumps(serializer.data), content_type='application/json')

def zone_search(request):
    zones = request.GET.get('zone', '')
    if zones:
        zones = zones.split(',')
    else:
        pass # error
    # queryset = Poi.objects.filter(zones__in=zones, state=1)
    queryset = Poi.objects.filter(zones__in=zones, state__in=[0, 1])
    category = request.GET.get('category', '')
    if category:
        klasses = category.split(',')
    else:
        klasses = poi_klasses
    components = request.GET.get('component', '')
    if components:
        components = components.split(',')
    else:
        components = ['fw_core_min',]
    queryset = queryset.filter(poitype_id__in=klasses)
    pois = {}
    for poi in queryset.all():
        pois[poi.id] = poi_dict(poi, components=components)
    serializer = PoiSerializer({'pois': pois,})
    # return HttpResponse(simplejson.dumps(serializer.data), content_type='application/json')
    return HttpResponse(json.dumps(serializer.data), content_type='application/json')

def get_pois(request):
    poi_id = request.GET.get('poi_id', '')
    if not poi_id:
        pass
    poi_ids = poi_id.split(',')
    poi_ids = [int(poi_id) for poi_id in poi_ids]
    components = request.GET.get('component', '')
    pois = Poi.objects.filter(id__in=poi_ids).all()
    pois_dict = {}
    if components:
        for poi in pois:
            pois_dict[poi.id] = poi_dict(poi, components=components)
    else:
        for poi in pois:
            pois_dict[poi.id] = poi_dict(poi)
    serializer = PoiSerializer({'pois': pois_dict,})
    # return HttpResponse(simplejson.dumps(serializer.data), content_type='application/json')
    return HttpResponse(json.dumps(serializer.data), content_type='application/json')

def server_version(request):
    data = {'server_version': SERVER_VERSION}
    # return HttpResponse(simplejson.dumps(data), content_type='application/json')
    return HttpResponse(json.dumps(data), content_type='application/json')
 
@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})

from django.contrib.gis.geos import Point
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def add_poi(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest()
    json_data=json.loads(request.body)
    fw_core = json_data.get('fw_core', {})
    source = fw_core.get('source', '')
    if not source:
        return HttpResponseForbidden()
    category = fw_core.get('category', '')
    name = fw_core.get('name', '')
    description = fw_core.get('description', {})
    if description:
        description = description.get(description.get('_def', ''), '').strip()[:120]
    if not category and name and description:
        return HttpResponseBadRequest()
    location = fw_core.get('location', {})
    wgs84 = location.get('wgs84', {})
    latitude = wgs84.get('latitude', '')
    longitude = wgs84.get('longitude', '')
    fw_contact = json_data.get('fw_contact', {})
    phone = fw_contact.get('phone', [])
    if phone:
        phone = [item.strip() for item in phone.split('|')]
    email = fw_contact.get('mailto', [])
    if email:
        email = [item.strip() for item in email.split('|')]
    postal = fw_contact.get('postal', None)
    if postal:
        street_address = postal[0]
        if street_address:
            if len(postal) == 2:
                street_address = '%s - %s' % (street_address, postal[1])
    else:
        street_address = ''
    if not (street_address or (latitude and longitude)):
        return HttpResponseBadRequest()
    fw_fairvillage = json_data.get('fw_fairvillage', {})
    feeds = []
    web = fw_fairvillage.get('web', [])
    if web:
        web = [item.strip() for item in web.split('|')]
        for item in web[:]:
            if item.count('feed'):
                feeds.append(item)
                web.remove(item)
    video = fw_fairvillage.get('video', [])
    if video:
        video = [item.strip() for item in video.split('|')]
        for item in video[:]:
            if not item.count('embed'):
                web.append(item)
                video.remove(item)
    notes = fw_fairvillage.get('notes', '').strip()
    text = fw_fairvillage.get('text', {})
    if text:
        text = text.get(text.get('_def', ''), '').strip()
    """
    try:
    """
    if True:
        poi = Poi(name=name, poitype_id=category, short=description, source=source, owner_id=1)
        if latitude and longitude:
            poi.point = Point(longitude, latitude,)
        if street_address:
            poi.street_address = street_address
        if phone:
            poi.phone = '\n'.join(phone)
        if email:
            poi.email = '\n'.join(email)
        if web or video:
            poi.web = '\n'.join(web)
        if video:
            poi.video = '\n'.join(video)
        if feeds:
            poi.feeds = '\n'.join(feeds)
        if text:
            poi.description = text
        if notes:
            poi.notes = notes
        poi.save()
        poi.update_zones(zonetypes=[7,])
    """ 
    except:
        return HttpResponseServerError()     
    """   
    data = {"created_poi": {
       "uuid": "%s-%d" % (source, poi.id),
       "timestamp": 0
       }
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

#   "source": {'name': 'FairVillage mobile', 'id': '3400727780'},
test_poi = {
"fw_core": {
    "source": "FairVillage mobile - 3400727780",
    "category": "0529035810",
    "name": "Consultorio Familiare di Via Agudio",
    "description": {"_def": "it", "it": "A Lunghezza. Donna: mercoled\u00ec 8:00-13:30. Bambino:  mar-mer 8:30-13:30, mercoled\u00ec 14:00-17:00."},
    "location": {"wgs84": {"longitude": 12.67037, "latitude": 41.92332}}
},
"fw_contact": {
    "phone": "064143.6420|06 44231115",
    "mailto": "comunicazioni@linkroma.it|toffoli@linkroma.it  (manager)",
    "postal": ["Via Tommaso Agudio 5", "00132 Roma"]
},
"fw_fairvillage": {
   "web": "www.aslromab.it/cittadini/distretti/terzo/consultori.php  Pagina nel sito della ASL RM B|www.aslromab.it/cittadini/distretti/terzo/guida_3_Distretto.pdf  Opuscolo su gravidanza, allattamento, contraccezione, ecc.",
   "video": "www.youtube.com/embed/B5pd_7X4Pyg",
   "text": {"_def": "it", "it": "<p>(dal sito web della ASL RM B)</p>"}
}
}

"""
# perform the test sending the test_poi data above
import urllib2, json
from fairvillage.api import test_poi
data = json.dumps(test_poi)
url = "http://localhost:8000/add_poi/"
r = urllib2.urlopen(url, data) # use the optional arg data to specify the POST method
"""

