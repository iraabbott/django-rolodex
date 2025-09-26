from django.urls import include, path, re_path
from rolodex import views
from rolodex.API import router, views as api_views


urlpatterns = [
    path('', views.home, name='rolodex_home'),
    re_path(r'^org/(.+)/$', views.search_org, name='rolodex_org'),
    re_path(r'^person/(.+)/$', views.search_person, name='rolodex_person'),

    # Entity maintenance
    re_path(r'^add-person/(.+)/$', views.new_person, name='rolodex_new_person'),
    re_path(r'^add-person/$', views.new_person_no_org, name='rolodex_new_person_no_org'),
    re_path(r'^edit-person/(.+)/$', views.edit_person, name='rolodex_edit_person'),
    re_path(r'^delete-person/(.+)/$', views.delete_person, name='rolodex_delete_person'),
    re_path(r'^add-org/$', views.new_org, name='rolodex_new_org'),
    re_path(r'^edit-org/(.+)/$', views.edit_org, name='rolodex_edit_org'),
    re_path(r'^delete-org/(.+)/$', views.delete_org, name='rolodex_delete_org'),

    # Doc adds
    re_path(r'^add-doc/org/(.+)/$', views.new_org_doc, name='rolodex_new_org_doc'),
    re_path(r'^add-doc/person/(.+)/$', views.new_person_doc, name='rolodex_new_person_doc'),
    re_path(r'^delete-doc/$', views.delete_doc, name='rolodex_delete_doc'),

    # Relationship maintenance
    re_path(r'^add-relationship/org/(.+)/$', views.new_org_relation, name='rolodex_new_org_relation'),
    re_path(r'^add-relationship/person/(.+)/$', views.new_person_relation, name='rolodex_new_person_relation'),
    re_path(r'^delete-relationship/$', views.delete_relationship, name='rolodex_delete_relation'),

    re_path(r'^add-tag/$', views.add_tag, name='rolodex_add_tag'),
    re_path(r'^remove-tag/$', views.remove_tag, name='rolodex_remove_tag'),
    re_path(r'^search-tag/(.+)/$', views.search_tag, name='rolodex_search_tag'),

    # network graphs
    re_path(r'^person-map/(.+)/$', views.person_map, name='rolodex_person_map'),
    re_path(r'^org-map/(.+)/$', views.org_map, name='rolodex_org_map'),
    re_path(r'^person-network/(.+)/$', views.person_network, name='rolodex_person_network'),
    re_path(r'^org-network/(.+)/$', views.org_network, name='rolodex_org_network'),
    re_path(r'^person-network-advanced/person/(.+)/$', views.adv_person_network, name='rolodex_adv_person_network'),
    re_path(r'^org-network-advanced/org/(.+)/$', views.adv_org_network, name='rolodex_adv_org_network'),

    # bloodhound/selectize remote search
    re_path(r'^entity-remote/', views.entity_remote_search, name='rolodex_entity_remote_search'),
    re_path(r'^org-remote/', views.org_remote_search, name='rolodex_org_remote_search'),
    re_path(r'^person-remote/', views.person_remote_search, name='rolodex_person_remote_search'),

    # api
    path('api/orgs/tree/<slug:slug>/', api_views.OrgHierarchyView.as_view(), name='rolodex_org_hierarchy'),
    path('api/', include(router.router.urls)),
    re_path(r'^api/employees/([0-9]+)/$', api_views.GetEmployees.as_view())
]

'''
    Work on more API calls to match model methods (though some model funcs
        are passed strings and others objects...)
'''
