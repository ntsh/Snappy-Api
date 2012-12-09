from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import serializers
from django import forms

import re

from django.conf import settings



class CategoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name = name)

class  Category(models.Model):
    objects = CategoryManager()
    name = models.CharField(max_length = 32, unique=True )
    
    def natural_key(self):
        return (self.name)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = "category"
        unique_together = (('name'),)
        
'''
class UserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(username = username)
 ''' 
      
       
class Post(models.Model):
    user = models.ForeignKey(User, to_field = 'username')
    category = models.ForeignKey(Category, to_field = 'name')
    description = models.TextField(max_length = 2048, blank=True)
    image = models.ImageField(max_length = 256, upload_to = "images/pics", blank=True)
    time = models.DateTimeField(auto_now=True)
    votes = models.IntegerField(default = 0 ,blank = True)
    comments = models.IntegerField(default = 0, blank = True)
    state = models.IntegerField(default = 1, blank = True)
    '''
        state = 0 : Post deleted
        state = 1 : Post active
        state = 2 : Post Hidden
    '''
    
    def __unicode__(self):
        return str(self.id)
    
    def json(self):
        post = self
        #Creating the url for the image using BASE_URL
        img_rel_path = str(post.image)
        if(img_rel_path != ""):
            image_path = settings.BASE_URL + settings.MEDIA_URL + img_rel_path
            post.image = image_path
        post_json = serializers.serialize("json",[post])
        m = re.match(r"\[([\S\s]+)\]", post_json)
        return m.group(1)
        #return post_json
        
    class Meta:
        db_table = "post"
 

class Vote(models.Model):
    CHOICES = (
        (u'UP', u'UPVOTE'),
        (u'DOWN', u'DOWNVOTE'),
        (u'NONE', u'NONE')
    )
    
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User, to_field = 'username')
    vote = models.CharField(max_length=6, choices = CHOICES)
    time = models.DateTimeField(auto_now=True)
 
    def __unicode__(self):
        return str(self.id)


class Comment(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User, to_field = 'username')
    comment = models.CharField(max_length=2048)
    time = models.DateTimeField(auto_now=True)
 
    def __unicode__(self):
        return str(self.id) 
        
    def json(self):
        comment = self
        comment_json = serializers.serialize("json", [comment])
        m = re.match(r"\[([\S\s]+)\]", comment_json)
        return m.group(1)
    
    class Meta:
        db_table = "comment"


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file  = forms.FileField()
