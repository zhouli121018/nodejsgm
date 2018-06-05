# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import Group
# from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate, get_user_model, password_validation
from app.core.models import User
from .models import MyPermission
from app.utils.regex import pure_digits_regex, pure_english_regex
from django.utils.translation import ugettext_lazy as _

class MyPermissionForm(forms.ModelForm):

    name = forms.CharField(
        label=_(u"权限名称"),
        required=True,
        max_length=50,
        strip=True,
        error_messages={
            "blank": _(u"请填写"),
            "required": _(u"请输入组名"),
            "max_length": _(u"不能超过50个字符"),
        },
        help_text=_(u'请使用英文名称，建议使用链接的前面部分，比如perms为管理员管理'),
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError(_(u"请输入权限名"))
        if not pure_english_regex(name):
            raise forms.ValidationError(u"请使用英文名称，可以使用数字、字母以及特殊字符（._-）")
        if MyPermission.objects.exclude(id=self.instance.id).filter(name=name).exists():
            raise forms.ValidationError(u"不能重复添加权限名")
        return name

    class Meta:
        model = MyPermission
        exclude = ['permission']

    def __init__(self, *args, **kwargs):
        super(MyPermissionForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = MyPermission.objects.filter(parent__isnull=True)

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label=_(u"组名"),
        required=True,
        max_length=80,
        strip=True,
        error_messages={
            "blank": _(u"请填写"),
            "required": _(u"请输入组名"),
            "max_length": _(u"不能超过80个字符"),
        }
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError(_(u"请输入组名"))
        if Group.objects.exclude(id=self.instance.id).filter(name=name).exists():
            raise forms.ValidationError(u"不能重复添加组名")
        return name

    class Meta:
        model = Group
        fields = ('name', )
        # exclude = ['permissions']

class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _(u"两次输入的密码不一致."),
    }
    password1 = forms.CharField(
        label=_(u"密码"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_(u"确认密码"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_(u"再次输入密码以进行验证。"),
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_superuser', 'is_active',)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': ''})

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1)<8:
            raise forms.ValidationError(_(u"您的密码必须至少包含8个字符。",))
        if pure_digits_regex(password1):
            raise forms.ValidationError(_(u"您的密码不能完全是数字。", ))
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        # self.instance.username = self.cleaned_data.get('username')
        # password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _(u"两次输入的密码不一致."),
    }
    new_password1 = forms.CharField(
        label=_(u"新密码"),
        widget=forms.PasswordInput,
        strip=False,
        # help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_(u"确认新密码"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if len(password1)<8:
            raise forms.ValidationError(_(u"您的密码必须至少包含8个字符。",))
        if pure_digits_regex(password1):
            raise forms.ValidationError(_(u"您的密码不能完全是数字。", ))
        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("您的旧密码输入不正确。 请重新输入。"),
    })
    old_password = forms.CharField(
        label=_(u"旧密码"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


