from __future__ import unicode_literals

from menu import Menu, MenuItem
# from django.core.urlresolvers import reverse
# from django.urls import reverse
from django.utils.translation import ugettext as _, ugettext_lazy

def zones_children(request):
    children = []
    if not request.user_agent.is_bot:
        """
        children.append (MenuItem(
             _("My zone"),
             url='/la-mia-zona',
             weight=10,
             ))
        """
        children.append(MenuItem(_("Macrozones"),
            url='/macrozone',
            weight=10,
        ))
        children.append(MenuItem(_("Municipalities"),
            url='/municipi',
            weight=10,
        ))
        children.append(MenuItem(_("Provinces"),
            url='/province',
            weight=10,
         ))
        """
        children.append(MenuItem(_("Traditional city districts") + " (" + _("map") + ")",
             url='/topo',
             weight=10,
             ))
        
        children.append(MenuItem(_("Zipcode areas") + " (" + _("map") + ")",
             url='/cap',
             weight=80,
             ))
    children.append(MenuItem(_("Zone types") + " (" + _("list") + ")",
             url='/tipi-di-zona',
             weight=80,
             ))
   
    if request.user.is_authenticated():
        children.append(MenuItem("Muoversi a Roma",
                 url='/muoviroma',
                 weight=80,
                 ))
    """
    return children

def project_children(request):
    children = []
    children.append (MenuItem(
         _("About"),
         url='/fairvillage/about',
         weight=80,
        ))
    children.append (MenuItem(
         _("Our partners"),
         url='/fairvillage/partners',
         weight=80,
        ))
    children.append (MenuItem(
         _("Contacts"),
         url='/fairvillage/contacts',
         weight=80,
        ))
    return children

def resources_children(request):
    children = []
    """
    children.append (MenuItem(
         _("By theme area"),
         url='/risorse-utili-roma-lazio-aree-tematiche',
         weight=80,
        ))
    
    if request.user.is_authenticated():
        children.append (MenuItem(
             _("By category"),
             url='/risorse-utili-roma-lazio-categorie',
             weight=80,
       ))
    """
    children.append (MenuItem(
        _("By category"),
         url='/categorie',
         weight=80,
    ))
    children.append (MenuItem(
         _("By affiliation"),
         url='/reti-di-risorse',
         weight=80,
        ))
    """
    if request.user.is_authenticated():
        children.append (MenuItem(
             _("Da controllare"),
             url='/analisi-risorse',
             weight=80,
            ))
        children.append (MenuItem(
         _("Top contributors"),
             url='/poi-contributors',
             weight=80,
            ))
    """
    if False:
        children.append (MenuItem(
             _("Advanced search"),
             url='/cerca/',
             weight=80,
            ))
        children.append (MenuItem(
             _("How to search"),
             url='/help/search',
             weight=80,
            ))
        children.append (MenuItem(
             _("Suggest a resource"),
             url='/nuova-risorsa',
             weight=80,
            ))
    return children
"""
def community_children(request):
    children = []
    children.append (MenuItem(
         _("Ethnic and linguistic communities"),
         url='/community/cultures',
         weight=80,
        ))
    children.append (MenuItem(
         _("Social networks"),
         url='/community/networks',
         weight=80,
        ))
    children.append (MenuItem(
         _("Why register"),
         url='/community/why-register',
         weight=80,
        ))
    return children

def user_children(request):
    children = []
    if not request.user.is_authenticated():
        children.append (MenuItem(
             "Login",
             url='/accounts/login/',
             weight=80,
            ))
    if request.user.is_authenticated() and request.user.is_superuser:
        children.append (MenuItem(
             "Admin",
             reverse("admin:index"),
             weight=80,
             ))
    if request.user.is_authenticated():
        children.append (MenuItem(
             "Logout",
             url='/accounts/logout/',
             weight=80,
            ))
    return children

def user_menu_title(request):
    if request.user.is_authenticated():
        user = request.user
        fullname = '%s %s' % (user.first_name, user.last_name)
        if fullname.strip():
            return fullname
        else:
            return user.username
    else:
        return 'Utente'
"""

Menu.items = {}
Menu.sorted = {}

# Add a few items to our main menu
Menu.add_item("main", MenuItem(ugettext_lazy("The resources"),
                               url='/r',
                               weight=10,
                               children=resources_children,
                               separator=True))
Menu.add_item("main", MenuItem(ugettext_lazy("The zones"),
                               url='/z',
                               weight=20,
                               children=zones_children,
                               separator=True))
Menu.add_item("main", MenuItem(ugettext_lazy("The project"),
                               url='/p',
                               weight=30,
                               children=project_children,
                               separator=True))     

