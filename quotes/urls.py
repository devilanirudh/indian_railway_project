from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name="home"),
	path('pnr.html', views.home1, name="pnr"),
	path('train_info.html', views.Train_info, name="train_info"),
    path('live_train_status.html', views.live_train_status, name="live_train_status"),
    path('stations.html', views.get_stations, name="stations"),
]