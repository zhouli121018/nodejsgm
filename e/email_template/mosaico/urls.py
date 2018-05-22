from django.conf.urls import url

from .views import index, editor, upload, download, image, template

from django.conf import settings
from django.conf.urls.static import static

app_name = 'mosaico'
urlpatterns = [
                  url(r'^$', index, name="index"),
                  url(r'^editor.html$', editor, name="editor"),
                  url(r'^img/$', image),
                  url(r'^upload/$', upload),
                  url(r'^dl/$', download),
                  url(r'^template/$', template),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
