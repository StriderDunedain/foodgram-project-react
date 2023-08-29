from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, Model, Q, UniqueConstraint)

from core import constants as const


class User(AbstractUser):
    REQUIRED_FIELDS = ('first_name', 'last_name', 'password', 'username')
    USERNAME_FIELD = 'email'

    username = CharField(
        max_length=const.USERNAME_LIMIT,
        unique=True
    )
    email = EmailField(
        max_length=const.EMAIL_LIMIT,
        unique=True
    )

    first_name = CharField(
        max_length=const.FIRST_NAME_LIMIT
    )
    last_name = CharField(
        max_length=const.LAST_NAME_LIMIT
    )

    password = CharField(
        max_length=const.PASSWORD_LIMIT,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(Model):
    author = ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=CASCADE
    )
    subscriber = ForeignKey(
        User,
        related_name='subscriber',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=(
                    'author',
                    'subscriber'
                ),
                name='author_subscriber_constraint'
            ),
            CheckConstraint(
                check=~Q(
                    subscriber=F('author')
                ),
                name='Self-subscription not allowed here, boi'
            )
        )
