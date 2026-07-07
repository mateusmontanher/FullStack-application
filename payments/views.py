import json
import os
import time

import stripe
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from Api_Clothes.models import DataBaseClothes
from users.HistoryPayments import HistoryPayments

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@csrf_exempt
@require_http_methods(["POST"])
def CreateCheckoutSession(request):
    """Replaces setup_backend_csharp PaymentsController.CreateCheckoutSession."""
    try:
        data = json.loads(request.body)
        timestamp = str(int(time.time()))

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": data.get("Currency", "brl"),
                        "product_data": {
                            "name": data["name"],
                            "images": [data["ImageAdress"]],
                        },
                        "unit_amount": int(float(data["amount"]) * 100),
                    },
                    "quantity": int(data["quantity"]),
                },
            ],
            mode="payment",
            success_url="https://mm-vendedores.vercel.app/",
            cancel_url="https://mm-vendedores.vercel.app/?message=PagamentoCancelado",
            metadata={
                "user": str(data.get("User", "")),
                "product": str(data["name"]),
                "price": str(data["amount"]),
                "amount": str(data["quantity"]),
                "image_adress": str(data["ImageAdress"]),
                "data": timestamp,
                "option": str(data.get("Option", "")),
            },
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        print(f"There was an error with the Payment request. See the reason: {e}")
        return JsonResponse(
            {"err": "An error occurred while creating the Checkout page"}, status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def StripeWebhook(request):
    """Replaces setup_backend_csharp StripeWebhookController.

    Verifies the signature and, on checkout.session.completed, runs the
    process_payments logic in-process (no HTTP hop to another service).
    """
    endpoint_secret = os.getenv("WEBHOOK_KEY")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        print(f"Erro ao validar webhook: {e}")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata") or {}
        if not metadata:
            print("Sessão ou metadata ausente.")
            return HttpResponse(status=400)

        try:
            product = DataBaseClothes.objects.get(name=metadata["product"])
            user = User.objects.get(username=metadata["user"])

            HistoryPayments.objects.create(
                Product=product,
                Image=metadata.get("image_adress", ""),
                Value=float(metadata["price"]),
                Amount=int(metadata["amount"]),
                Username=user,
            )

            product.amount -= int(metadata["amount"])
            product.save()
            print("Pagamento processado com sucesso.")
        except Exception as e:
            print(f"Erro ao registrar o pagamento: {e}")
            return JsonResponse({"ERROR": str(e)}, status=400)

    return HttpResponse(status=200)
