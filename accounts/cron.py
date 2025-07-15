from accounts.models import User, Quiz, Pred
from datetime import datetime

def reset_data():
    print("Inside Cron Updating values |---| Executed on =====>",datetime.now())
    User.objects.all().update(spin_left=5, scratch=5)
    Quiz.objects.all().update(
        quiz_1 = False,
        quiz_2 = False,
        quiz_3 = False,
        quiz_4 = False,
        quiz_5 = False
    )
    Pred.objects.all().update(
        pred_1 = False,
        pred_2 = False,
        pred_3 = False,
        pred_4 = False,
        pred_5 = False
    )

