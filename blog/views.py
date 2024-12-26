from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag
from django.urls import reverse
from django.core.paginator import Paginator

class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'blog/post_list.html'
    context_object_name = 'products'
    paginate_by = 6  # 한 페이지에 표시할 게시물 수

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = get_object_or_404(Category, slug=slug)
        post_list = Post.objects.filter(category=category)

    paginator = Paginator(post_list, 6)  # 한 페이지에 6개의 게시물 표시
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)

    return render(
        request,
        'blog/post_list.html',
        {
            'products': posts,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )

def tag_page(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    post_list = tag.post_set.all()

    paginator = Paginator(post_list, 6)  # 한 페이지에 6개의 게시물 표시
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)

    return render(
        request,
        'blog/post_list.html',
        {
            'products': posts,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['add_cart_url'] = reverse('cart:add_cart', args=[self.object.id])
        return context
