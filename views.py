# -*- coding: utf-8 -*-
import json

from django.conf import settings
# from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404  #render_to_response, 
from django.template import RequestContext
from django.contrib.flatpages.models import FlatPage
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django_user_agents.utils import get_user_agent

# from api import poitypes as categories
from roma.session import get_focus, set_focus, focus_set_category, focus_add_themes
from pois.models import Zonetype, Zone, Odonym, Poitype, Poi

from pois.models import list_all_zones
from pois.models import make_zone_subquery
from pois.models import MACROZONE,TOPOZONE,MUNICIPIO,CAPZONE
from pois.forms import PoiBythemeForm
from pois.models import POI_CLASSES
from pois.models import resources_by_topo_count
from pois.models import zone_prefix_dict

from roma.settings import LANGUAGE_CODE
from roma.settings import MAX_POIS
from fairvillage.settings import POITYPE_SLUGS
CATEGORIES = Poitype.objects.filter(slug__in=POITYPE_SLUGS)

from pois.views import resources_by_category_and_zone, viewport_get_pois

# from django.core.cache import get_cache
from django.core.cache import caches
from django.db.models import Q

def zone_index_map(request, zonetype_id=1, prefix='', render_view=True):
    zonetype = get_object_or_404(Zonetype, pk=zonetype_id)
    zonetype_label = ''
    region = 'LAZIO'
    user_agent = get_user_agent(request)
    view_map = user_agent.is_pc or user_agent.is_tablet
    if zonetype_id or zonetype_id==0:
        if zonetype_id==0 and prefix:
            zone_list = Zone.objects.filter(zonetype=zonetype_id, code__istartswith=prefix).exclude(geom__isnull=True).order_by('name')
            zonetype_label = prefix=='RM.' and _('macrozones') or prefix=='PR.' and _('provinces')
            region = prefix=='RM.' and 'ROMA' or prefix=='PR.' and 'LAZIO'
        elif zonetype_id==3 and prefix:
            zone_list = Zone.objects.filter(zonetype=zonetype_id, code__istartswith=prefix).exclude(geom__isnull=True).order_by('name')
            zonetype_label = prefix=='R.' and _('historical quarters') or prefix=='Q.' and _('quarters') or prefix=='S.' and _('quarter extensions') or prefix=='Z.' and _('suburban zones')
            region = 'ROMA'
        elif zonetype_id==7 and prefix:
            zone_list = Zone.objects.filter(zonetype=zonetype_id, code__istartswith=prefix).exclude(geom__isnull=True)
            zonetype_label = prefix=='M.' and _('municipalities') or prefix=='COM.' and _('towns')
            region = prefix=='M.' and 'ROMA' or prefix=='COM.' and 'LAZIO'
        else:
            zone_list = Zone.objects.filter(zonetype=zonetype_id).exclude(geom__isnull=True)
            if zonetype_id==0:
                zone_list = zone_list.exclude(code='ROMA')
                zonetype_label = _('macrozones')
                region = 'ROMA / LAZIO'
            elif zonetype_id==6:
                zonetype_label = _("zipcode areas")
                region = 'ROMA / LAZIO'
            elif zonetype_id==3:
                zonetype_label = _("traditional city districts")
                region = 'ROMA'
            else:
                zonetype_label = Zonetype.objects.get(pk=zonetype_id).name
    else:
        zone_list = Zone.objects.all()
    zcount = zone_list.count()
    zone_list = [zone.make_dict() for zone in zone_list]
    data_dict = {'view_map': view_map, 'zonetype': zonetype, 'zone_list' : zone_list, 'zone_count' : zcount, 'zonetype_label': zonetype_label, 'region': region, 'prefix': prefix}

    if render_view:
       return render(request, 'pois/fv_zone_index_map.html', data_dict)
    else:
        return data_dict

def home_data(request):
    zone_dict = zone_index_map(request, zonetype_id=0, render_view=False)
    language = translation.get_language() or 'en'
    data_dict = {}
    # summary = FlatPage.objects.get(url='/fairvillage/project/').content
    summary = ""
    data_dict['summary'] = summary
    """
    news = FlatPage.objects.get(url='/project/news/').content
    data_dict['news'] = news
    by_theme_list = []
    themes = Tag.objects.all()
    for theme in themes:
        n = resources_by_theme_count(theme)
        if n:
            # by_theme_list.append([theme, n])
            by_theme_list.append([theme.name, theme.slug, n])
    data_dict['by_theme_list'] = by_theme_list
    """
    by_zone_list = []
    for zone_prefix in ['M']:
        topotype_name_plural = zone_prefix_dict[zone_prefix][2]
        # zones = Zone.objects.filter(zonetype_id=3, code__istartswith=zone_prefix).order_by('name')
        zones = Zone.objects.filter(zonetype_id=7, code__istartswith=zone_prefix).order_by('name')
        topotype_sublist = []
        for zone in zones:
            n = resources_by_topo_count(zone)
            if n:
                topotype_sublist.append([zone.name, zone.slug, n])
        # by_zone_list.append([topotype_name_plural, topotype_sublist])
        by_zone_list.append(['Roma - Comune', topotype_sublist])
    by_prov_list = []
    province = Zone.objects.filter(code__istartswith='PR').order_by('code')
    for prov in province:
        prov.sublist = []
        zones = Zone.objects.filter(code__istartswith='COM'+prov.code[2:]).order_by('name')
        for zone in zones:
            n = resources_by_topo_count(zone)
            if n:
                prov.sublist.append([zone.name, zone.slug, n])
        if prov.sublist:
            if prov.code == 'PR.58':
                by_prov_list.insert(0,[prov.name, prov.sublist])
            else:
                by_prov_list.append([prov.name, prov.sublist])
    data_dict['by_zone_list'] = by_zone_list
    data_dict['by_prov_list'] = by_prov_list
    site_url = request.META["HTTP_HOST"]
    """
    d = feedparser.parse('http://%s/feed' % site_url)
    feed = d.entries and d or []
    data_dict['feed'] = feed
    """
    data_dict.update(zone_dict)
    return data_dict

def home(request):
    data_dict = home_data(request)
    by_category_list = []
    for category in CATEGORIES:
        poitype = Poitype.objects.filter(klass=category.klass)[0]
        resources = Poi.objects.filter(poitype_id=category.klass, state=1).order_by('name')
        n = resources.count()
        if n:
            by_category_list.append([category.name, category.slug, poitype.icon, n])
    data_dict['by_category_list'] = by_category_list
    # return render_to_response('fairvillage/home.html', data_dict, context_instance=RequestContext(request))
    return render(request,'fairvillage/home.html', data_dict)
    
def zone_category_index(request, zone_id, zone=None):
    if not zone:
        zone = get_object_or_404(Zone, pk=zone_id)
    """
    language = RequestContext(request).get('LANGUAGE_CODE', 'en')
    zones_cache = get_cache('zones')
    key = 'zone%04d' % zone_id
    if not language.startswith('it') or request.GET.get('nocache', None):
        category_poitype_list = None
        print '%s invalid' % key
    else:
        category_poitype_list = zones_cache.get(key, None)
        print '%s valid' % key
    """
    region = zone.zone_parent()
    category_poitype_list = None
    if not category_poitype_list:
        category_poitype_list = []
        for category in CATEGORIES:
           q = make_zone_subquery(zone)
           poitype = Poitype.objects.filter(klass=category.klass)[0]
           if poitype.active:
             pois = Poi.objects.filter(q & Q(poitype_id=category.klass, state=1)).order_by('name')
           else:
             klasses = poitype.sub_types(return_klasses=True)
             pois = Poi.objects.filter(q & Q(poitype_id__in=klasses, state=1)).order_by('name')
           n_pois = pois.count()
           if n_pois:
              if n_pois == 1:
                category_poitype_list.append([category.name, poitype.icon, poitype.slug, n_pois, pois[0].name, pois[0].friendly_url()])
              else:
                category_poitype_list.append([category.name, poitype.icon_name(),  poitype.slug, n_pois, '', ''])
        #category_poitype_list=sorted(category_poitype_list,  key=str.lower)
        category_poitype_list = sorted(category_poitype_list, key=lambda x: x[0].lower())
        """
        if language.startswith('it'):
            try:
                zones_cache.set(key, category_poitype_list)
            except:
                print category_poitype_list
    cache = get_cache('custom')
    key = 'allzones_' + language

    if request.GET.get('nocache', None):
        all_zones = None
        print 'allzones invalid'
    else:
        all_zones = cache.get(key, None)
        print 'allzones valid'
    """
    all_zones = None
    if not all_zones:
        all_zones = list_all_zones()
        # cache.set(key, all_zones)
    can_edit = zone.can_edit(request)
    # return render_to_response('pois/zone_category_index.html', {'zone': zone, 'zonetype_list': all_zones, 'category_poitype_list': category_poitype_list, 'can_edit': can_edit,}, context_instance=RequestContext(request))
    return render(request,'pois/fv_zone_category_index.html', {'zone': zone, 'region': region, 'zonetype_list': all_zones, 'category_poitype_list': category_poitype_list, 'can_edit': can_edit,})

def zone_category_index_by_slug(request, zone_slug):
    zone = get_object_or_404(Zone, slug=zone_slug)
    return zone_category_index(request, zone.id, zone=zone)

def category_index(request):
    by_category_list = []
    for category in CATEGORIES:
        poitype = Poitype.objects.filter(klass=category.klass)[0]
        resources = Poi.objects.filter(poitype_id=category.klass, state=1).order_by('name')
        n = resources.count()
        if n:
            by_category_list.append([category.name, category.slug, poitype.icon, n])
    # return render_to_response('pois/category_index.html', {'by_category_list': by_category_list,}, context_instance=RequestContext(request))
    return render(request,'pois/fv_category_index.html', {'by_category_list': by_category_list,})

def poi_detail(request, poi_id, poi=None):
    if not poi:
        poi = get_object_or_404(Poi, pk=poi_id)
        return HttpResponseRedirect('/risorsa/%s/' % poi.slug)
    language = translation.get_language() or 'en'
    can_edit = poi.can_edit(request)
    focus_set_category(request, poi.poitype_id)
    """
    focus_add_themes(request, poi.get_themes_indirect(return_ids=True))
    focus_add_themes(request, poi.get_themes(return_ids=True))
    """
    # MMR pois_cache = get_cache('pois')
    pois_cache = caches['pois']
    key = 'poi%05d' % poi_id
    if not language.startswith('it') or request.GET.get('nocache', None):
        data_dict = None
    else:
        data_dict = pois_cache.get(key, None)
    if not data_dict:
        print ('invalid cache for ', key)
        poi_dict = poi.make_dict() # 140603
        """
        zone_list = Zone.objects.filter(pois=poi_id, zonetype__id__in=[0,7,1,3]).order_by('-zonetype__id', 'id')
        zone_list = [{ 'name': zone.name_with_code(), 'url': zone.friendly_url()} for zone in zone_list]
        """
        zones = Zone.objects.filter(pois=poi_id, zonetype__id__in=[7]).order_by('zonetype__id')
        zone_list = []
        macrozone = None
        for zone in zones:
            """
            if zone.zonetype_id == 3: # zona toponomastica
                zone_list.append({ 'name': '%s %s' % (zone.code, zone.name), 'url': '/zona/%s/' % zone.slug, 'slug': zone.slug})
            else: # municipio
            """
            zone_list.append({ 'name': zone.name, 'url': '/zona/%s/' % zone.slug, 'slug': zone.slug})
            macrozone = zone.get_macrozone_slug()
        hosted_list = Poi.objects.filter(host=poi).order_by('name')
        hosted_list = [{ 'name': p.name, 'url': p.friendly_url()} for p in hosted_list]
        poi_list = Poi.objects.filter(pois=poi).order_by('name')
        poi_list = [{ 'name': p.name, 'url': p.friendly_url()} for p in poi_list]
        n_caredby = Poi.objects.filter(careof=poi).count()
        poitype = poi.poitype
        if poitype:
            """
            poitype = { 'name': poitype.name, 'url': poitype.friendly_url()}
            """
            if macrozone:
                poitype = { 'name': poitype.name, 'url': '/categoria/%s/zona/%s/' % (poitype.slug, macrozone)}
            else:
                poitype = { 'name': poitype.name, 'url': poitype.friendly_url()}
        """
        theme_names = poi.get_all_themes(return_names=True)
        """
        theme_names = []
        theme_list = [{ 'id': theme.id, 'name': theme.name, 'slug': theme.slug } for theme in poi.get_all_themes()]
        # return render_to_response('pois/poi_detail.html', {'poi': poi, 'poitype_name': poitype_name, 'theme_names': theme_names, 'hosted_list': hosted_list, 'zone_list': zone_list, 'poi_list': poi_list, 'n_caredby': n_caredby, 'can_edit': can_edit,}, context_instance=RequestContext(request))
        data_dict = {'poi_dict': poi_dict, 'poitype': poitype, 'theme_list': theme_list, 'theme_names': theme_names, 'hosted_list': hosted_list, 'zone_list': zone_list, 'poi_list': poi_list, 'n_caredby': n_caredby,}
        if macrozone:
            data_dict['macrozone'] = macrozone
        if language.startswith('it'):
            pois_cache.set(key, data_dict)
    feeds = []
    for f in poi.get_feeds():
        entries = []
        for e in f.entries:
            # entry = { 'title': e.title, 'link': e.link }
            try: entry = { 'title': e.title, 'link': e.link }
            except: continue
            try: entry['summary'] = e.summary
            except: pass
            try: entry['content'] = e.content[0].value
            except: pass
            try: entry['date'] = e.date
            except:
                try: entry['date'] = e.published
                except: pass
            entries.append(entry)
        feeds.append({ 'title': f.feed.title, 'entries': entries })
    data_dict['can_edit'] = can_edit
    data_dict['feeds'] = feeds
    # return render_to_response('pois/fv_poi_detail.html', data_dict, context_instance=RequestContext(request))
    return render(request,'pois/fv_poi_detail.html', data_dict)

def poi_detail_by_slug(request, poi_slug):
    """
    poi = None
    try:
        poi = Poi.objects.select_related().get(slug=poi_slug, state=1)
        poi_id = poi.id
    except:
        pass
    """
    poi = get_object_or_404(Poi, slug=poi_slug)
    if poi.state == 1 or poi.can_edit(request):
        poi_id = poi.id
    else:
        poi = None
        poi_id = -1
    return poi_detail(request, poi_id, poi)

def poitype_detail(request, klass, poitype=None):
    list_all = request.GET.get('all', '')
    zone_list = [];  poi_dict_list = []
    max_count = 0; min_count = 10000
    if not poitype:
        poitype = get_object_or_404(Poitype, klass=klass)
    zone = get_object_or_404(Zone, code='ROMA')
    theme = request.GET.get('theme', '')
    if theme and not theme in poitype.tags.all():
        theme_id = int(theme)
        theme_list = [get_object_or_404(Tag, pk=theme_id)]
    else:
        theme_id = None
        theme_list = poitype.tags.all()
    region = 'ROMA'
    language = translation.get_language() or 'en'
    categories_cache = caches['categories']
    key = 'cat_%s' % klass
    if not language.startswith('it') or request.GET.get('nocache', None) or theme:
        data_dict = None
    else:
        data_dict = categories_cache.get(key, None)
        if data_dict:
            print ('%s valid' % key)
        else:
            print ('%s invalid' % key)
    if not data_dict:
        help_text = FlatPage.objects.get(url='/help/category/').content
        # if theme and not theme in poitype.tags.all():
        if theme_id:
            poi_list = resources_by_tags_and_type([theme_id], poitype.klass)
        else:
            if poitype.active:
                poi_list = Poi.objects.select_related().filter(poitype=poitype.klass, state=1).order_by('name')
            else:
                klasses = poitype.sub_types(return_klasses=True)
                poi_list = Poi.objects.filter(poitype_id__in=klasses, state=1).order_by('name')
            # theme_list = poitype.tags.all()
            if poi_list.count() > MAX_POIS and not list_all:
                zones = Zone.objects.filter(zonetype_id=0).exclude(code='ROMA')
                zone_list = zone_list_no_sorted = []
                for zone in zones:
                    pois = resources_by_category_and_zone(klass, zone)
                    if pois:
                        n = pois.count()
                        max_count = max(n, max_count); min_count = min(n, min_count)
                        zone_dict = zone.make_dict()
                        zone_dict['url'] = '/categoria/%s/zona/%s/' % (poitype.slug, zone.slug)
                        zone_dict['count'] = n
                        zone_list_no_sorted.append(zone_dict)
                        zone_list = sorted(zone_list_no_sorted, key=lambda k: k['name'].lower())
                if zone_list:
                    for item in zone_list:
                        if 'provincia' in item['name'].lower():
                            region = 'LAZIO'
                            break
                zone = None
                help_text = FlatPage.objects.get(url='/help/big-list/').content
        if not zone_list:
            poi_dict_list_no_sorted = [poi.make_dict(list_item=True) for poi in poi_list]
            poi_dict_list = sorted(poi_dict_list_no_sorted, key=lambda k: k['name'].lower())
            for item in poi_dict_list:
                if item['comune'][1] != 'roma':
                    region = 'LAZIO'
                    break
        
        """
        set_focus(request, tags=[theme.id for theme in theme_list])
        focus_set_category(request, klass)
        """
        sub_types = not poitype.active and [{ 'name': p.name, 'slug': p.slug } for p in poitype.sub_types()] or []
        poitype = { 'name': poitype.name,  'slug': poitype.slug, 'active': poitype.active }
        if sub_types:
            poitype['sub_types'] = sub_types
        data_dict = {'help': help_text, 'poitype': poitype, 'theme_list': theme_list, 'poi_dict_list': poi_dict_list, 'region': region, 'zone_list': zone_list, 'min': min_count, 'max': max_count}
        data_dict['zone'] = zone
        if language.startswith('it') and not theme:
            try:
                categories_cache.set(key, data_dict)
            except:
                pass
    return render(request, 'pois/fv_poitype_detail.html', data_dict)

def poitype_detail_by_slug(request, klass_slug):
    poitype = get_object_or_404(Poitype, slug=klass_slug)
    return poitype_detail(request, poitype.klass, poitype)

def poitype_zone_detail(request, klass, zone_id, poitype=None, zone=None):
    if not poitype:
        poitype = get_object_or_404(Poitype, klass=klass)
    if not zone:
        zone = get_object_or_404(Zone, pk=zone_id)
    language = translation.get_language() or 'en'
    catzones_cache = caches['catzones']
    key = 'cat_%s_zone%04d' % (klass, zone_id)
    # region = 'ROMA'
    if not language.startswith('it') or request.GET.get('nocache', None):
        data_dict = None
    else:
        data_dict = catzones_cache.get(key, None)
    if data_dict:
        print ('%s valid' % key)
    else:
        print ('%s invalid' % key)
        poi_list = resources_by_category_and_zone(klass, zone, select_related=True)
        zone_list = zone_list_no_sorted = []
        if zone.zonetype_id == 0:
            zones = Zone.objects.filter(zonetype_id=0).exclude(code='ROMA')
            for z in zones:
                if z.id != zone.id:
                    pois = resources_by_category_and_zone(klass, z)
                    if pois:
                        n = pois.count()
                        """
                        z.count = n
                        z.url = '/categoria/%s/zona/%s/' % (poitype.slug, z.slug)
                        """
                        url = '/categoria/%s/zona/%s/' % (poitype.slug, z.slug)
                        z = z.make_dict()
                        z['count'] = n
                        z['url'] = url
                        zone_list_no_sorted.append(z)
                        zone_list = sorted(zone_list_no_sorted, key=lambda k: k['name'].lower())
        theme_list = [ t.make_dict() for t in poitype.tags.all()]
        sub_types = not poitype.active and [{ 'name': p.name, 'slug': p.slug } for p in poitype.sub_types()] or []
        poitype = { 'name': poitype.name,  'slug': poitype.slug, 'active': poitype.active }
        if sub_types:
            poitype['sub_types'] = sub_types
        help_text = FlatPage.objects.get(url='/help/category/').content
        poi_dict_list_no_sorted = [poi.make_dict(list_item=True) for poi in poi_list]
        poi_dict_list = sorted(poi_dict_list_no_sorted, key=lambda k: k['name'].lower())
        """
        if zone_list and poi_dict_list:
            for item in zone_list:
                if 'provincia' in item['name'].lower():
                    region = 'LAZIO' 
                    break
        elif poi_dict_list:
            for item in poi_dict_list:
                if item['comune'][1] != 'roma':
                    region = 'LAZIO' 
                    break
        else:
        """
        region = zone.zone_parent()
        data_dict = {'help': help_text, 'poitype': poitype, 'theme_list': theme_list, 'poi_dict_list': poi_dict_list, 'zone_list': zone_list, 'region': region}

        if language.startswith('it'):
            try:
                catzones_cache.set(key, data_dict)
            except:
                print (data_dict)
    data_dict['zone'] = zone
    return render(request, 'pois/fv_poitype_detail.html', data_dict)

def poitype_zone_detail_by_slugs(request, klass_slug, zone_slug):
    poitype = get_object_or_404(Poitype, slug=klass_slug)
    zone = get_object_or_404(Zone, slug=zone_slug)
    return poitype_zone_detail(request, poitype.klass, zone.id, poitype=poitype, zone=zone)

def street_detail(request, street_id, street=None):
    if not street:
        street = get_object_or_404(Odonym, pk=street_id)
        return HttpResponseRedirect('/toponimo/%s/' % street.slug)
    language = translation.get_language() or 'en'
    streets_cache = caches['streets']
    key = 'street_%05d' % street_id
    if not language.startswith('it') or request.GET.get('nocache', None):
        data_dict = None
    else:
        data_dict = streets_cache.get(key, None)
    if data_dict:
        print ('%s valid' % key)
    else:
        print ('%s invalid' % key)
        help_text = FlatPage.objects.get(url='/help/street/').content
        zones = street.get_zones()
        zone_list = [zone.make_dict(list_item=True) for zone in zones[0]]
        zone_zipcode_list = [zone.make_dict(list_item=True) for zone in zones[1]]
        pois = Poi.objects.select_related().filter(street=street, state=1)
        if POI_CLASSES:
            pois = pois.filter(poitype_id__in=POI_CLASSES)
        pois = pois.order_by('name')
        poi_dict_list_no_sorted = [poi.make_dict(list_item=True) for poi in pois]
        poi_dict_list = sorted(poi_dict_list_no_sorted, key=lambda k: k['name'].lower())
        region = 'ROMA'
        if poi_dict_list:
            for item in poi_dict_list:
                if item['comune'][1] != 'roma':
                    region = 'LAZIO' 
                    break
        data_dict = {'help': help_text, 'street_name': street.name, 'street_id': street.id, 'zone_list': zone_list, 'zone_zipcode_list': zone_zipcode_list, 'poi_dict_list': poi_dict_list, 'view_type': 'street', 'region': region}
        if language.startswith('it'):
            try:
                streets_cache.set(key, data_dict)
            except:
                print ('cache non recuperata')
    can_edit = street.can_edit(request)
    data_dict['can_edit'] = can_edit
    return render(request,'pois/fv_street_detail.html', data_dict)

def street_detail_by_slug(request, street_slug):
    street = get_object_or_404(Odonym, slug=street_slug)
    return street_detail(request, street.id, street)

def zone_detail(request, zone_id, zone=None):
    if not zone:
        zone = get_object_or_404(Zone, pk=zone_id)
        return HttpResponseRedirect('/zona/%s/' % zone.slug)
    language = translation.get_language() or 'en'
    zonemaps_cache = caches['zonemaps']
    key = 'zone%04d' % zone_id
    if not language.startswith('it') or request.GET.get('nocache', None):
        data_dict = None
    else:
        data_dict = zonemaps_cache.get(key, None)
        # print (data_dict)       
    if data_dict:
        print ('%s valid' % key)
    else:
        print ('%s invalid' % key)
        help_text = FlatPage.objects.get(url='/help/zone/').content.replace('</p>', '')
        macrozones = []
        subzone_list = []
        zone_dict = zone.make_dict()
        zone_dict['prefix'] = zone.zone_parent()
        zone_dict['type_subzones'] = [z.make_dict(list_item=True) for z in zone.type_subzones()]
        zone_dict['sametype_zones'] = [z.make_dict(list_item=True) for z in zone.sametype_zones()]
        # MMR zone_dict['neighbouring'] = [z.make_dict(list_item=True) for z in zone.neighbouring()]
        zone_dict['neighbouring'] = zone.neighbouring()
        zone_dict['overlapping'] = [z.make_dict(list_item=True) for z in zone.overlapping()]
        if zone.zonetype_id == MACROZONE:
            subzone_list = zone.list_subzones(zonetype_id=TOPOZONE)
        elif zone.zonetype_id in [TOPOZONE, MUNICIPIO]:
            macrozones = Zone.objects.filter(zonetype_id=MACROZONE, zones=zone)
            macrozones = [z.make_dict for z in macrozones]
        # pois = Poi.objects.select_related().filter(zones=zone, state=1).order_by('name')
        # VEDI def make_zone_subquery(zone): in models.py
        if zone.zonetype_id == CAPZONE:
            pois = Poi.objects.select_related().filter(zipcode=zone.code, state=1) # .order_by('name')
        elif zone.zonetype_id == MACROZONE:
            subzones = zone.zones.filter(zonetype_id=MUNICIPIO)
            zone_ids = [subzone.id for subzone in subzones]
            pois = Poi.objects.select_related().filter(zones__in=zone_ids, state=1) # .order_by('name')
        else:
            pois = Poi.objects.select_related().filter(zones=zone, state=1) # .order_by('name')
        if POI_CLASSES:
            pois = pois.filter(poitype_id__in=POI_CLASSES)
        pois = pois.order_by('name')
        # form = PoiBythemeForm(initial={'tags': []})
        poi_dict_list_no_sorted = [poi.make_dict(list_item=True) for poi in pois]
        poi_dict_list = sorted(poi_dict_list_no_sorted, key=lambda k: k['name'].lower())
        data_dict = {'help': help_text, 'zone': zone_dict, 'macrozones': macrozones, 'subzone_list': subzone_list, 'poi_dict_list': poi_dict_list}
        if language.startswith('it'):
            try:
                zonemaps_cache.set(key, data_dict)
            except:
                pass
    can_edit = zone.can_edit(request)
    data_dict['can_edit'] = can_edit
    # eturn render_to_response('pois/fv_zone_detail.html', data_dict, context_instance=RequestContext(request))
    return render(request,'pois/fv_zone_detail.html', data_dict)

def zone_detail_by_slug(request, zone_slug):
    zone = get_object_or_404(Zone, slug=zone_slug)
    return zone_detail(request, zone.id, zone)

def viewport(request):
    help_text = FlatPage.objects.get(url='/help/viewport/').content
    focus = get_focus(request)
    tags = focus.get('tags', [])
    viewport = focus.get('viewport', None)
    if not viewport:
        try:
            w = float(request.REQUEST['left'])
            s = float(request.REQUEST['bottom'])
            e = float(request.REQUEST['right'])
            n = float(request.REQUEST['top'])
        except:
            # return render_to_response("roma/slim.html", {'text': '',}, context_instance=RequestContext(request))
            return render(request,"roma/slim.html", {'text': '',})
        viewport = [w, s, e, n]
    pois = viewport_get_pois(request, viewport, tags=tags)
    # poi_dict_list = [poi.make_dict(list_item=True) for poi in pois]
    if POI_CLASSES:
       pois = pois.filter(poitype_id__in=POI_CLASSES)
    pois = pois.order_by('name')
    # poi_dict_list = [poi.make_dict(list_item=True) for poi in pois]
    poi_dict_list_no_sorted = [poi.make_dict(list_item=True) for poi in pois]
    poi_dict_list = sorted(poi_dict_list_no_sorted, key=lambda k: k['name'].lower())
    region = 'ROMA'
    if poi_dict_list:
        for item in poi_dict_list:
            if item['comune'][1] != 'roma':
                region = 'LAZIO'
                break
    # form = PoiBythemeForm(tags=tags)
    form = PoiBythemeForm(initial={'tags': tags})
    # return render_to_response('pois/fv_street_detail.html', {'help': help_text, 'poi_dict_list': poi_dict_list, 'view_type': 'viewport', 'form': form, 'tags': tags,}, context_instance=RequestContext(request))
    return render(request,'pois/fv_street_detail.html', {'help': help_text, 'poi_dict_list': poi_dict_list, 'view_type': 'viewport', 'form': form, 'tags': tags, 'region': region})

from django.db.models import Count
def resource_networks(request):
    pois = Poi.objects.filter(state=1).exclude(poi__pois=None)
    if POI_CLASSES:
        pois = pois.filter(poitype_id__in=POI_CLASSES)
    pois = pois.annotate(num_pois=Count('poipoi')).order_by('-num_pois')
    poi_dict_list = []
    for poi in pois:
        poi_dict = poi.make_dict(list_item=True)
        if poi.num_pois > 3:
            poi_dict['num_pois'] = poi.num_pois
            poi_dict_list.append(poi_dict)
    return render(request, 'pois/fv_poi_list.html', {'list_type': 'networks', 'poi_dict_list': poi_dict_list, 'count': len(poi_dict_list)})
