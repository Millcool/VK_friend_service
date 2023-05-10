import logging

from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import FriendRequest, User, Friendship

"""Logger for every action with SQLite"""
logging.basicConfig(
    filename="views.log",
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
)


def get_context(user_id):
    """
    Получение всех нужных данных о пользователе для передачи на html страничку.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Словарь с данными о пользователе и его взаимодействиях с другими пользователями.
    """

    user = User.objects.get(id=user_id)
    friends = Friendship.objects.filter(user_id=user.id).values_list(
        "friend_id", flat=True
    )
    users = User.objects.all()

    requests_from_user = FriendRequest.objects.filter(from_user=user.id).values_list(
        "to_user", flat=True
    )
    requests_to_user = FriendRequest.objects.filter(to_user=user.id).values_list(
        "from_user", flat=True
    )
    context = {
        "user": user,
        "users": users,
        "friends": friends,
        "requests_to_user": requests_to_user,
        "requests_from_user": requests_from_user,
    }

    return context


def welcome_page(request):
    """
    Первая страница, на которую попадает пользователь.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона welcome_page.html.
    """

    if request.method == "GET":
        return render(request, "friends/welcome_page.html")


def log_in_user(request):
    """
    Контроллер для обработки запросов на вход пользователя.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона log_in_page.html или register_user.html.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            context = get_context(user.id)
            return render(request, "friends/user_page.html", context=context)

        return render(request, "friends/register_user.html")

    elif request.method == "GET":
        return render(request, "friends/log_in_page.html")


def register_user(request):
    """
    Страница для регистрации пользователя.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона register_user.html или user_already_exist.html.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        context = {"user": username}

        # Если пытается зарегистрироваться пользователь, который уже зарегистрирован
        if User.objects.filter(username=username).exists():
            # переадресация на страницу user_already_exist.html
            return render(request, "friends/user_already_exist.html", context=context)
        else:
            User.objects.create(username=username)
            return render(request, "friends/log_in_page.html", context=context)

    elif request.method == "GET":
        return render(request, "friends/register_user.html")


def user_page(request, user_id, friend_id=0):
    """
    Контроллер для основной страницы, на которой собрана вся информация о пользователе и его взаимоотношениях
    с другими пользователями.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.
        friend_id(int): Идентификатор друга.
    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона user_page.html.
    """

    if request.method == "POST":

        # Проверяем отправлял ли другой пользователь запрос на дружбу
        friend_request = FriendRequest.objects.filter(
            from_user=friend_id, to_user=user_id
        ).first()
        if friend_request:
            friend_request.accepted = True
            friend_request.save()

        logging.info(
            "Changed FriendRequest object from user: %d, to friend: %d",
            friend_id,
            user_id,
        )

        # Создаем заявку в друзья от user к friend
        FriendRequest.objects.create(
            from_user=user_id, to_user=friend_id, accepted=True
        )
        logging.info(
            "Created FriendRequest object from user: %d, to friend: %d",
            user_id,
            friend_id,
        )

        # Создаем записи о дружбе между пользователями
        Friendship.objects.create(user_id=user_id, friend_id=friend_id)
        Friendship.objects.create(user_id=friend_id, friend_id=user_id)

        logging.info(
            "Created Friendship object of user: %d, and friend: %d", user_id, friend_id
        )
        logging.info(
            "Created Friendship object of user: %d, and friend: %d", user_id, friend_id
        )

        # Если другой пользователь не отправлял запрос, то создаем заявку в друзья

        FriendRequest.objects.create(
            from_user=user_id, to_user=friend_id, accepted=False
        )
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)

    if request.method == "GET":
        # Проверяем отправлял ли другой пользователь запрос на дружбу
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def friend_list(request, user_id):
    """
    Контроллер для странички, отображающей всех друзей пользователя.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона friend_list.html.
    """

    if request.method == "GET":
        user = User.objects.get(id=user_id)
        friends = Friendship.objects.filter(user_id=user.id).values_list(
            "friend_id", flat=True
        )
        friends_of_user = User.objects.filter(id__in=friends)
        context = {"user": user, "friends": friends_of_user}
        return render(request, "friends/friend_list.html", context=context)


def friend_requests(request, user_id):
    """
    Контроллер для странички, отображающей все запросы в друзья от пользователей к user и от user к пользователям.

       Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона friend_requests.html.
    """

    if request.method == "GET":
        user = User.objects.get(id=user_id)
        requests_from_user = FriendRequest.objects.filter(
            from_user=user.id
        ).values_list("to_user", flat=True)
        requests_to_user = FriendRequest.objects.filter(to_user=user.id).values_list(
            "from_user", flat=True
        )
        users_requested_to_you = User.objects.filter(id__in=requests_to_user)
        users_requested_from_you = User.objects.filter(id__in=requests_from_user)
        context = {
            "user": user,
            "users_requested_to_you": users_requested_to_you,
            "users_requested_from_you": users_requested_from_you,
        }
        return render(request, "friends/friend_requests.html", context=context)


def withdraw(request, user_id, friend_id):
    """
    Контроллер для кнопки отзыва заявки в друзья пользователем.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.
        friend_id(int): Идентификатор друга.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона user_page.html.
    """

    if request.method == "POST":
        # Удаляем заявку в друзья
        friend_request = FriendRequest.objects.get(from_user=user_id, to_user=friend_id)
        friend_request.delete()
        logging.info(
            "Deleted friend_request from user: %d, to user: %d", user_id, friend_id
        )

        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def add_friend(request, user_id, friend_id, accepted):
    """
    Контроллер для добавления в друзья пользователя.

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.
        friend_id(int): Идентификатор друга.
        accepted(Bool): Показывает принят запрос или отклонен (1 - принят, 0 - отклонен)

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона user_page.html.
    """

    context = get_context(user_id)
    if request.method == "POST":
        #  Если пользователь принял заявку в друзья, то создаем в бд запись о их дружбе
        if accepted == 1:
            Friendship.objects.create(user_id=user_id, friend_id=friend_id)
            Friendship.objects.create(user_id=friend_id, friend_id=user_id)

            logging.info(
                "Created Friendship object of user: %d, and friend: %d",
                user_id,
                friend_id,
            )
            logging.info(
                "Created Friendship object of user: %d, and friend: %d",
                user_id,
                friend_id,
            )

            # Обновляем friend_request на True
            friend_request = FriendRequest.objects.get(
                from_user=friend_id, to_user=user_id
            )
            friend_request.accepted = True
            friend_request.save()
            logging.info(
                "Changed FriendReuest object of user: %d, to friend: %d to %s",
                user_id,
                friend_id,
                "True",
            )

        # Если заявку отклонили, то удаляем запись о посланнй заявке
        elif accepted == 0:
            friend_request = FriendRequest.objects.get(
                from_user=friend_id, to_user=user_id
            )
            friend_request.delete()
            logging.info(
                "Deleted FriendRequest object of user: %d, to user: %d",
                user_id,
                friend_id,
            )

        return render(request, "friends/user_page.html", context=context)

    elif request.method == "GET":
        return render(request, "friends/user_page.html", context=context)


def remove_friend(request, user_id, friend_id):
    """
    Контроллер для кнопки удаления друга

    Args:
        request (django.http.HttpRequest): Объект запроса HTTP.
        user_id (int): Идентификатор пользователя.
        friend_id(int): Идентификатор друга.

    Returns:
        django.http.HttpResponse: HTTP-ответ с рендерингом шаблона user_page.html.
    """


    if request.method == "POST":
        # Удаляем друга с user_id friend_id
        friend_request = Friendship.objects.get(user_id=user_id, friend_id=friend_id)
        friend_request.delete()
        logging.info(
            "Deleted Friendship object of user: %d, and friend: %d", user_id, friend_id
        )

        # Удаляем поле друга с friend_id user_id
        friend_request = Friendship.objects.get(user_id=friend_id, friend_id=user_id)
        friend_request.delete()
        logging.info(
            "Deleted Friendship object of user: %d, and friend: %d", friend_id, user_id
        )

        # Делаем accepted для заявки от бывшего друга False
        friend_request = FriendRequest.objects.filter(
            from_user=friend_id, to_user=user_id
        ).first()
        if friend_request:
            friend_request.accepted = False
            friend_request.save()
            logging.info(
                "Changed Friendship object of user: %d, and friend: %d to %s",
                user_id,
                friend_id,
                "False",
            )

        # Нужно удалить заявку в друзья от user_id
        else:
            friend_request = FriendRequest.objects.filter(
                from_user=user_id, to_user=friend_id
            ).first()
            if friend_request:
                friend_request.delete()
                logging.info(
                    "Deleted Friendship object of user: %d, and friend: %d",
                    user_id,
                    friend_id,
                )
        context = get_context(user_id)
        return render(request, "friends/user_page.html", context=context)


def page_not_found(request, exeption):
    """Если страница не найдена (404)"""

    if request.method == "GET":
        return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def server_error(request):
    """Если ошибка сервера (500)"""

    if request.method == "GET":
        return HttpResponseNotFound("<h1>Ошибка сервера</h1>")
