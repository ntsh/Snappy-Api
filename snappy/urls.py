from django.conf.urls import patterns, include, url

from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()
from django.conf.urls.static import static
#import jqmobile
#jqmobile.autodiscover()


urlpatterns = patterns('stream.views',
    url(r'^upload/$', 'upload'),
    url(r'^login/$', 'login'),
    url(r'^signup/$', 'signup'),
    url(r'^settings/$', 'user_settings'),
    url(r'^post/(?P<post_id>\d+)/json/$', 'post_json'),
    url(r'^post/(?P<post_id>\d+)/vote/$', 'vote'),
    url(r'^post/(?P<post_id>\d+)/comment/$', 'comment'),
    url(r'^post/(?P<post_id>\d+)/comments/(?P<page_id>\d+)/json/$', 'comments_json'),
    url(r'^new/(?P<page_id>\d+)/json/$', 'new_posts_json'),
    url(r'^popular/(?P<page_id>\d+)/json/$', 'new_posts_json',{'feed':'popular'}),
    url(r'^cat/(?P<cat>\w+)/new/(?P<page_id>\d+)/json/$', 'new_posts_json',{'feed':'cat_new'}),
    url(r'^cat/(?P<cat>\w+)/popular/(?P<page_id>\d+)/json/$', 'new_posts_json',{'feed':'cat_popular'}),
    url(r'^user/(?P<username>\w+)/posts/(?P<page_id>\d+)/json/$','new_posts_json',{'feed':'user_posts'}),
    url(r'^user/(?P<username>\w+)/upvotes/(?P<page_id>\d+)/json/$','new_posts_json',{'feed':'user_upvotes'}),
    url(r'^upload_test/$', 'upload_file'),    
)

urlpatterns += patterns('sitedocs.views',
    url(r'^tos/$','tos'),
    url(r'^privacy/$','privacy')
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'snappy.views.home', name='home'),
    # url(r'^snappy/', include('snappy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^ma/',    include(jqmobile.site.urls)),
    
)
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$','django.views.static.serve', {
            'document_root':settings.STATIC_ROOT,
        }),
   )
