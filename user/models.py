from django.db import models


# Create your models here.
class User(models.Model):
    username = models.CharField("用户名", max_length=30, null=True, blank=True)
    email = models.CharField("邮箱", max_length=30, unique=True, null=True, blank=True)  # 确保每个邮箱不一样
    password = models.CharField("密码", max_length=32)
    token = models.CharField(max_length=64, null=True, blank=True)  # 传统的token验证（不是jwt）
    created_time = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)  # 记录用户注册时间
    updated_time = models.DateTimeField('更新时间', auto_now=True, null=True, blank=True)

    def str_(self):
        return 'username %s' % self.username
