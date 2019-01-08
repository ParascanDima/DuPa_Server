from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contact/', views.contact, name='contact'),
    url(r'^blog/', views.blog, name='blog'),
    url(r'^weather/(?P<city>Chisinau|Kiev)/', views.weather, name='weather'),
    url(r'^sendstart/(?P<function>watering|collectdata)/', views.SocketSend, name='SocketSend'),
    url(r'^sendstop/(?P<function>watering)/', views.SocketSend, name='SocketSend'),
    url(r'^plane/(?P<function>watering)/', views.PlaneAction, name='PlaneAction'),
    url(r'^windspeedchart/', views.windspeedchart, name='windspeedchart'),
    url(r'^planeTime/', views.PlanedTime, name="planeTime"),
    url(r'^chart/windspeedchart/', views.WindSpeedChartRender, name='WindSpeedChartRender'),
    url(r'^groundhumiditychart/', views.groundhumiditychart, name='groundhumiditychart'),
    url(r'^chart/groundhumiditychart/', views.GroundHumidityChartRender, name='GroundHumidityChartRender'),
    url(r'^datatransfer/', views.DataTransfer, name='DataTransfer'),
    url(r'^saveip/', views.SaveIP, name='SaveIP'),
    url(r'^getip/', views.ShowGSMIP, name='GetIP'),
]
