from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from . import models
from .models import Note


# 装饰器，判断是否登录，可以节省很多重复代码
def check_login(fn):
    def wrap(request, *args, **kwargs):
        if 'username' not in request.session or 'uid' not in request.session:
            # 没在session就检查Cookies
            c_username = request.COOKIES.get('username')
            c_uid = request.COOKIES.get('uid')
            # 没在cookies就说明没登录，跳转
            if not c_username or not c_uid:
                return HttpResponseRedirect('/user/login')
            else:
                # 回写session
                request.session['username '] = c_username
                request.session['uid'] = c_uid
        return fn(request, *args, **kwargs)

    return wrap


# Create your views here.
@check_login
def add_note(request):
    if request.method == 'GET':
        return render(request, 'note/add_note.html')
    elif request.method == 'POST':
        # 处理数据
        title = request.POST.get('title')
        content = request.POST.get('content')
        uid = request.session.get('uid')  # 这里如果用cookies行不行？
        models.Note.objects.create(title=title, content=content, user_id=uid)
        return HttpResponseRedirect('/note/list')


@check_login
def list_view(request):
    all_notes = Note.objects.all()
    return render(request, 'note/note_list.html', locals())


@check_login
def update_note(request, note_id):
    # 怎么知道当前要更新的是谁？
    try:
        note = Note.objects.get(id=note_id)
    except Exception as e:
        print('笔记获取失败', e)
    if request.method == 'GET':
        return render(request, 'note/update_note.html', locals())
    if request.method == 'POST':
        new_title = request.POST.get('title')
        new_content = request.POST.get('content')
        note.title = new_title
        note.content = new_content
        note.save()
        return HttpResponseRedirect('/note/list')
