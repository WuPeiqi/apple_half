
from django.conf.urls import url,include
from django.contrib import admin
from blog import views

from django.views.static import serve
from django.conf import settings



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^$', views.index),
    url(r'^blog/', include('blog.urls')),
    url(r'^u/', include('blog.urls')),
    url(r'^login/', views.log_in),
    url(r'^valid_code/', views.valid_code),
    url(r'^reg/', views.reg),
    url(r'^log_out/', views.log_out),
    url(r'^postlist/', views.postlist),
    url(r'^addArticle/', views.addArticle),
    url(r'^upload_file/', views.upload_file),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

]