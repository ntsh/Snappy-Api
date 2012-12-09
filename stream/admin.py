from stream.models import *
from django.contrib import admin
#import jqmobile

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'description', 'id','votes','comments')
    list_filter = ['category__name','user__username']
    search_fields = ['description']
        
admin.site.register(Post,PostAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Vote)
