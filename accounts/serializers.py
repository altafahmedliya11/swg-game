from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from rest_framework import serializers
from accounts.models import *
from django.contrib.auth import get_user_model



def camel_case(value):
    try:
        return value.strip().lower().title()
    except Exception as e:
        return False

class CapitalizeCharField(serializers.CharField):
    def to_internal_value(self, data):
        if data is not None:
            return super().to_internal_value(data.title())
        else:
            return super().to_internal_value(data)
    
    def to_representation(self, value):
        if value is not None:
            return super().to_representation(value.title())
        else:
            return super().to_representation(value)


class TokenSerializer(TokenObtainPairSerializer):
    # captcha = ReCaptchaField()

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user_id"] = self.user.id
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        "bad_token": ("Token is expired or invalid")
    }

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Inherit from `TokenRefreshSerializer` and touch the database
    before re-issuing a new access token and ensure that the user
    exists and is active.
    """
    error_msg = "No active account found with the given credentials"
    def validate(self, attrs):
        token_payload = token_backend.decode(attrs["refresh"])
        try:
            user = get_user_model().objects.get(pk=token_payload["user_id"])
            if not user.is_active:
                raise serializers.ValidationError(
                    "no active account found."
            )
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                "account is deleted."
            )
        return super().validate(attrs)


class UserDetailSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField()
    pred = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "password","coins","quiz","spin_left","scratch","ref_code","contact_number","picture","pred"]
    
    def get_quiz(self, obj):
        return Quiz.objects.filter(user = obj).values()

    def get_pred(self, obj):
        return Pred.objects.filter(user = obj).values()
    
    def get_picture(self, obj):
        return "http://165.22.8.90:1110/media/"+ str(obj.picture)

class UserSerializer(serializers.ModelSerializer):
    full_name = CapitalizeCharField()
    email = serializers.EmailField()
    quiz = serializers.SerializerMethodField()
    pred = serializers.SerializerMethodField()
    coins = serializers.IntegerField(required = False)
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "password","coins","quiz","spin_left","scratch","ref_code","contact_number","picture","pred"]
        extra_kwargs = {
            "password": {"write_only": True},
            "ref_code": {"required": False}  # Set ref_code as not required

        }

    def get_quiz(self, obj):
        return Quiz.objects.filter(user = obj).values()

    def get_pred(self, obj):
        return Pred.objects.filter(user = obj).values()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            contact_number = validated_data["contact_number"],
            coins = validated_data["coins"] if "coins" in validated_data else 0
            )
        quiz = Quiz.objects.create(
            user = user
        )
        pred = Pred.objects.create(
            user = user
        )
        return user

    def validate_full_name(self, value):
        valid = camel_case(value)
        if not valid:
            raise serializers.ValidationError("full name must contain only alphabetic characters.")
        return valid

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get("email")

        if User.objects.filter(username = email).exists():
            raise serializers.ValidationError("User already exists")

        return attrs
    
    def get_picture(self, obj):
        return "http://165.22.8.90:1110/media/"+ str(obj.picture)

class resetpasswordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    class Meta:
        model = User
        fields = "__all__"

    def save(self):
        username = self.validated_data["username"].lower()
        password = self.validated_data["password"]
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            return user
        else:
            raise serializers.ValidationError({"error": "Please enter valid crendentials"})
        
    
class DynamicCoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicCoins
        fields = ['name','coins','time_in_seconds',"type"]


class DynamicLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicLinks
        fields = ['name','link']


class CoinsPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinsPayment
        fields = ['coins','funds']


class BannersSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    def get_picture(self, obj):
        return "http://165.22.8.90:1110/media/"+ str(obj.picture)
    
    class Meta:
        model = Banners
        fields = ['name','link','picture','created_on']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user','contact_number','amount','status','created_on','payment_type']