from django.urls import path

from . import views

urlpatterns = [
    path("create-checkout-session/", views.CreateCheckoutSession, name="create_checkout_session"),
    path("webhook/", views.StripeWebhook, name="stripe_webhook"),
]
