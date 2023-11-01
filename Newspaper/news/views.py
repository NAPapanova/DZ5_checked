from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.views import generic
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, TemplateView #Позволяет выводить объекты из базы данных в html
from django.views.generic.edit import FormView
from .forms import LoginForm, RegisterForm
#from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from news.models import Post
from Newspaper.news.search import PostFilter # импортируем недавно написанный фильтр



class NewsList(generic.ListView):
    """Представление главной страницы, которая отображает список всех новостей"""
    model = Post
    context_object_name = 'posts'
    template_name = 'tempates/flatpages/news_page.html'
    queryset = Post.objects.all().order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs): # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
       context = super().get_context_data(**kwargs)
       context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) # вписываем наш фильтр в контекст
       return context
    
    def post(self, request, *args, **kwargs):
       # берём значения для нового продукта из POST-запроса, отправленного на сервер
       title = request.POST['title']
       text = request.POST['text']
       category = request.POST['category']
       preview = request.POST['preview']
       post = Post(title=title, preview=preview, category=category, text=text) # создаём новый продукт и сохраняем
       post.save()
       return super().get(request, *args, **kwargs) # отправляем пользователя обратно на GET-запрос


class PostDetail(DetailView):
    model = Post
    template_name = 'tempates/news_templates/post_detail.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

class Posts(View):
    def get(self, request):
        posts = Post.objects.order_by('-dateCreation')
        p = Paginator(posts,10)
        posts = p.get_page(request.GET.get('page', 1))
        data = {
            'posts': posts,
        }
        return render(request, 'news/news_page.html', data)

class PostCreateView(CreateView):
   template_name = 'tempates/news_templates/product_create.html'
   #form_class = PostForm

class PostUpdateView(UpdateView):
    template_name = 'fastfood/product_create.html'
   #form_class = PostForm

   # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)

class PostDeleteView(DeleteView):
   template_name = 'proj/templates/news_templates/post_delete.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:post') # не забываем импортировать функцию reverse_lazy из пакета django.urls



class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect.html'




class ProtectedView(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
    template_name = 'post_create.html'
    permission_required = ('<news>.<create>_<post>',
                           '<news>.<delete>_<post>',
                           '<news>.<edit>_<post>')