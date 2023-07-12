from django.db.models import (
    ForeignKey,
    Model,
    EmailField,
    CharField,
    CASCADE,
    DateTimeField,
    Q,
    F,
    UniqueConstraint,
    CheckConstraint
)
from django.contrib.auth.models import AbstractUser
from core import constants as const


class CustomUser(AbstractUser):
    email = EmailField(
        verbose_name='Email',
        max_length=const.EMAIL_LIMIT,
        unique=True
    )
    username = CharField(
        verbose_name='Username',
        max_length=const.USERNAME_LIMIT,
        unique=True
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=const.FIRST_NAME_LIMIT
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=const.LAST_NAME_LIMIT
    )
    password = CharField(
        verbose_name='Пароль',
        max_length=const.PASSWORD_LIMIT
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscription(Model):
    author = ForeignKey(
        verbose_name='Автор',
        related_name='recipe_author',
        to=CustomUser,
        on_delete=CASCADE
    )
    subscriber = ForeignKey(
        verbose_name='Подписчик',
        related_name='author_subscriber',
        to=CustomUser,
        on_delete=CASCADE
    )
    creation_date = DateTimeField(
        verbose_name='Время создания подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'subscriber'),
                name='Repeat subscription',
            ),
            CheckConstraint(
                check=~Q(author=F('subscriber')), name='No self subscription'
            ),
        )

    def __str__(self) -> str:
        return f'{self.subscriber.username} -> {self.author.username}'
