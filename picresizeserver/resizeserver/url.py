from django.urls import path
from .views import ResizeImageView,ImageBackgroundRemoveView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('resizeimage', ResizeImageView.as_view(), name='resizeimage'),
    path('removebackground', ImageBackgroundRemoveView.as_view(), name='removebackground'),
]

