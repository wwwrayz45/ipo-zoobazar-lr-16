from django.http import HttpResponse


def home(request):
    return HttpResponse("""
    <h1>Zoobazar</h1>
    <a href="/author/">Об авторе</a><br>
    <a href="/shop/">О магазине</a>
    """)


def author(request):
    return HttpResponse("""
    Автор лабораторной работы: Будько Дарья<br>
    Учебная группа: 87 ТП
    """)


def shop_info(request):
    return HttpResponse("""
    <h2>О магазине Zoobazar</h2>

    <p>
    Zoobazar — сеть зоомагазинов в Беларуси.
    </p>

    <p>
    Тема лабораторной работы: Создание веб-приложения на Django для управления функционалом магазина.
    </p>

    <h3>На сайте магазина представлены:</h3>

    <ul>
        <li>Корма для животных</li>
        <li>Игрушки</li>
        <li>Аксессуары</li>
        <li>Ветеринарные товары</li>
        <li>Товары для собак, кошек, птиц и грызунов</li>
    </ul>
    """)