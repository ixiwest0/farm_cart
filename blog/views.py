from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag
from django.urls import reverse

# def allProdCat(request, c_slug=None):
#     c_page = None;
#     products = None;
#     if c_slug != None:
#         c_page = get_object_or_404(Category, slug=c_slug)
#         products = Post.objects.filter(category=c_page, available=True)
#     else:
#         products = Post.objects.all().filter(available=True)
#     return render(request, 'blog/post_list.html',{'category':c_page, 'products':products})




class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
 'blog/post_list.html',
         {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
            }
        )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
    {
        'post_list':post_list,
        'tag': tag,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count(),
    }
)


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['add_cart_url'] = reverse('cart:add_cart', args=[self.object.id])
        return context
