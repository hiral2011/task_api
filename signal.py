# #from django.contrib.auth.models import AbstractUser
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from api.models import Family, User, Permissions


# @receiver(post_save, sender=User)
# def create_saving_plan(sender,instance,created,*args,**kwargs):
#     if created:
#         user =instance
#         print("<><<><<<><><><><><><><><><><><><><><><><><><><><><>",user)
#         family=Family.objects.create(family_head=user,relation="self")
#         if user.family == family:
#             permission = Permissions.objects.create(permission=instance.admin_permission,role_id=1,user_id=user,family_id=family)
#         else :
#             permission = Permissions.objects.create(permission=instance.admin_permission,role_id=2,user_id=user,family_id=family)
#         print(family.user_id.add(user))
#         #User.objects.create(
#         #     user=instance,
#         #     subscription=subscription,
#         #     title=subscription.title,
#         #     price=subscription.price,
            
#         #  )
        