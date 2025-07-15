from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializers import TokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import re
from accounts.serializers import UserSerializer, UserDetailSerializer, resetpasswordSerializer, \
    DynamicCoinsSerializer, DynamicLinksSerializer, CoinsPaymentSerializer, BannersSerializer,TransactionSerializer
from accounts.models import User, AccessTokensBlackList, Quiz, Pred, Transaction, DynamicCoins, DynamicLinks, CoinsPayment, Banners
from django.core.mail import EmailMessage
# Create your views here.
from rest_framework.decorators import permission_classes
from django.core.cache import cache
import math, random, jwt
from datetime import datetime, timedelta
import pytz, os
utc = pytz.UTC
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from swg_game.settings import SECRET_KEY
def generateOTP():

    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

class UserTokenObtainView(TokenObtainPairView):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            try:
                request.data._mutable = True
                request.data.update({"username":request.data["email"]})
            except:
                request.data["username"] = request.data["email"]
            # Attempt to retrieve the user object by email
            user = User.objects.filter(email=email).first()

            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # If the user and password are valid, proceed with token generation
            response = super(UserTokenObtainView, self).post(request, *args, **kwargs).__dict__['data']
            serializer = UserDetailSerializer(user)
            response.update({"data":serializer.data})
            return Response({"message":"User logged in successfully","msg":response, "code": status.HTTP_200_OK})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserLogoutView(APIView):
    permission_classes = IsAuthenticated,

    # def get(self, request, format=None):
    #     print(request.headers.get("Authorization", "").split(" ")[1])
            

    def post(self,request):
        try:
            token = request.data["token"]
            access_token = request.META.get("HTTP_AUTHORIZATION", None).split()[1]
            decoded_data = jwt.decode(access_token,key=SECRET_KEY, algorithms=['HS256'])
            jti = decoded_data["jti"]
            expiry = datetime.fromtimestamp(decoded_data["exp"])
            user=request.user
            user.last_login=datetime.now(utc)
            user.is_online = False
            user.save()
            try:
                AccessTokensBlackList.objects.create(
                    jti = jti,
                    user = request.user,
                    expires_at = expiry,
                    token = access_token
                )
                RefreshToken(token).blacklist()
            except:
                pass
            return Response({"message":"User logged out","msg": "Successfully logged out","code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class UserDetailsView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,
    
    def list(self, request, pk=None):
        user = User.objects.filter(id = request.user.id)
        if not user.exists():
            return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
        serializer = UserDetailSerializer(user, many=True)
        return Response({"msg":serializer.data,"code":status.HTTP_200_OK})

    def create(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            if "spin" in request.data:
                if user.spin_left == 0:
                    return Response({"error":"You don't have enough spins"}, status = status.HTTP_400_BAD_REQUEST)
                user.spin_left -= round(abs(int(request.data["spin"])))
            
            if "scratch" in request.data:
                if user.scratch == 0:
                    return Response({"error":"You don't have enough scratch"}, status = status.HTTP_400_BAD_REQUEST)
                user.scratch -= round(abs(int(request.data["scratch"])))
            user.coins = user.coins + round(abs(int(request.data["coins"])))
            user.save()
            serializer = UserDetailSerializer(user)
            data = dict()
            data.update({"total_coins":user.coins,
                        "spin":user.spin_left,
                        "scratch":user.scratch})
            return Response({"message":"Coins Added",
                            "msg":data, 
                            "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        
class LastLoginView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request):
        user = User.objects.filter(id=request.user.id).first()
        if user:
            current_datetime = datetime.now(utc)
            last_login_datetime = user.last_login

            # Calculate the time difference in days
            if last_login_datetime is not None:
                time_difference = (current_datetime - last_login_datetime).days
            else:
                time_difference = 0
                user.last_login = datetime.now(utc)
                user.coins = user.coins + 10
                user.save()
                return Response({"message":"Welcome to Spin & Win",
                                "d_show": True, 
                                "msg":"Welcome to Spin & Win","code":status.HTTP_200_OK,
                                "total_coins": user.coins,
                                "reward_coins": 10})

            # Define the coin rewards for consecutive logins (1st to 7th day)
            consecutive_login_rewards = [10, 20, 30, 40, 50, 60, 70]

            if time_difference >= 1:
                # Calculate the number of days since the last login (excluding today)
                days_since_last_login = time_difference - 1

                # Check if the user logged in today (current day)
                if time_difference == 1:
                    # Award coins based on consecutive login rewards
                    if days_since_last_login < len(consecutive_login_rewards):
                        reward_coins = consecutive_login_rewards[days_since_last_login]
                    else:
                        reward_coins = consecutive_login_rewards[-1]  # Max reward after 7 days

                    # Update user's coins and last_login
                    user.coins += reward_coins
                    user.last_login = current_datetime
                    user.save()
                    return Response({"msg": "Success",
                                    "d_show": True,
                                    "code": status.HTTP_200_OK,
                                    "total_coins": user.coins,
                                    "reward_coins": reward_coins})
                else:
                    # User didn't log in today, reset consecutive login count
                    user.last_login = current_datetime
                    user.save()

                    return Response({"msg": "Success",
                                    "d_show": False,
                                    "code": status.HTTP_200_OK,
                                    "total_coins": user.coins})
            else:
                return Response({"msg": "Success",
                                "d_show": False,
                                "total_coins": user.coins,
                                "code": status.HTTP_200_OK})
        else:
            return Response({"message": "Fail - User not found.", "msg": "Fail - User not found."}, status=status.HTTP_404_NOT_FOUND)

class UserRegistrationView(viewsets.ViewSet):
    def create(self, request, pk=None):
        # try:
            data = {
                "email": request.data["email"],
                "username":request.data["email"],
                "full_name": request.data["full_name"],
                "password": request.data["password"],
                "confirm_password": request.data["confirm_password"],
                "contact_number": request.data["contact_number"],
            }
            if "ref_code" in request.data:
                ref_user = User.objects.filter(ref_code=request.data["ref_code"]).first()
                if ref_user:
                    ref_user.coins = ref_user.coins + 100
                    ref_user.save()
                    data.update({"coins":50})
                else:
                    pass

            if User.objects.filter(email = request.data["email"]).exists():
                return Response({"error":"Email already exists"}, status = status.HTTP_400_BAD_REQUEST)
            if not re.match("^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", str(data["email"].lower())):
                return Response({"error": "Enter a valid email"},status=status.HTTP_400_BAD_REQUEST)
            if not re.match("^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])",data["password"]):
                return Response({"error":"Password must contain one lowercase, one uppercase, one number, and a special character"},status=status.HTTP_400_BAD_REQUEST)
            if len(data["password"]) <= 8:
                return Response({"error": "Password is short"}, status=status.HTTP_400_BAD_REQUEST)
            if data["password"] != data["confirm_password"]:
                return Response({"error": "Password and Confirm password do not match"},status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"User Resigtration Successful","msg": serializer.data, "code": status.HTTP_200_OK}, status = status.HTTP_200_OK)
            errors = serializer.errors
            try:
                for _, messages in errors.items():
                    for message in messages:
                        return Response({"error":message.replace("field",_)}, status = status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error":errors}, status=status.HTTP_400_BAD_REQUEST)

        # except Exception as e:
        #     return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

class SendOtp(APIView):
    def post(self, request):
        data = request.data
        # try:
        Username = data.get("email").lower()
        user_email = User.objects.filter(username=Username)
        if user_email.exists():
            user_email=user_email[0]
            otp=generateOTP()
            email = user_email.username
            userotp = user_email.otp = otp
            user_email.save()
            
            ## using cache for more than 3 login counts 
            key = f"otp_attempts_{ request.data['email'] }_{request.META['REMOTE_ADDR']}"
            attempts = cache.get(key, 0)
            if attempts >= 4:
                return Response({"error":"Please try again after a few minutes"}, status = status.HTTP_400_BAD_REQUEST)
            else:
                attempts += 1
                cache.set(key, attempts, timeout = 300)
            
            
            recipient_list = [email]
            message = get_template("otp.html").render({
                "user": user_email.full_name,
                "otp": userotp
            })
            mail = EmailMessage(
                subject = "OTP Verification",
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to = recipient_list
            )
            mail.content_subtype = "html"
            mail.send()
            users=User.objects.get(username=Username)
            users.otpgenerationTime=datetime.now(utc)+timedelta(minutes=5)
            users.failedLoginCount = 0
            users.save()
            return Response({"message":"OTP sent successfully","msg": "OTP sent to your registered email","code":status.HTTP_200_OK})
        return Response({"error": "Invalid credentials"},status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"msg": str(e)},status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(viewsets.ViewSet):
    def create(self, request):
        try:
            users=User.objects.filter(email = request.data["email"])
            if not users.exists():
                return Response({"error":"Invalid Credentials"}, status = status.HTTP_400_BAD_REQUEST)
            data={
                "password":request.data["password"],
                "confirm_password":request.data["confirm_password"],
                "username":users[0].email,
            }
            
            if users[0].otp_verified:
                r_p = re.compile("^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])")
                if len(data["password"]) <= 8:
                    return Response({"error": "Password is short"}, status=status.HTTP_400_BAD_REQUEST)
                if not r_p.match(data["password"]):
                    return Response({"error":"Password must contain one lowercase, one uppercase, one number, and a special character"}, status = status.HTTP_400_BAD_REQUEST)
                # if not re.match('^(?=.*[A-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9]).{8,}$',data["password"]):
                #     return Response({"error":"Password must contain one lowercase, one uppercase, one number, and a special character"},status=status.HTTP_400_BAD_REQUEST)
                if data["password"] == data["confirm_password"]:
                    serializer=resetpasswordSerializer(instance=users[0], data=data, partial=True)
                    if serializer.is_valid():
                        user = users[0]
                        user.otp = None
                        user.save()
                        serializer.save()
                        return Response({"message":"Password changed successfully","msg":"Password changed successfully","code":status.HTTP_200_OK})
                    return Response({"error":"New password is invalid"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error":"Passwords did not match"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error":"Generate & verify OTP again"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(viewsets.ViewSet):
    def create(self, request):
        users=User.objects.filter(email = request.data["email"])
        if not users.exists():
            return Response({"error":"Invalid Credentials"}, status = status.HTTP_400_BAD_REQUEST)
        if not users[0].otp:
            return Response({"error":"First Generate OTP!"}, status = status.HTTP_400_BAD_REQUEST)
        currenttime=datetime.now(utc)
        valid_time=users[0].otpgenerationTime
        if valid_time >= currenttime:
            if int(users[0].otp) == int(request.data["otp"]):
                user_verify = User.objects.filter(email= request.data["email"]).first()
                user_verify.otp_verified = True
                user_verify.save()
                return Response({"message":"OTP Verified","msg":"OTP Verified","code":status.HTTP_200_OK})
            return Response({"error":"Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"OTP is expired, Please generate again"}, status = status.HTTP_400_BAD_REQUEST)

class QuizView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request, pk=None):
        try:
            user = User.objects.filter(id = request.user.id)
            if not user.exists():
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            quiz = Quiz.objects.filter(user = user[0])
            quiz = quiz[0]
            if "quiz_1" in request.data:
                quiz.quiz_1 = bool(request.data["quiz_1"])
            if "quiz_2" in request.data:
                quiz.quiz_2 = bool(request.data["quiz_2"])
            if "quiz_3" in request.data:
                quiz.quiz_3 = bool(request.data["quiz_3"])
            if "quiz_4" in request.data:
                quiz.quiz_4 = bool(request.data["quiz_4"])
            if "quiz_5" in request.data:
                quiz.quiz_5 = bool(request.data["quiz_5"])
            quiz.save()
            if "coins" in request.data:                
                user_ = user[0]
                user_.coins += round(abs(int(request.data["coins"])))
                user_.save()
            serializer = UserDetailSerializer(user, many=True)
            return Response({"msg":serializer.data, "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error":str(e)}, status = status.HTTP_400_BAD_REQUEST)

class PredView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request, pk=None):
        try:
            user = User.objects.filter(id = request.user.id)
            if not user.exists():
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            pred = Pred.objects.filter(user = user[0])
            pred = pred[0]
            if "pred_1" in request.data:
                pred.pred_1 = bool(request.data["pred_1"])
            if "pred_2" in request.data:
                pred.pred_2 = bool(request.data["pred_2"])
            if "pred_3" in request.data:
                pred.pred_3 = bool(request.data["pred_3"])
            if "pred_4" in request.data:
                pred.pred_4 = bool(request.data["pred_4"])
            if "pred_5" in request.data:
                pred.pred_5 = bool(request.data["pred_5"])
            pred.save()
            if "coins" in request.data:
                user_ = user[0]
                user_.coins += round(abs(int(request.data["coins"])))
                user_.save()
            serializer = UserDetailSerializer(user, many=True)
            return Response({"msg":serializer.data, "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error":str(e)}, status = status.HTTP_400_BAD_REQUEST)


class QuizResetView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request, pk=None):
        user = User.objects.filter(id = request.user.id)
        try:
            if not user.exists():
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            quiz = Quiz.objects.filter(user = user[0])
            quiz = quiz[0]
            quiz.quiz_1 = False
            quiz.quiz_2 = False
            quiz.quiz_3 = False
            quiz.quiz_4 = False
            quiz.quiz_5 = False
            quiz.save()
            serializer = UserDetailSerializer(user, many=True)
            return Response({"msg":serializer.data, "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error":str(e)}, status = status.HTTP_400_BAD_REQUEST)
    

class CoinsAddView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request):
        user = User.objects.filter(id = request.user.id)
        try:
            if not user.exists():
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error":str(e)}, status = status.HTTP_400_BAD_REQUEST)

class ProfileUpdate(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            if "full_name" in request.data:
                user.full_name = request.data["full_name"]
            if "contact_number" in request.data:
                user.contact_number = request.data["contact_number"]
            if "picture" in request.FILES:
            # Delete the previous profile picture if it exists
                if user.picture:
                    # Construct the path to the previous picture
                    previous_picture_path = os.path.join(user.picture.path)
                    # Check if the file exists and delete it
                    try:
                        if os.path.isfile(previous_picture_path):
                            os.remove(previous_picture_path)
                    except:
                        pass
                # Save the new profile picture
                else:
                    user.picture = user.picture
                user.picture = request.FILES["picture"]
            user.save()
            serializer = UserDetailSerializer(user)
            return Response({"message":"Profile Updated Successfully","msg":serializer.data, "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
    
class SpinScratchUpdate(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            data = dict()
            if "spin" in request.data:
                user.spin_left += round(abs(int(request.data["spin"])))
                data.update({"spin":"Spin added successfully"})
            
            if "scratch" in request.data:
                user.scratch += round(abs(int(request.data["scratch"])))
                data.update({"scratch":"Scratch added successfully"})

            user.save()
            serializer = UserDetailSerializer(user)
            return Response({"message":data["spin"] if "spin" in data else data["scratch"],
                            "msg":data, 
                            "code":status.HTTP_200_OK})
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)


class PaymentView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def create(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            to_convert_coins = round(abs(int(request.data["coins"])))
            if to_convert_coins < int(user.coins):
                amount = CoinsPayment.objects.filter(coins = to_convert_coins).first().funds
                if not amount:
                    return Response({"error":"You do not have enough coins","code":status.HTTP_400_BAD_REQUEST})
                # if amount.is_integer():
                transaction = Transaction.objects.create(user = user, amount = amount,payment_type = request.data["payment_type"].capitalize())
                user.coins = user.coins - to_convert_coins
                user.save()
                serializer = UserDetailSerializer(user)
                return Response({"message":"Request created for money transfer","msg":serializer.data, "code":status.HTTP_200_OK})
                # return Response({"error":"The requested amount cannot be fullfilled","code":status.HTTP_400_BAD_REQUEST})        
            return Response({"error":"You do not have enough coins","code":status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
    

class DynamicCoinsView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def list(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            query = DynamicCoins.objects.all()
            serializer = DynamicCoinsSerializer(query, many = True)
            quiz= list()
            scratch = list()
            pred = list() 
            game = list()
            spin = list()
            for i in serializer.data:
                if "quiz" in i["type"]:
                    quiz.append(i)
                
                if "pred" in i["type"]:
                    pred.append(i)

                if "game" in i["type"]:
                    game.append(i)
                
                if "spin" in i["type"]:
                    spin.append(i)
                
                if "scratch" in i["type"]:
                    scratch.append(i)

            msg = dict()
            msg.update({"quiz":quiz,"pred":pred,"game":game,"spin":spin,"scratch":scratch})
            return Response({"msg":msg,"code":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        

class DynamicLinksView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,
    
    def list(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            data = DynamicLinks.objects.all()
                        # Reformat the data
            reformatted_data = {}
            for item in data:
                reformatted_data[item.name] = item.link
            return Response({"msg":reformatted_data,"message":"Dynamic links data", "code":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        

class CoinsPaymentView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,
    
    def list(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            data = CoinsPayment.objects.all()
            return Response({"msg":CoinsPaymentSerializer(data, many = True).data, "code":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        

class BannersView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def list(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            data = Banners.objects.all()
            return Response({"msg":BannersSerializer(data, many = True).data,"message":"Banners data", "code":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
    

class TransactionView(viewsets.ViewSet):
    permission_classes = IsAuthenticated,

    def list(self, request):
        try:
            user = User.objects.filter(id = request.user.id).first()
            if not user:
                return Response({"error":"User Does not Exists"}, status = status.HTTP_400_BAD_REQUEST)
            data = Transaction.objects.filter(user = user)
            return Response({"msg":TransactionSerializer(data, many = True).data,"message":"Transactions of user", "code":status.HTTP_200_OK},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)