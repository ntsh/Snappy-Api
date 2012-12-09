from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response, get_object_or_404  

from stream.models import *
import json
import base64
import time
import re
from django.core import serializers
from django.core.context_processors import csrf
from django.template import Context, loader, RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate, login , logout

from django.conf import settings

def invite(request):
    return render_to_response('invitepage.html',context_instance=RequestContext(request))

@csrf_exempt
def login(request):
    username = str(request.POST['username'])
    password = str(request.POST['password'])
    user = authenticate(username=username, password=password)
    if user is not None:
        return HttpResponse('pass')
    else:
        return HttpResponse('Error : Wrong username or password')

def is_username_available(username):
    user_check = User.objects.filter(username__exact = username)
    if (user_check.count() == 0):
        return True
    else:
        return False

@csrf_exempt
def signup(request):
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['emailid']
    if (is_username_available(username) != True):
        return HttpResponse("Error : Username already exists.")
    length = len(username)   
    if(length < 4 ):
        return HttpResponse("Error : Username must be atleast 4 characters long")
    if(length > 30):
        return HttpResponse("Error : Username must be atmost 30 characters long")
    if(re.match("^[\w\.]+$", username )) is None:
        return HttpResponse("Error : Username must only contain alphanumeric, _ and . ")
    # if (password != password2):
    #     return HttpResponse("Error : Password mismatch.")
    user = User(username = username , email = email)
    user.set_password(password)
    user.save()
    return HttpResponse('pass')

def user_settings(request):
    response = ''
    username = request.POST['username']
    user = User.objects.get(username = username)
    if 'new_username' in request.POST:
        new_username = request.POST['new_username']
        if (is_username_available(new_username) != True):
            return HttpResponse("Error : Username already exists.")
        user.username = new_username
        response += " New Username : " + new_username
    if 'email' in request.POST:
        email = request.POST['emailid']
        user.email = email
        response += " New Email : " + email
    if 'new_password' in request.POST:
        new_password = request.POST['new_password']
        old_password = request.POST['old_password']
        if (user.check_password(old_password)):
            user.set_password(new_password) 
            response += " New password set successfully."
    return HttpResponse(response)
    
def post_json(request,post_id):
    post = get_object_or_404(Post,pk=post_id)
    post_json = post.json()
    return HttpResponse(post_json)
    #return render_to_response('post.html',{'img':image},context_instance=RequestContext(request))

#def user_posts_json(request, username, page_id):
@csrf_exempt
def vote(request,post_id):
    username = request.POST['user']
    vote = request.POST['vote']
    user = User.objects.get(username__exact = username)
    post = Post.objects.get(id = post_id)
    v_old = Vote.objects.filter(user = user, post = post)
    if (len(v_old) == 0):
        v = Vote(user = user, post = post, vote = vote)
        if(vote == 'UP'):
            post.votes += 1
        elif(vote == 'DOWN'):
            post.votes -= 1
    else:
        v = v_old[0]
        if (vote == 'UP'):
            if(v.vote == 'DOWN'):
                v.vote = 'NONE'
                post.votes += 1
            elif(v.vote == 'NONE'):
                v.vote = 'UP'
                post.votes += 1
        elif (vote == 'DOWN'):
            if(v.vote == 'NONE'):
                v.vote = 'DOWN'
                post.votes -= 1
            elif(v.vote == 'UP'):
                v.vote = 'NONE' 
                post.votes -= 1          
    post.save()
    v.save()
    return HttpResponse("Voted post" + post_id + " as " + vote + " by user " + username)

@csrf_exempt
def comment(request,post_id):
    username = request.POST['user']
    #post_id = POST['post_id']
    comment = request.POST['comment']
    user = User.objects.get(username__exact = username)
    post = Post.objects.get(id = int(post_id))
    com = Comment(user = user, post = post, comment = comment)
    post.comments += 1
    post.save()
    com.save()
    return HttpResponse("Comment :" + comment + " post_id " + post_id + " by user " + username)

def comments_json(request, post_id, page_id):
    comments_per_page = 20
    page_id = int(page_id)
    start = (page_id-1) * comments_per_page
    end = (page_id) * comments_per_page
    post_id = int(post_id)
    post = Post.objects.get(id = post_id)
    comments = Comment.objects.filter(post = post).order_by('-id')[start:end]
    count = len(comments)
    if (count < comments_per_page):        
        if(count == 0):
            return HttpResponse("[]") 
        else:
            end = start + count    
    comments_all = "["
    for i in range(start,end):
        comments_all += comments[i-start].json()
        comments_all += ", "
    m = re.match(r"(.*),\s+", comments_all)
    comments_all = m.group(1)
    comments_all += "]"
    return HttpResponse(comments_all)

def new_posts_json(request, page_id, feed = 'new', username = '', cat = ''):
    posts_per_page = 7
    page_id = int(page_id)
    start = (page_id-1) * posts_per_page
    end = (page_id) * posts_per_page
    if (feed == 'new'):
        posts = Post.objects.filter(state = 1).order_by('-id')[start:end]
    elif (feed == 'popular'):
        min_votes = 4
        posts = Post.objects.filter(votes__gte = min_votes, state = 1).order_by('-id')[start:end]
    elif (feed == 'user_posts'):
        posts = Post.objects.filter(user = username, state = 1).order_by('-id')[start:end]
    elif (feed == 'user_upvotes'):
        user = User.objects.get(username = username)
        vs = user.vote_set.all().filter(vote = 'UP').order_by('-id')[start:end]
        posts = []
        for i in range(0,len(vs)):
            ps = vs[i].post
            if ps.state == 1 :
                posts.append(ps)
    elif (feed == 'cat_new'):
        category = Category.objects.get(name = cat)
        posts = Post.objects.filter(category = category, state = 1).order_by('-id')[start:end]
    elif (feed == 'cat_popular'):
        min_votes = 4
        category = Category.objects.get(name = cat)
        posts = Post.objects.filter(category = category, votes__gte = min_votes, state = 1).order_by('-id')[start:end]
    if ((len(posts)) < posts_per_page):
        count = len(posts)
        if(count == 0):
            return HttpResponse("[]") 
        else:
            end = start + count        
    '''
    posts_all = []
    for i in range(start,end):
        posts_all.append(posts[i-start].json())
    '''
    
    posts_all = "["
    for i in range(start,end):
        posts_all += posts[i-start].json()
        posts_all += ", "
    m = re.match(r"(.*),\s+", posts_all)
    posts_all = m.group(1)
    posts_all += "]"
    
    #posts_all = serializers.serialize("json",posts)
    return HttpResponse(posts_all)

@csrf_exempt
def upload(request):  
    if request.method == 'POST':
        desc = request.POST['story']
        cat = request.POST['cat']
        username = request.POST['user']
        #
        cat = Category.objects.get(name__exact = cat)
        user = User.objects.get(username__exact = username)
        if(request.POST['post_type']=='photo'):
            image_loc = handle_uploaded_file(request.FILES['file'])
            post = Post(user = user, category = cat, description = desc, image = image_loc )
        else:
            post = Post(user = user, category = cat, description = desc)
        post.save()
        return HttpResponse(post.json())
           
@csrf_exempt      
def upload_file(request):
    title = request.POST.get('title','notitle') 
    '''if 'title' in request.POST:
        title = request.POST['title']
    else:
        title = 'none'
    '''
    if(title):
        resp = 'title is' + title
    else:
        resp = 'title is not' + title
    return HttpResponse(resp)
    
    if request.method == 'POST':
        #form = UploadFileForm(request.POST, request.FILES)
        handle_uploaded_file(request.FILES['file'])
        #param = request.POST['value2']
        param = "hi"
        title = str(request.POST['title'])
        desc = str(request.POST['desc'])
        cat = str(request.POST['cat'])
        post = ""
        return HttpResponse("python: right.. " + title + "..." + desc + "..." + cat)   
        if form.is_valid():
            #handle_uploaded_file(request.FILES['imageData'])
            #return HttpResponseRedirect('/success/url/')
            #return HttpResponse(request.POST['imageData'])
            return HttpResponse("right")
        else:
            return HttpResponse("python: something wrong with form")
    else:
        form = UploadFileForm()
    #return HttpResponse(request.get_host())
    return render_to_response('upload.html', {'form': form},context_instance=RequestContext(request))
    return HttpResponse("wrong")
    
def handle_uploaded_file(f):
    t = str(time.time())
    image_loc = 'images/pics/img_'+ t +'.jpeg'
    with open(settings.MEDIA_ROOT + image_loc , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        #destination.write(f)
    return image_loc

