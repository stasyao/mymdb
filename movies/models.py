from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.aggregates import Sum


class PersonManager(models.Manager):
    """
    Кастомный менеджер для модели Person.
    """
    def all_with_prefetch_movies(self):
        qs = self.get_queryset()
        return qs.prefetch_related(
            'directed',  # директор фильма из Movie
            'scriptwriter',  # автор сценария фильма из Movie
            'role_set__movie',  # роль из Role в фильме из Movie
        )


class Person(models.Model):
    first_name = models.CharField(max_length=140)
    last_name = models.CharField(max_length=140)
    born = models.DateField()
    died = models.DateField(null=True, blank=True)

    objects = PersonManager()

    class Meta:
        ordering = ('last_name', 'first_name')

    def __str__(self):
        if self.died:
            return (
                f'{self.last_name}, {self.first_name} ({self.born}-{self.died})'
            )
        return f'{self.last_name}, {self.first_name} ({self.born})'


class MovieManager(models.Manager):
    def all_with_related_persons_and_movies(self):
        qs = self.get_queryset()
        qs = qs.select_related('director')  # связь один-ко-многим
        qs = qs.prefetch_related('writers', 'actors')  # связь многие-ко-многим
        return qs

    def all_with_related_persons_and_score(self):
        qs = self.all_with_related_persons_and_movies()
        qs = qs.annotate(score=Sum('vote__value'))
        return qs


class Movie(models.Model):
    title = models.CharField(max_length=140,)
    plot = models.TextField()
    year = models.PositiveSmallIntegerField()
    runtime = models.PositiveSmallIntegerField()
    website = models.URLField(blank=True)
    director = models.ForeignKey(
        to='Person',  # у одной картины может быть только один директор
        null=True,
        on_delete=models.SET_NULL,
        related_name='directed',  # алиас, через который можно посмотреть
        # для объекта Person
        blank=True,
    )
    writers = models.ManyToManyField(
        to='Person',
        related_name='scriptwriters',
        blank=True,)
    actors = models.ManyToManyField(
        to='Person',
        through='Role',
        related_name='acting_credits',
        blank=True,
    )

    objects = MovieManager()

    class Meta:
        ordering = ('-year', 'title')

    def __str__(self):
        return f'{self.title} ({self.year})'


class Role(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.DO_NOTHING)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=140)

    def __str__(self):
        return "{} {} {}".format(self.movie_id, self.person_id, self.name)

    class Meta:
        unique_together = ('movie', 'person', 'name')


class VoteManager(models.Manager):
    def get_vote_or_unsaved_blank_vote(self, movie, user):
        try:
            return Vote.objects.get(movie=movie, user=user, )
        except Vote.DoesNotExist:
            return Vote()


class Vote(models.Model):
    """
    Модель для подсчета голосов пользователей
    """
    UP = 1
    DOWN = -1
    VALUE_CHOICES = ((UP, "👍",), (DOWN, "👎",),)

    #  оценка
    value = models.SmallIntegerField(choices=VALUE_CHOICES,)
    #  проголосовавший юзер
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE,)
    #  фильм, за который отдан голос
    movie = models.ForeignKey(to=Movie, on_delete=models.CASCADE, )
    #  дата и время голосования
    voted_on = models.DateTimeField(auto_now=True,)

    objects = VoteManager()

    class Meta:
        unique_together = ('user', 'movie')
