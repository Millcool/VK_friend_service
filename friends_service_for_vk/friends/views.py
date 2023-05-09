import logging

from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import FriendRequest, User, Friendship

logging.basicConfig(
    filename="views.log",
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s"
)


def get_context(user_id):
    """Получение всех нужных данных о пользователе для передачи на html страничку"""

    user = User.objects.get(id=user_id)
    friends = Friendship.objects.filter(user_id=user.id).values_list('friend_id', flat=True)
    users = User.objects.all()
    requests_from_user = FriendRequest.objects.filter(from_user=user.id).values_list('to_user', flat=True)
    requests_to_user = FriendRequest.objects.filter(to_user=user.id).values_list('from_user', flat=True)
    print(f'Users: {users}, '
          f'friends: {friends},'
          f' username = {user.username},'
          f'request_to_user = {requests_to_user},'
          f' request_from_user = {requests_from_user} ')

    context = {'user': user, 'users': users, 'friends': friends, "requests_to_user": requests_to_user,
               "requests_from_user": requests_from_user, }

    return context


# Контроллеры для нашего сайта
def welcome_page(request):
    return render(request, 'friends/welcome_page.html')


def log_in_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            context = get_context(user.id)
            return render(request, 'friends/user_page.html', context=context)
        else:
            return render(request, 'friends/register_user.html')

    elif request.method == 'GET':
        return render(request, 'friends/log_in_page.html')


def register_user(request):
    print(request.method)
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        context = {'user': username}
        if User.objects.filter(username=username).exists():
            # ответ в виде строки 'User already exists'
            return render(request, "friends/user_already_exist.html", context=context)
        else:
            user = User.objects.create(username=username)
            return render(request, "friends/log_in_page.html", context=context)

    elif request.method == 'GET':
        return render(request, 'friends/register_user.html')



def user_page(request, user_id, friend_id=0):
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        # Проверяем отправлял ли другой пользователь запрос на дружбу
        FriendRequest.objects.create(from_user=user_id, to_user=friend_id, accepted=False)
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)

    if request.method == 'GET':
        user = User.objects.get(id=user_id)
        # Проверяем отправлял ли другой пользователь запрос на дружбу
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def friend_list(request, user_id):
    user = User.objects.get(id=user_id)
    friends = Friendship.objects.filter(user_id=user.id).values_list('friend_id', flat=True)
    friends_of_user = User.objects.filter(id__in=friends)
    context = {'user': user,  'friends': friends_of_user }
    return render(request, "friends/friend_list.html", context=context)

def friend_requests(request, user_id):
    user = User.objects.get(id=user_id)
    requests_from_user = FriendRequest.objects.filter(from_user=user.id).values_list('to_user', flat=True)
    requests_to_user = FriendRequest.objects.filter(to_user=user.id).values_list('from_user', flat=True)
    users_requested_to_you = User.objects.filter(id__in=requests_to_user)
    users_requested_from_you = User.objects.filter(id__in=requests_from_user)
    context = {'user': user, 'users_requested_to_you': users_requested_to_you, 'users_requested_from_you':users_requested_from_you}
    return render(request, "friends/friend_requests.html", context=context)


def withdraw(request, user_id, friend_id):
    if request.method == 'POST':
        # Удаляем заявку в друзья
        friend_request = FriendRequest.objects.get(from_user=user_id, to_user=friend_id)
        friend_request.delete()
        logging.info("Deleted friend_request from user: %d, to user: %d", user_id, friend_id)

        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def add_friend(request, user_id, friend_id, accepted):
    context = get_context(user_id)
    if request.method == 'POST':

        #  Если пользователь принял заявку в друзья, то создаем в бд запись о их дружбе
        if accepted == 1:
            Friendship.objects.create(user_id=user_id, friend_id=friend_id)
            Friendship.objects.create(user_id=friend_id, friend_id=user_id)

            logging.info("Created Friendship object of user: %d, and friend: %d", user_id, friend_id)
            logging.info("Created Friendship object of user: %d, and friend: %d", user_id, friend_id)


            # Обновляем friend_request на True
            friend_request = FriendRequest.objects.get(from_user=friend_id, to_user=user_id)
            friend_request.accepted = True
            friend_request.save()
            logging.info("Changed FriendReuest object of user: %d, to friend: %d to %s", user_id, friend_id, "True")

        # Если заявку отклонили, то удаляем запись о посланнй заявке
        elif accepted == 0:
            friend_request = FriendRequest.objects.get(from_user=friend_id, to_user=user_id)
            friend_request.delete()
            logging.info("Deleted FriendRequest object of user: %d, to user: %d", user_id, friend_id)

        return render(request, "friends/user_page.html", context=context)

    elif request.method == 'GET':
        return render(request, "friends/user_page.html", context=context)


def remove_friend(request, user_id, friend_id):
    if request.method == 'POST':

        # Удаляем друга
        friend_request = Friendship.objects.get(user_id=user_id, friend_id=friend_id)
        friend_request.delete()
        logging.info("Deleted Friendship object of user: %d, and friend: %d", user_id, friend_id)

        # Делаем accepted для заявки от бывшего друга False
        friend_request = FriendRequest.objects.filter(from_user=friend_id, to_user=user_id).first()
        if friend_request:
            friend_request.accepted = False
            friend_request.save()
            logging.info("Changed Friendship object of user: %d, and friend: %d to %s", user_id, friend_id, "False")
        # Нужно удалить нашу заявку в друзья
        else:
            friend_request = FriendRequest.objects.filter(from_user=user_id, to_user=friend_id).first()
            if friend_request:
                friend_request.delete()
                logging.info("Deleted Friendship object of user: %d, and friend: %d", user_id, friend_id)
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def pageNotFound(request, exeption):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def ServerError(request):
    return HttpResponseNotFound('<h1>Ошибка сервера</h1>')
