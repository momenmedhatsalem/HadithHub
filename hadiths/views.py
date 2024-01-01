from django.contrib import messages
from .models import Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from random import choice
from typing import List
import textwrap
from bidi.algorithm import get_display
import arabic_reshaper
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse, JsonResponse
import langid


from django.core.paginator import Paginator

from .models import Profile, Hadith_Read, ProfileHadith, HadithSource, Hadith, ProfileHadithSource

from datetime import date

from django.contrib.auth.decorators import login_required

from django.http import Http404


def index(request):
    # Load sources from database
    sources = HadithSource.objects.all().values_list('name', flat=True)
    # Render page
    context = {
        'sources': sources,
    }

    return render(request, 'index.html', context)


def search_hadiths(hadiths, query):
    # Detect language of search query
    lang, _ = langid.classify(query)

    # Filter hadiths based on search query
    if query:
        if lang == 'ar':
            hadiths = list(filter(lambda hadith: query.lower()
                           in hadith.text_ar.lower(), hadiths))
        else:
            hadiths = list(filter(lambda hadith: query.lower()
                           in hadith.text_en.lower(), hadiths))
    return hadiths


def fit_text_to_image(text: str, image_size: tuple, font_name: str) -> tuple:
    def text_fits(text, font_size):
        font = ImageFont.truetype(font_name, font_size)
        lines = textwrap.wrap(text, width=len(text) * font_size // 42)
        y = 0
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            if text_width > (image_size[0] - 20):
                return False
            y += text_height + 10
        return y <= image_size[1]

    # Create a new image with a white background
    image = Image.new('RGB', image_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Find the largest font size that allows the text to fit within the image
    min_font_size = 1
    max_font_size = 150
    while min_font_size <= max_font_size:
        mid_font_size = (min_font_size + max_font_size) // 2
        if text_fits(text, mid_font_size):
            min_font_size = mid_font_size + 1
        else:
            max_font_size = mid_font_size - 1

    # Wrap the text into multiple lines based on the calculated font size
    optimal_font_size = max_font_size
    lines = textwrap.wrap(text, width=len(text) * optimal_font_size // 36)

    return (optimal_font_size, len(lines), lines)


def hadith_to_image(text_en: str,
                    text_ar: str,
                    color=(0, 0, 0),
                    background_color=(255, 255, 255)) -> Image.Image:

    def draw_text(draw: ImageDraw.Draw,
                  lines: List[str],
                  y: int,
                  max_line_length: int,
                  font_size: int) -> None:
        font = ImageFont.truetype('arial.ttf', font_size)
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            x = (max_line_length - text_width) // 2
            draw.text((x, y), line, fill=color, font=font)
            y += text_height + 10

    # Create a new square image with a white background
    image_size = (1080, 1080)
    image = Image.new('RGB', image_size, background_color)
    draw = ImageDraw.Draw(image)

    # Reshape and reorder the Arabic text
    reshaped_text_ar = arabic_reshaper.reshape(text_ar)
    bidi_text_ar = get_display(reshaped_text_ar)

    # Determine the optimal font size and line breaks for the English and Arabic texts
    font_size_en, num_lines_en, lines_en = fit_text_to_image(
        text_en, image_size, 'arial.ttf')
    font_size_ar, num_lines_ar, lines_ar = fit_text_to_image(
        bidi_text_ar, image_size, 'arial.ttf')

    # Draw the English and Arabic texts onto the image
    padding = 50
    draw_text(draw, lines_en, image_size[1] // 4 +
              padding, image_size[0] - 2*padding, font_size_en)
    draw_text(draw, lines_ar, image_size[1] // 4 * 3 +
              padding, image_size[0] - 2*padding, font_size_ar)

    return image


def hadith_image(request, hadith_id):
    # Get the Hadith object from the database
    hadith = Hadith.objects.get(hadith_id=hadith_id)

    # Convert the Hadith to an image
    image = hadith_to_image(hadith.text_en, hadith.text_ar, 20)

    # Create a response object with the appropriate content type
    response = HttpResponse(content_type='image/png')

    # Set the content disposition header to trigger a download
    response['Content-Disposition'] = 'attachment; filename="hadith.png"'

    # Save the image to the response object
    image.save(response, 'PNG')

    return response


def hadith(request, source):
    # Load hadiths from Django database
    if source == 'x':
        hadiths = Hadith.objects.all()
        per_page = 30
    elif source == 'y':
        hadiths = Hadith.objects.all()
        today = date.today()
        index = today.toordinal() % len(hadiths)
        hadith = hadiths[index]
        return render(request, 'hadith.html', {'page_obj': [hadith], 'day': 'true'})
    else:
        hadiths = Hadith.objects.filter(source__name=source)
        per_page = 1
    # Filter hadiths based on search query
    search_query = request.GET.get('search', '')
    hadiths = search_hadiths(hadiths, search_query)
    # Set page number based on URL query string or calculated value
    page_number = request.GET.get('page')
    # Get user progress for a specific source
    user = request.user
    read_hadith_ids = []
    if user.is_authenticated and source != 'x':
        profile, created = Profile.objects.get_or_create(user=user)
        try:
            profile_hadith_source = ProfileHadithSource.objects.get(
                profile=profile, hadith_source__name=source)
            # Get the first unread Hadith
            read_hadith_ids = ProfileHadith.objects.filter(
                profile=profile).values_list('hadith_id', flat=True)
            unread_hadiths = hadiths.exclude(hadith_id__in=read_hadith_ids)
            if not page_number:
                if unread_hadiths.exists():
                    first_unread_hadith = unread_hadiths.first()
                    page_number = hadiths.filter(
                        hadith_id__lte=first_unread_hadith.hadith_id).count()
                else:
                    page_number = 1
            else:
                page_number = int(page_number)
        except ProfileHadithSource.DoesNotExist:
            hadith_source = HadithSource.objects.get(name=source)
            profile_hadith_source = ProfileHadithSource.objects.create(
                profile=profile, hadith_source=hadith_source)
            page_number = 1
        total_hadiths = hadiths.filter(source__name=source).count()
        progress = (profile_hadith_source.hadiths_read_number /
                    total_hadiths) * 100
        progress = round(progress, 4)
    else:
        progress = 0
        page_number = int(page_number) if page_number else 1
    paginator = Paginator(hadiths, per_page)
    page_obj = paginator.get_page(page_number)
    context = {
        'username': request.user.username,
        'page_obj': page_obj,
        'progress': progress,
        'search_query': search_query,
        'source': source,
        'read': read_hadith_ids,
    }
    return render(request, 'hadith.html', context)


def update_progress(request, hadith_id, source):
    user = request.user
    profile = Profile.objects.get(user=user)
    sources = HadithSource.objects.all().values_list('name', flat=True)

    try:
        profile_hadith_source = ProfileHadithSource.objects.get(
            profile=profile, hadith_source__name=source)
    except ProfileHadithSource.DoesNotExist:
        try:
            # Create a new ProfileHadithSource object for the user if one does not already exist
            hadith_source = HadithSource.objects.get(name=source)
            profile_hadith_source = ProfileHadithSource.objects.create(
                profile=profile, hadith_source=hadith_source)
        except HadithSource.DoesNotExist:
            return JsonResponse({'message': 'The specified Hadith source does not exist.'})

    # Check if the user has already read the hadith
    hadith = Hadith.objects.get(hadith_id=hadith_id)
    if not ProfileHadith.objects.filter(profile=profile, hadith=hadith).exists():
        # Update the progress only if the user has not already read the hadith
        profile_hadith_source.hadiths_read_number += 1
        profile_hadith_source.save()
        # Create a new ProfileHadith object to keep track of the hadith that the user has read
        ProfileHadith.objects.create(profile=profile, hadith=hadith)

    return JsonResponse({'message': 'Progress updated'})


def single_hadith(request, hadith_id):
    try:
        # Try to get the Hadith with the given id
        hadith = Hadith.objects.get(hadith_id=hadith_id)
    except Hadith.DoesNotExist:
        # If a Hadith with this id doesn't exist, raise a 404 error
        raise Http404("Hadith does not exist")

    # Render page
    context = {
        'hadith': hadith,

    }
    return render(request, 'singlehadith.html', context)


def my_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            # Invalid credentials
            messages.error(request, 'Invalid username or password')
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form})
    elif request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})


def my_create_account_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Profile object for the new user
            profile = Profile.objects.create(user=user)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'create_account.html', {'form': form})


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    sources = profile.sources.all()
    source_stats = []
    for source in sources:
        phs = ProfileHadithSource.objects.get(
            profile=profile, hadith_source=source)
        source_stats.append({
            'source': source,
            'hadiths_read': phs.hadiths_read_number
        })
    if request.method == 'POST':
        source_id = request.POST.get('source_id')
        if source_id:
            phs = ProfileHadithSource.objects.get(
                profile=profile, hadith_source_id=source_id)
            phs.hadiths_read_number = 0
            phs.save()
            # Delete all ProfileHadith objects associated with the user's profile and Hadiths from that source
            ProfileHadith.objects.filter(
                profile=profile, hadith__source_id=source_id).delete()
            return redirect('profile')
    context = {
        'username': request.user.username,
        'source_stats': source_stats,
    }
    return render(request, 'profile.html', context)


@login_required
def my_logout_view(request):
    logout(request)
    return redirect('/')
