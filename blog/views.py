from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from blog import models
import json, time
from apple_blog import settings
from blog import forms
from blog.models import UserInfo
from blog.models import Blog
from blog.models import Article, ArticleDetail, Comment, CommentUp, Tag, Article2Tag
from blog.models import Category, ArticleUpDown
from django.db.models import F, Q
from datetime import *

# Create your views here.


def reg(request):
    ret = {"flag": False, "error": None}
    '''
    flag 标志位,error 错误字典
    '''

    if request.method == "POST":
        form_obj = forms.RegForm(request, request.POST)
        '''
        将注册页面取出的值赋给实例化的RegForm表单 
        '''

        if form_obj.is_valid():
            '''
            判断前端输入的值是否合法,如果合法,创建新用户 
            '''
            username = form_obj.cleaned_data["username"]
            password = form_obj.cleaned_data["password"]
            email = form_obj.cleaned_data["email"]
            file_obj = request.FILES.get("img")

            print(file_obj)

            UserInfo.objects.create_user(username=username, password=password, email=email, avatar=file_obj)

        else:
            '''
            如果信息不合法,取出错误信息,并把标志位 flag 改为TRUE,并把错误信息赋给 ret["error"]
            '''
            errors = form_obj.errors

            print("errors:-----", errors)

            ret["flag"] = True
            ret["error"] = errors
        return HttpResponse(json.dumps(ret))

    form_obj = forms.RegForm()
    return render(request, "reg.html", {"form_obj": form_obj})


def index(request, **kwargs):

    type_choices = models.Article.type_choices
    current_type_choices_id = int(kwargs.get("article_type_id", 0))
    article_list = models.Article.objects.all()
    print(article_list)
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    p_obj = Paginator(article_list, 5)
    page_num = request.GET.get("page")
    try:
        book_list = p_obj.page(page_num)
    except EmptyPage:
        book_list = p_obj.page(p_obj.num_pages)
    except PageNotAnInteger:
        book_list = p_obj.page(1)

    return render(request, "index.html", {"type_choices": type_choices,
                                          "current_type_choices_id": current_type_choices_id,
                                          "article_list": article_list,
                                          "book_list": book_list,
                                          "p_obj": p_obj})


def log_in(request):
    ret = {"flag": False, "error": None}
    re_url = request.path

    re_url = re_url.replace("/login", "")
    print(re_url)

    if request.method == "POST":
        print(request.session["valid_code"])

        if request.session["valid_code"].upper() == request.POST.get("valid_code").upper():
            user = auth.authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
            if user:
                auth.login(request, user)
            else:
                ret["flag"] = True
                ret["error"] = "账号或密码错误"
        else:
            ret["flag"] = True
            ret["error"] = "验证码错误"

        return HttpResponse(json.dumps(ret))

    return render(request, "login.html", {"re_url": re_url})


def valid_code(request):
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    import random
    f = BytesIO()
    img = Image.new(mode='RGB', size=(120, 30), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(img, mode='RGB')
    font = ImageFont.truetype("blog/static/bootstrap/fonts/kumo.ttf", 28)
    code_list = []
    for i in range(5):
        char = random.choice([chr(random.randint(65, 90)), str(random.randint(1, 9))])
        code_list.append(char)
        draw.text([i * 24, 0], char, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                  font=font)

    img.save(f, "png")

    valid_code = ''.join(code_list)

    request.session["valid_code"] = valid_code

    return HttpResponse(f.getvalue())


def func_class(request):
    return {"func": settings.FUNCTION}


def log_out(request):

    auth.logout(request)# 清除的是当前用户的session记录

    return redirect("/login/")


def blog(request, **kwargs):
    username = kwargs.get("username", 0)
    user_obj = UserInfo.objects.filter(username=username).first()
    blog_obj = user_obj.blog
    article_list = Article.objects.filter(blog=blog_obj)
    article_num = Article.objects.filter(blog=blog_obj).count()#文章总数

    category_list = Category.objects.filter(blog=blog_obj)#文章分类的列表
    from django.db.models import Avg, Sum, Min, Max, Count

    categoryRet = Article.objects.filter(blog=blog_obj).values_list("category__title", "category__nid").annotate(Count("nid"))

    tagRet=article_list.values_list("tags__title", "tags__nid").annotate(Count("nid"))
    # print(tagRet)
    dateRet = Article.objects.archive(blog=blog_obj)

    if kwargs.get("condition"):

        con = kwargs.get("condition")

        if con == "category":

            article_list = Article.objects.filter(blog=blog_obj, category_id=kwargs.get("para"))

        elif con == "tag":

            article_list = Article.objects.filter(blog=blog_obj, tags=kwargs.get("para"))

        elif con == "date":
            article_list = []
            for i in blog_obj.article_set.all():

                if kwargs.get("para") == i.create_time.strftime("%Y-%m"):
                    article_list.append(i)
                else:
                    pass

    return render(request, "blog.html", locals())


def blog_text(request, **kwargs):
    username = kwargs.get("username", 0)

    article_id = kwargs.get("article_id", 0)

    user_obj = UserInfo.objects.filter(username=username).first()

    blog_obj = user_obj.blog

    article_list = Article.objects.filter(blog=blog_obj)

    article_num = Article.objects.filter(blog=blog_obj).count()  # 文章总数

    category_list = Category.objects.filter(blog=blog_obj)  # 文章分类的列表

    from django.db.models import Avg, Sum, Min, Max, Count

    categoryRet = Article.objects.filter(blog=blog_obj).values_list("category__title", "category__nid").annotate(Count("nid"))
    print("categoryRetcategoryRetcategoryRetcategoryRetcategoryRet", categoryRet)
    tagRet = article_list.values_list("tags__title", "tags__nid").annotate(Count("nid"))

    dateRet = Article.objects.archive(blog=blog_obj)

    article_obj = Article.objects.filter(nid=article_id).first()

    articledetail_obj = ArticleDetail.objects.filter(article=article_obj).first()

    coment_list = Comment.objects.filter(article_id=article_id)

    return render(request, "blog_text.html", locals())


def poll(request):
    user_id = request.user.nid
    ret = {"flag": True}

    article_id = request.POST.get("article_id")

    coment_nid = request.POST.get("coment_nid")

    if article_id:

        if ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id):
            ret["flag"] = False

        else:
            ArticleUpDown.objects.create(user_id=user_id, article_id=article_id)
            Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
    else:

        if CommentUp.objects.filter(user_id=user_id, comment_id=coment_nid):
            ret["flag"] = False

        else:
            CommentUp.objects.create(user_id=user_id, comment_id=coment_nid)
            Comment.objects.filter(nid=coment_nid).update(up_count=F("up_count") + 1)

    return HttpResponse(json.dumps(ret))


def comment(request):
    comment_dic = {"flag": True}
    user_id = request.user.nid
    article_id = request.POST.get("article_id")
    comment_content = request.POST.get("comment_content")
    parent_id = request.POST.get("parent_id")

    if not comment_content:

        comment_dic["flag"] = False

    else:
        if parent_id == "a":

            comment_obj = Comment.objects.create(article_id=article_id, content=comment_content, user_id=user_id)
            Article.objects.filter(nid=article_id).update(comment_count=F("comment_count") + 1)

            comment_dic["username"] = comment_obj.user.username
            comment_dic["content"] = comment_obj.content
            comment_dic["nid"] = comment_obj.nid
            time_obj = comment_obj.create_time

            comment_dic["create_time"] = time_obj.strftime("%Y-%m-%d %H:%M")

        else:
            comment_obj = Comment.objects.create(article_id=article_id, parent_id_id=parent_id, content=comment_content, user_id=user_id)
            Article.objects.filter(nid=article_id).update(comment_count=F("comment_count") + 1)
            parent_comment_obj = Comment.objects.filter(nid=parent_id).first()

            comment_dic["username"] = comment_obj.user.username
            comment_dic["content"] = comment_obj.content
            comment_dic["nid"] = comment_obj.nid
            time_obj = comment_obj.create_time
            comment_dic["create_time"] = time_obj.strftime("%Y-%m-%d %H:%M")
            comment_dic["parent_name"] = UserInfo.objects.filter(nid=parent_comment_obj.user_id).first().username
            comment_dic["parent_content"] = parent_comment_obj.content

    return HttpResponse(json.dumps(comment_dic))


def postlist(request):

    re_url = request.path

    if request.user.is_authenticated():
        user_nid = request.user.nid
        user_obj = UserInfo.objects.filter(nid=user_nid).first()

        article_list = Article.objects.filter(blog=user_obj.blog).all()

        return render(request, "postlist.html", {"article_list": article_list, "user_obj": user_obj})

    else:
        return render(request, "login.html", {"re_url": re_url})


def addArticle(request):

    if request.method == "POST":

        user_nid = request.user.nid

        user_obj = UserInfo.objects.filter(nid=user_nid).first()
        blog_obj = user_obj.blog
        type_choices = request.POST.get("type_choices")

        title = request.POST.get("title")

        category_nid = request.POST.get("category")
        category_obj = Category.objects.filter(nid=category_nid).first()

        article_content = request.POST.get("article_content")

        tag_list = request.POST.getlist("tag_list")

        desc = request.POST.get("desc")

        article_obj = Article.objects.create(title=title, desc=desc, category=category_obj, blog=blog_obj, article_type_id=type_choices)

        for tag_nid in tag_list:

            tag_obj = Tag.objects.filter(nid=tag_nid).first()
            Article2Tag.objects.create(article=article_obj, tag=tag_obj)

        ArticleDetail.objects.create(content=article_content, article=article_obj)

        return redirect("/postlist/")

    re_url = request.path

    if request.user.is_authenticated():

        user_nid = request.user.nid

        type_choices = models.Article.type_choices

        user_obj = UserInfo.objects.filter(nid=user_nid).first()

        dt = datetime.now()

        blog_obj = user_obj.blog

        category_list = blog_obj.category_set.all()

        tag_list = blog_obj.tag_set.all()

        return render(request, "addArticle.html", {"user_obj": user_obj,
                                                   "type_choices": type_choices,
                                                   "category_list": category_list,
                                                   "tag_list": tag_list,
                                                   "dt": dt})

    else:
        return render(request, "login.html", {"re_url": re_url})


def upload_file(request):

    file_obj = request.FILES.get("imgFile")
    filename = file_obj.name
    with open("blog/media/upload/img/"+filename, "wb") as f:

        for chunk in file_obj.chunks():

            f.write(chunk)

    response_put = {
        "error": 0,
        "url": "/media/upload/img/"+filename
    }

    return HttpResponse(json.dumps(response_put))

