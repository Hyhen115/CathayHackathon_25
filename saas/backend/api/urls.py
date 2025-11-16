from django.urls import path
from .views import recommend_product, fetch_image, detect_labels

urlpatterns = [
    path('recommend', recommend_product, name='recommend-product'),
    path('fetch-image', fetch_image, name='fetch-image'),
    path('detect-labels', detect_labels, name='detect-labels'),
]
