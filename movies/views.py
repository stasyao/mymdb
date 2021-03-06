from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import VoteForm
from .models import Movie, Person, Vote


class MovieList(ListView):
    model = Movie
    paginate_by = 10


class CreateVote(LoginRequiredMixin, CreateView):
    """
    Проголосовать впервые.
    """
    #  Указываем форму, которую будет использовать контроллер
    form_class = VoteForm

    #  Переопределяем метод, отвечающий за изначальное заполнение формы
    def get_initial(self):
        #  Получаем пустой словарь
        initial = super().get_initial()
        #  Добавляем ключ-значение поля user
        initial['user'] = self.request.user.id
        #  Добавляем ключ-значение поля movie
        initial['movie'] = self.kwargs['movie_id']
        return initial

    #  Если кто-то соберется сделать get-запрос на /vote
    #  Будет перенаправлен на страницу с фильмом
    def render_to_response(self, context, **response_kwargs):
        movie_id = self.kwargs['movie_id']
        movie_detail_url = reverse(
            'movies:MovieDetail',
            kwargs={'pk': movie_id})
        return redirect(to=movie_detail_url)

    def get_success_url(self):
        #  Вернуть на ту же страницу, где и фильм
        movie_id = self.object.movie.id
        return reverse('movies:MovieDetail', kwargs={'pk': movie_id})


class UpdateVote(LoginRequiredMixin, UpdateView):
    """
    Обновить свой голос.
    """
    form_class = VoteForm
    queryset = Vote.objects.all()

    def get_object(self, queryset=None):
        vote = super().get_object(queryset)
        #  Дополняем извлечение записи о голосе проверкой на авторство
        if vote.user != self.request.user:
            raise PermissionDenied('Нельзя проголосовать за другого')
        return vote

    def render_to_response(self, context, **response_kwargs):
        #  Чтобы не ломать прямой GET-запрос из-за отсутствия шаблона
        movie_id = context['object'].id
        movie_detail_url = reverse(
            'movies:MovieDetail',
            kwargs={'pk': movie_id}
        )
        return redirect(to=movie_detail_url)

    def get_success_url(self):
        #  Вернуть на ту же страницу, где и фильм
        movie_id = self.object.movie.id
        return reverse('movies:MovieDetail', kwargs={'pk': movie_id})


class MovieDetail(DetailView):
    queryset = Movie.objects.all_with_related_persons_and_score()

    def get_context_data(self, **kwargs):
        #  Получили дефолтный контекст
        #  Словарь из object, movie, view
        ctx = super().get_context_data(**kwargs)
        #  Если пользователь авторизован
        if self.request.user.is_authenticated:
            #  Вернуть запись об оценке, если она уже была
            #  Создать ОБЪЕКТ "новая оценка" (ещё НЕ запись)
            vote = Vote.objects.get_vote_or_unsaved_blank_vote(
                movie=self.object,
                user=self.request.user
            )

            if vote.id:
                #  получаем эндпоинт для ОБНОВЛЕНИЯ своего голоса
                vote_form_url = reverse(
                    'movies:UpdateVote',
                    kwargs={
                        'movie_id': vote.movie.id,
                        'pk': vote.id
                    }
                )
            #  если же текущий пользователь ещё НЕ голосовал за фильм
            else:
                #  получаем адрес ресурса для НОВОГО голоса
                vote_form_url = reverse(
                        'movies:CreateVote',
                        kwargs={
                            'movie_id': self.object.id
                        }
                    )
            #  Если никогда не голосовал - пустая форма
            #  Суть пустой формы: юзер и фильм есть, но они скрыты
            #  Если голосовал ранее - форма отображается с предвыбранным
            #  голосом
            vote_form = VoteForm(instance=vote)

            #  Добавляем в контекст новые переменные
            ctx['vote_form'] = vote_form
            ctx['vote_form_url'] = vote_form_url
        return ctx


class PersonDetail(DetailView):
    queryset = Person.objects.all_with_prefetch_movies()
