#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "aplle_half"
# Date: 2017/9/6
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


class RegForm(forms.Form):
    def __init__(self, *args):
        if args:
            self.request = args[0]
            forms.Form.__init__(self, args[1])
        else:
            forms.Form.__init__(self)

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "username"}),
                               error_messages={'required': '用户名不能为空'})

    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "password"}),
                               error_messages={'required': '密码不能为空'})

    repeat_password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "password"}), error_messages={'required': '密码不能为空'})

    email = forms.EmailField(error_messages={'required': '邮箱不能为空'},
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "email"}))

    valid_code = forms.CharField(error_messages={'required': '验证码不能为空'},
                                 widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "valid_code"}))

    def clean_password(self):

        if len(self.cleaned_data.get("password")) < 4:
            raise ValidationError("密码小于4位！")
        elif len(self.cleaned_data.get("password")) > 20:
            raise ValidationError("密码最长为20位!！")
        else:

            return self.cleaned_data["password"]

    def clean_username(self):

        if self.cleaned_data.get("username").isdigit() or self.cleaned_data.get("username").isalpha():
            raise ValidationError("用户名必须包含数字与字母！")

        elif len(self.cleaned_data.get("username")) < 4:
            raise ValidationError("用户名小于4位！")

        elif len(self.cleaned_data.get("username")) > 12:
            raise ValidationError("用户名大于12位！")

        else:
            return self.cleaned_data["username"]

    def clean_valid_code(self):

        if self.cleaned_data.get("valid_code").upper() == self.request.session["valid_code"].upper():
            return self.cleaned_data["valid_code"]

        else:
            raise ValidationError("验证码错误")

    def clean(self):

        if self.cleaned_data.get("password") == self.cleaned_data.get("repeat_password"):
            return self.cleaned_data

        else:
            raise ValidationError("密码不一致")
