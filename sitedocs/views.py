# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.conf import settings

def tos(request):
	return render_to_response('sitedocs/tos.html')

def privacy(request):
	return render_to_response('sitedocs/privacy.html')