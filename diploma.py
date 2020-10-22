import requests
from urllib.parse import urljoin
import os
import tqdm
import datetime
import json


VK_TOKEN = ''
VKAPI_BASE_URL = 'http://api.vk.com/method/'
V = '5.21'
YANDEX_TOKEN = ''
YANDEX_FOLDER_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
YANDEX_API_URL = 'https://cloud-api.yandex.net/v1/disk/resources/upload'


def get_vk_photos(user_id, count=5, album_id='profile'):
    photos_get_url = urljoin(VKAPI_BASE_URL, 'photos.get')
    response = requests.get(photos_get_url, params={
        'access_token': VK_TOKEN,
        'v': V,
        'owner_id': user_id,
        'album_id': album_id,
        'extended': 1,
        'count': count,
        'rev': 1,
        'photo_sizes': 1
    })
    all_photos = response.json()['response']['items']
    save_vk_photos(all_photos)
    return all_photos


def save_vk_photos(all_photo):
    folder_name = create_yadisk_folder()

    new_all_photo = []
    url = ''
    data_for_json = []
    size = ''
    titles_list = []

    for photo in all_photo:
        temp_dict = {
            'date': photo['date'],
            'likes': photo['likes']['count']
        }
        for pic in photo['sizes']:
            temp_dict[pic['type']] = [pic['src'], pic['width'], pic['height']]
        new_all_photo.append(temp_dict)

    for elm in tqdm.tqdm(new_all_photo):
        if 'w' in elm.keys():
            url = elm['w'][0]
            size = 'w'
        elif 'z' in elm.keys():
            url = elm['z'][0]
            size = 'z'
        elif 'y' in elm.keys():
            url = elm['y'][0]
            size = 'y'
        elif 'x' in elm.keys():
            url = elm['x'][0]
            size = 'x'
        elif 'r' in elm.keys():
            url = elm['r'][0]
            size = 'r'
        elif 'q' in elm.keys():
            url = elm['q'][0]
            size = 'q'
        elif 'p' in elm.keys():
            url = elm['p'][0]
            size = 'p'
        elif 'o' in elm.keys():
            url = elm['o'][0]
            size = 'o'
        elif 'm' in elm.keys():
            url = elm['m'][0]
            size = 'm'
        elif 's' in elm.keys():
            url = elm['s'][0]
            size = 's'
        unix_date = datetime.datetime.fromtimestamp(elm['date'])
        normal_date = unix_date.strftime('%Y%m%d')
        title = str(elm['likes']) + os.path.splitext(url)[1]
        if title in titles_list:
            title = str(elm['likes']) + '_' + normal_date + os.path.splitext(url)[1]
        titles_list.append(title)
        create_yadisk_file(url, title, folder_name)
        data_for_json.append({'file_name': title, 'size': size})
    print(f'Фотографии загружены в папку {folder_name}')
    create_json_file(data_for_json, folder_name)
    return data_for_json


def create_yadisk_folder():
    folder_name = datetime.datetime.now().strftime('%H-%M-%S_%d-%m-%Y')
    headers = {'Authorization': YANDEX_TOKEN}
    params = {'path': folder_name}
    requests.put(YANDEX_FOLDER_URL, params=params, headers=headers)
    return folder_name


def create_yadisk_file(file_url, file_title, folder_name):
    headers = {'Authorization': YANDEX_TOKEN}
    file_name = folder_name + '/' + file_title
    params = {
        'url': file_url,
        'path': file_name,
        'overwrite': 'false'
    }
    response = requests.post(YANDEX_API_URL, params=params, headers=headers)
    return response


def create_json_file(json_data, path):
    json_file_name = path + '.json'
    with open(json_file_name, 'w') as f:
        json.dump(json_data, f, indent=2)
    headers = {'Authorization': YANDEX_TOKEN}
    params = {
        'path': path + '/' + json_file_name,
        'overwrite': 'true'
    }
    response1 = requests.get(YANDEX_API_URL, params=params, headers=headers)
    url2 = response1.json()['href']
    with open(json_file_name, 'rb') as f:
        files = {'file': f}
        requests.put(url2, files=files)
    os.remove(json_file_name)
    print(f'Информация по загруженным фотографиям  {json_file_name}')
    return json_file_name


if __name__ == '__main__':
    vk_user_id = '2359003'
    get_vk_photos(vk_user_id, 20, 'wall')
