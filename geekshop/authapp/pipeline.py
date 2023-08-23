from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse

import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden
from .models import ShopUserProfile
from .models import ShopUser


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return
    api_url = urlunparse(('https',
                          'api.vk.com',
                          '/method/users.get',
                          None,
                          urlencode(OrderedDict(fields=','.join(('bdate', 'sex',
                                                                 'about', 'domain',
                                                                 'site', 'interests',
                                                                 'lang', 'photo_100')),
                                                access_token=response['access_token'], v='5.92')),
                          None
                          ))

    resp = requests.get(api_url)

    #  проверяем ответ от request
    if resp.status_code != 200:
        return

    # если все ок, то продолжаем
    data = resp.json()['response'][0]
    print(data)
    if data['sex']:
        user.shopuserprofile.gender = ShopUserProfile.MALE if data['sex'] == 2 else ShopUserProfile.FEMALE
    url_vk = ''

    # ссылка на социальную сеть по заданию №5
    if data['domain']:
        url_vk = ''.join(['https://vk.com/', data['domain']])
        user.shopuserprofile.my_social_page = url_vk

    if data['about']:
        # ссылку на страницу выведем в поле "о себе"
        user.shopuserprofile.aboutMe = data['about'] + '\n'+ url_vk

    if data['bdate']:
        bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()
        age = timezone.now().date().year - bdate.year
        user.age = age
        print(user.age)
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.vk.VKOAuth2')

    if data['interests']:
        tagline = data['interests']
        user.shopuserprofile.tagline = tagline




    user.save()
