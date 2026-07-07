from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetDoneView, PasswordResetView, PasswordChangeView
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from allauth.socialaccount.models import SocialAccount
from django.db import models
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from requests import get
from Api_Clothes.models import DataBaseClothes
from Api_Clothes.serializers import SerializersClothes
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from xml.etree import ElementTree
import requests
import json

from .forms import LoginUsers, RegisterUsers, ConfirmEmail, ResetPasswordDone
from users.forget_email import RetriveAccount, SendEmailAfterRegister
from users.HistoryPayments import HistoryPayments

def Verifications(request):
    photo_url = ''
    status_user = False
    is_superuser = False

    cards = DataBaseClothes.objects.all()


    if request.user.is_authenticated:
        if request.user.is_superuser:
            is_superuser=True
            print("A verificação foi bem-sucedida, você é um administrador!")

        try:
            # Devemos manter a lógica assim pois, e se o usuário não tiver imagem?, ele vai cair na mesma página de quem não está logado?
            # Ou, e se o usuário acabou de deletar sua conta?, ele deve ser redirecionado para a mesma página padrão?
            social_account = SocialAccount.objects.filter(user=request.user, provider="google").first()
            if social_account:
                photo_url = social_account.extra_data.get("picture", "")
                status_user = True
                # Isso deve permanecer assim (status_user como True fora da condicional), pois nem todos os usuários usarão o allauth.
            status_user = True
        except Exception as e:
            print(f"Houve um erro inesperado, o erro é: {e}")

        status_user = True
    return {"each_user_image": photo_url, "StatusUser": status_user, "IsSuperUser":is_superuser, "cards": cards}


class LoginValidate(serializers.Serializer):
    user = serializers.CharField()
    password = serializers.CharField()

@csrf_exempt
@require_http_methods(['POST'])
@api_view(['POST'])
@ensure_csrf_cookie
def ProcessLogin(request):

    if request.method == 'POST':

        serializer = LoginValidate(data=request.data)

        if not serializer.is_valid():
            return Response({"ERROR": "O conteúdo submetido não é válido."}, status=403)

        get_user = serializer.validated_data.get("user")
        get_password = serializer.validated_data.get("password")

        if not User.objects.filter(username=get_user).exists():
            return Response({"ERROR": "Usuário não foi encontrado"}, status=404)

        user = auth.authenticate(
            request,
            username = get_user,
            password = get_password,
        )
        CSRF = get_token(request)
        print("Valor do csrf token: ",CSRF)
        if user is not None:
            print("O usuário não é Null")
            auth.login(request, user)
            tokens = RefreshToken.for_user(user)
            return JsonResponse(
                {"Success": "Seja bem vindo!",
                 "X-CSRFToken": CSRF,
                 "access": str(tokens.access_token),
                 "refresh": str(tokens),
                }, status=200)
        return JsonResponse({"ERROR": "As credenciais não conferem"}, status=401)
# TODO: Refatorar
def formLogin(request):

    if request.method == "POST":
        serializer = LoginValidate(data=request.data)

        if not serializer.is_valid():
            # I've written this message in portuguese because it'll be show on the FrontEnd.
            return Response({"ERRO":'Os dados submetidos não são validos'})

        username_form_login = serializer.validated.data.get("user")
        password_form_login = serializer.validated.data.get("password")

        user = auth.authenticate(
            request,
            username=username_form_login,
            password=password_form_login,
        )

        if user is not None:
            auth.login(request, user)
            return Response({"Success":f"Senha bem vindo: {username_form_login}"})
        else:
            return Response({"NotFound":"Usuário não encontrado no nosso sistema."})

    return render(request, "Forms/Login.html")


class RegisterValidate(serializers.Serializer):
    email = serializers.EmailField()
    user = serializers.CharField()
    password = serializers.CharField()
    secondPassword = serializers.CharField()

@csrf_exempt
@require_http_methods(['POST'])
@api_view(['POST'])
def ProcessRegister(request):
    serializer = RegisterValidate(data=request.data)
    if request.method == 'POST':
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user = serializer.validated_data.get("user")
            password = serializer.validated_data.get("password")
            secondPassword = serializer.validated_data.get("secondPassword")

            print(f"Os dados que Chegaram ao Djago foram: {email, user, password, secondPassword}")

            if User.objects.filter(username=user).exists() or User.objects.filter(email=email):
                return Response({"ERROR": "Já existe um usuário com essas credenciais"}, status=302)
            else:
                if password != secondPassword:
                    return Response({"ERROR": "As senhas são diferentes"}, status=400)
                else:
                    if len(password) < 8:
                        return Response({"ERROR": "As senhas devem conter ao menos 8 dígitos"}, status=400)
                    else:
                        user = User.objects.create_user(
                            email = email,
                            username = user,
                            password = password,
                        )
                        user.save()
                        try:
                            SendEmailAfterRegister.submit_email(user, "http://localhost:3000/")
                            print(f"Email enviado!, veja a caixa de entrada")
                        except Exception as err:
                            print(f"Houve um erro, veja: {err}")
                        return Response({"Success": "Usuário cadastrado com sucesso"}, status=201)
        else:
            return Response({"ERROR": "O conteúdo submetido não é valido."}, status=400)

def formRegister(request):

    register_forms = RegisterUsers()

    if request.method == "POST":
        register_forms = RegisterUsers(request.POST)

        if register_forms.is_valid():
            if register_forms.cleaned_data['password_register_form'] != register_forms.cleaned_data['confirm_password_register_form']:
                messages.error(request, "As senhas não são iguais.")
                return render(request, "Forms/Register.html", {"form": register_forms})

            name_form_register = register_forms.cleaned_data['username_register_form']
            email_form_register = register_forms.cleaned_data['email_register_form']
            password_form_register = register_forms.cleaned_data['password_register_form']

            if User.objects.filter(username=name_form_register).exists() or User.objects.filter(email=email_form_register).exists():
                messages.error(request, "Já existe um usuário com credenciais semelhantes. Tente novamente.")
                return render(request, "Forms/Register.html", {"form": register_forms})

            new_user = User.objects.create_user(
                username=name_form_register,
                email=email_form_register,
                password=password_form_register,
            )
            new_user.save()
            return redirect("/forms/login/")

    return render(request, "Forms/Register.html", {"form": register_forms})

# Vou usar isso no futuro, quando a complexidade da empresa favorecer.
# Atualmente, há um processo relativamente burocrático cujo qual não
# vale a pena ser investido tempo nisso.
def UsarApiCorreios(cep_destino):
    url = "https://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"
    params = {
        "nCdServico": "04014",
        "sCepOrigem": "37440000",
        "sCepDestino": cep_destino.replace("-", ""),
        "nVlPeso": "1",
        "nCdFormato": "1",
        "nVlComprimento": "20",
        "nVlAltura": "5",
        "nVlLargura": "15",
        "nVlDiametro": "0",
        "sCdMaoPropria": "N",
        "nVlValorDeclarado": "0",
        "sCdAvisoRecebimento": "N",
        "StrRetorno": "xml"
    }

    response = requests.get(url, params=params)
    tree = ElementTree.fromstring(response.content)
    prazo = tree.find('.//PrazoEntrega').text
    return int(prazo)

@csrf_exempt
def CalcFretePrazo(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        cep_destino = body.get('cep_destino')
        if(cep_destino):
            try:
                prazo_de_entrega_com_um_atraso = UsarApiCorreios(cep_destino) + 1
                return JsonResponse({'Success': prazo_de_entrega_com_um_atraso})
            except Exception as e:
                return JsonResponse({'ERROR': str(e) })
        else:
            return JsonResponse({'ERROR': 'Deve-se conter o cep do destinatário'}, status=400)
    else:
        return JsonResponse({'EROR':'Method not allowed'}, status=405)

@require_http_methods(['POST'])
@csrf_protect
def ProcessLogout(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Usuário não está logado"}, status=400)

        auth.logout(request)
        print("desconectado")
        return JsonResponse({"success": "Usuário desconectado com sucesso"}, status=200)
    except Exception as e:
        print(f'Houve um erro na requisição, e o erro é: {e}')
        return JsonResponse({'ERRO': f'Houve um erro na requisição, e o erro é: {e}'})

def Logout(request):
    auth.logout(request)
    messages.success(request, "Você foi deslogado")
    redirect("login_form")
    return render(request, "Forms/Logout.html")

# A autenticação JWT agora é feita diretamente pelo DRF (simplejwt),
# substituindo o middleware "verifyToken" que existia no serviço Node.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProcessUsers(request):
    try:
        user = request.user
        return JsonResponse({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, status=200)
    except Exception as e:
        return JsonResponse({ "error": str(e) }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProcessUsersPayments(request):
    try:
        GetPaymentsUsers = HistoryPayments.objects.filter(Username=request.user)
        if not GetPaymentsUsers.exists():
            return JsonResponse({"ERROR":"Nenhum produto encontrado para o respectivo usuário"}, status=404)
        products = [
            {
                "Product": payment.Product.name,
                "Image": payment.Image,
                "Value": payment.Value,
                "Amount": payment.Amount,
                "Date": payment.Date.isoformat(),
                "User": payment.Username.username,
            }
            for payment in GetPaymentsUsers
        ]
        return JsonResponse({"Products": products})
    except Exception as e:
        return JsonResponse({"ERROR": str(e)}, status=500)

@csrf_exempt
def ProcessPayments(request):
    data = json.loads(request.body)
    try:
        HistoryPayments.objects.create(
            Product=data['product_name'],
            Image=data['image_adress'],
            Value=data['product_value'],
            Amount=data['amount'],
            Date=data['payment_date'],
            Username=data['username']
        )

        gotProduct = DataBaseClothes.objects.get(name=data['product_name'])
        gotProduct.amount -= int(data['amount'])
        gotProduct.save()

        return Response({"Success": "Pagamento registrado com sucesso"}, status=201)
    except Exception as e:
        print(e)
        return Response({"ERROR": str(e)}, status=400)


@csrf_exempt
def ProcessSearch(request):
    try:
        body = json.loads(request.body)
        search = body.get("search")
        print(search)
        if not search:
            return JsonResponse({'ERROR': 'Pesquisa vazia.'}, status=400)

        product_qs = DataBaseClothes.objects.filter(name__icontains=search)
        print(product_qs)
        if not product_qs.exists():
            return JsonResponse({'ERROR': f'Não temos um produto como: {search}'}, status=404)

        products = list(product_qs.values("id", "name", "price", "image"))

        return JsonResponse({'results': products}, status=200)

    except Exception as e:
        return JsonResponse({'ERROR': str(e)}, status=400)

class SerializerClothesCategory(serializers.Serializer):
    Category = serializers.CharField()

@csrf_exempt
@require_http_methods(["POST"])
def ProcessSearchCategory(request):
    try:
        body = json.loads(request.body)
        validate_body = SerializerClothesCategory(data=body)
        if not validate_body.is_valid():
            return JsonResponse({"error":"The body is not valid"})
        category = validate_body.validated_data.get("Category")
        if not category:
            return JsonResponse({'error': "There is no Category"}, status=400)

        process_info = DataBaseClothes.objects.filter(category__name__iexact=category)
        # Sorry Uncle Bob, but I need to use another Serializer from other paste to use here
        # I promess to fix it soon.
        process_search = SerializersClothes(process_info, many=True)
        return JsonResponse({'results': process_search.data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_account(request):
    user = request.user
    auth.logout(request, user)
    user.delete()
    messages.success(request, f"usuário {user} deletado com sucesso")
    return redirect("main")


def MainPage(request, pk=None, **kwargs):
    cards = DataBaseClothes.objects.all()
    return render(request, "Main/FakeMainPage.html", {"cards": cards})


def ProfileUser(request):
    return render(request, "Main/ProfileUser.html")


def product(request, pk):
    photo_url = ''
    status_user = False
    is_superuser = False
    sizes = ["GG", "PP","P","M","G"]


    if request.user.is_authenticated:
        if request.user.is_superuser:
            is_superuser = True
            print("A verificação foi bem-sucedida, você é um administrador!")
        try:
            # Devemos manter a lógica assim pois, e se o usuário não tiver imagem?, ele vai cair na mesma página de quem não está logado?
            # Ou, e se o usuário acabou de deletar sua conta?, ele deve ser redirecionado para a mesma página padrão?
            social_account = SocialAccount.objects.filter(user=request.user, provider="google").first()
            if social_account:
                photo_url = social_account.extra_data.get("picture", "")
                # Isso deve permanecer assim (status_user como True), pois nem todos os usuários usarão o allauth.
            status_user = True
        except Exception as e:
            print(f"Houve um erro inesperado, o erro é: {e}")
    product_request = get_object_or_404(DataBaseClothes, pk=pk)

    # Create a flash-card about it
    boolean_fields = {
        field.name: getattr(product_request, field.name)
        for field in product_request._meta.fields
        if isinstance(field, models.BooleanField) and field.name != 'public'
    }

    return render(request, "Main/Product.html", {"product": product_request ,"each_user_image": photo_url, "StatusUser": status_user, "IsSuperUser":is_superuser,
                                                "dynamic_boolean_fields": boolean_fields})

@login_required
def ProfileUser(request):
    user = request.user
    return render(request, "Main/ProfileUser.html", {"user":user})

class Forget(PasswordResetView):

    template_name = "Emails/Forget.html"
    success_url = "password_reset_done"

    def Get(self, request, user):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', args=[uidb64, token]))
        return reset_link

    def get(self, request, *args, **kwargs):
        forget_forms = ConfirmEmail()
        return render(request, self.template_name, {"forget": forget_forms})

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            forget_forms = ConfirmEmail(request.POST)
            if forget_forms.is_valid():
                email_user = forget_forms.cleaned_data["email_register_form"]
                try:
                    if User.objects.filter(email=email_user).exists():
                        user = User.objects.get(email=email_user)
                        reset_link = self.Get(request, user)
                        print(f"A URL criada foi: {reset_link}")
                        try:
                            RetriveAccount.submit_email(user, reset_link)
                            messages.success(request, "Email enviado com sucesso")
                            print("Email enviado!")
                            return redirect(self.success_url)
                        except Exception as e:
                            messages.error(request, f"Erro ao enviar email: {e}")
                    else:
                        messages.error(request, "O email digitado não existe.")
                except Exception as e:
                    messages.error(request, f"Erro inesperado: {e}")

            return render(request, self.template_name, {"forget": forget_forms})


class ChangePassword_done(PasswordResetDoneView):
    template_name = 'Reset/password_reset_done.html'

def Reset_password_SendForm(request):
    ResetPasswordDone_forms = ResetPasswordDone()
    return render(request, "Emails/Reset.html", {"reset_password_form": ResetPasswordDone_forms})

class Reset_password(PasswordChangeView):
    template_name = "Emails/Reset.html"
    success_url = "password_reset_completed"

    def Post(self, request, *args, **kwargs):
        # Validar as informações contidas aqui.
        pass


class ChagePassword_completed(PasswordResetCompleteView):
    template_url = 'Reset/password_reset_completed.html'
    success_url = reverse_lazy("login_form")
