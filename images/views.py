from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from actions.utils import create_action
import redis
from django.conf import settings

from .forms import ImageCreateForm
from .models import Image

r= redis.Redis(host=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB)

# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        # Form was submitted
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Form data is valid
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # Assign current user to the item
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            # Redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
            # Build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})

def image_detail(request,id,slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr('image:{}:views'.format(image.id))
    r.zincrby('image_ranking',1,image.id)
    return render(request, 'images/image/detail.html', {'section': 'images', 'image': image, 'total_views': total_views})

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

@login_required
def image_ranking(request):
    image_ranking = r.zrange('image_ranking',0,-1,desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})