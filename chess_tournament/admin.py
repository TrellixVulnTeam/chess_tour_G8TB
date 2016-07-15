from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from chess_tournament.models import *

class ChessInline(admin.StackedInline):
    model = Chess
    can_delete = False
    verbose_name_plural = 'Chess'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ChessInline, )

# Define a new User admin
class ChessAdmin(admin.ModelAdmin):
    fields = ('user', 'last_activity', 'is_avaliable', 'in_progress')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Chess)
admin.site.register(Tournament)
admin.site.register(Round)