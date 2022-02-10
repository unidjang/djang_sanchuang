import hashlib
import json
from django.http import JsonResponse
from jwt import exceptions
import jwt
from .models import User  # 用来进行数据库操作


# 注册（跟jwt没关系）
def reg(request):
    po = json.loads(request.body.decode("utf-8"))
    username = po['name']
    email = po['email']
    password_1 = po['password']
    password_2 = po['password_confirmation']
    # 1，两个密码要保持一致
    if password_1 != password_2:
        return JsonResponse({"error": "两次密码不一致"})

    else:
        m = hashlib.md5()
        m.update(password_1.encode())
        password_m = m.hexdigest()

        # 2，判断是否重名
        users = User.objects.filter(username=username)
        if users:
            return JsonResponse({"error": "用户名已被注册"})
        else:
            # 创建用户数据，再次try，防止并发问题
            try:
                user = User.objects.create(username=username, password=password_m, email=email)
            except Exception as e:
                print('--create user error is %s' % e)
                return JsonResponse({"error": "用户名已被注册"})

            return JsonResponse({'code': 1001, "meg": "注册成功"})


# ================================用户传入账号密码登录，返回jwt（设置jwt的有效时长,20分钟过期）
def jwt_log(request):
    if request.method == "POST":
        try:
            po = json.loads(request.body.decode("utf-8"))
            ema = po['email']
            pwd = po['password']
        except Exception:
            return JsonResponse({'code': 1000, 'error': '没有输入邮箱或者密码'})

        # user_object = models.User.objects.filter(email=ema, password=pwd).first()  # 他这里高亮，但是就是得这么写
        try:
            user_object = User.objects.get(email=ema)  # 他这里高亮，但是就是得这么写
            # 验证密码是否正确
            m = hashlib.md5()
            m.update(pwd.encode())
            if m.hexdigest() != user_object.password:
                return JsonResponse({'code': 1000, 'error': '邮箱或密码错误'})

        except Exception:
            return JsonResponse({'code': 1000, 'error': '邮箱或密码错误'})

        if not user_object:  # 如果用户名或者密码不对（没找到对应的用户）
            return JsonResponse({'code': 1000, 'error': '邮箱或密码错误'})

        import datetime
        salt = 'dsajkldhaslkjndoasibndisa'  # 随便写个字符串也行，来加密（也可以用settings里的一个专用加密字符串）
        # 构造header（不写的话，默认也是这个头部）
        headers = {
            'typ': 'jwt',
            'alg': 'HS256'
        }
        # 构造payload
        payload = {
            'user_id': user_object.id,  # 自定义用户ID
            # 'username': user_object.username,  # 自定义用户名
            # 'email': user_object.email,
            # 'profile':user_object.profile,        后面再添加这个字段
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20)  # 超时时间为minutes的值
        }
        # 生成jwt
        token = jwt.encode(payload=payload, key=salt, algorithm="HS256", headers=headers).decode('utf-8')

        return JsonResponse({'code': 1001, 'token': token})

# 验证token的专用视图函数（比如‘点击收藏’对应的【前端页面】就调用一下这个函数，验证一下token是否还正确，是否过期）
# 顺便还返回用户的信息，就不单独做获取用户信息的函数了，反正要获取信息就是得从请求头解析出来
def jwt_confirm(request):
    # token = request.GET.get('token')  # 情况①：token通过查询字符串传过来.
    authorization = request.META.get("HTTP_AUTHORIZATION", '')  # 情况②：token从请求头传过来
    auth = authorization.split()  # auth是 bear token
    if not auth:
        return JsonResponse({'error': '未获取到Authorization请求头', 'code': 507})
    if auth[0].lower() != 'bearer':
        return JsonResponse({'error': 'Authorization请求头中认证方式错误', 'code': 507})
    if len(auth) == 1:
        return JsonResponse({'error': "非法Authorization请求头", 'code': 507})
    elif len(auth) > 2:
        return JsonResponse({'error': "非法Authorization请求头", 'code': 507})

    token = auth[1]

    salt = 'dsajkldhaslkjndoasibndisa'  # 跟上面加密的盐一样

    payload = None
    err = None
    try:
        payload = jwt.decode(token, salt, True)  # 解密直接一步到位（封装好的，三合一）
    # 检验token，有问题就返回对应的问题。
    except exceptions.ExpiredSignatureError:
        err = 'token已失效'
    except jwt.DecodeError:
        err = 'token认证失败'
    except jwt.InvalidTokenError:
        err = '非法的token'

    if not payload:
        return JsonResponse({'code': 507, 'error': err})

    # print(payload['user_id'], payload['username'])  # 这里的键值对是根据上面加密的时候，构建payload写的
    return JsonResponse({'code': 207, 'user_id': payload['user_id']})


# 返回用户信息
def auth_info(request):
    # ===============================先进行jwt验证(跟上面jwt_confirm代码一样)，顺便拿到用户id================================
    # token = request.GET.get('token')  # 情况①：token通过查询字符串传过来.
    authorization = request.META.get("HTTP_AUTHORIZATION", '')  # 情况②：token从请求头传过来
    auth = authorization.split()  # auth是 bear token
    if not auth:
        return JsonResponse({'error': '未获取到Authorization请求头', 'code': 507})
    if auth[0].lower() != 'bearer':
        return JsonResponse({'error': 'Authorization请求头中认证方式错误', 'code': 507})
    if len(auth) == 1:
        return JsonResponse({'error': "非法Authorization请求头", 'code': 507})
    elif len(auth) > 2:
        return JsonResponse({'error': "非法Authorization请求头", 'code': 507})

    token = auth[1]

    salt = 'dsajkldhaslkjndoasibndisa'  # 跟上面加密的盐一样

    payload = None
    err = None
    try:
        payload = jwt.decode(token, salt, True)  # 解密直接一步到位（封装好的，三合一）
    # 检验token，有问题就返回对应的问题。
    except exceptions.ExpiredSignatureError:
        err = 'token已失效'
    except jwt.DecodeError:
        err = 'token认证失败'
    except jwt.InvalidTokenError:
        err = '非法的token'

    if not payload:
        return JsonResponse({'code': 507, 'error': err})
    # ===========================jwt验证分割线====================================

    # 根据jwt验证出来的id，来查询数据库，然后再返回用户数据。
    user_object = User.objects.get(id=payload['user_id'])
    return JsonResponse({
        'name': user_object.username,
        # 'profile':user_object.profile,
        'email': user_object.email
    })


# 修改用户信息(put请求)
def auth_update(request):
    po = json.loads(request.body.decode("utf-8"))
    user_object = User.objects.get(username=po['pre_name'])  # 他这里高亮，但是就是得这么写
    user_object.username = po['name']
    # user_object.profile = po['profile']
    user_object.save()
    return JsonResponse({"前端传来的put数据": 'what'})
