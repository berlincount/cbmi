#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError(_('Sorry, that login was invalid. '
                                          'Please try again.'), code='invalid_login')
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class GastroPinField(forms.CharField):
    widget = forms.PasswordInput
    def validate(self, value):
        """
        Check if the value is all numeric and 4 - 6 chars long.
        """
        match = re.match(r'^\d{4,6}$', value)
        if not match:
            raise forms.ValidationError(_('PIN must be 4 to 6 digits.'))


class GastroPinForm(forms.Form):
    gastropin1 = GastroPinField(label=_('New Gastro-PIN'))
    gastropin2 = GastroPinField(label=_('Repeat Gastro-PIN'))

    def clean(self):
        cleaned_data = super(GastroPinForm, self).clean()
        gastropin1 = cleaned_data.get("gastropin1")
        gastropin2 = cleaned_data.get("gastropin2")
        if gastropin1 != gastropin2:
            raise forms.ValidationError(
                _('The PINs entered were not identical.'),
                code='not_identical')



class WlanPresenceForm(forms.Form):
    # Boolean fields must never be required.
    presence = forms.BooleanField(required=False,
            label=_('Enable WiFi presence'))


class PasswordForm(forms.Form):
    password1 = forms.CharField(max_length=255, widget=forms.PasswordInput,
        label=_('New password'))
    password2 = forms.CharField(max_length=255, widget=forms.PasswordInput,
        label=_('Repeat password'))


class RFIDForm(forms.Form):
    rfid = forms.CharField(max_length=255, label=_('Your RFID'),
        help_text=_('Find out your RFID by holding your RFID tag to the '
                    'reader in the airlock.'))


class SIPPinForm(forms.Form):
    sippin1 = GastroPinField(label=_('Your SIP PIN'))
    sippin2 = GastroPinField(label=_('Repeat SIP PIN'))

    def clean(self):
        cleaned_data = super(SIPPinForm, self).clean()
        sippin1 = cleaned_data.get("sippin1")
        sippin2 = cleaned_data.get("sippin2")
        if sippin1 != sippin2:
            raise forms.ValidationError(
                _('The PINs entered were not identical.'),
                code='not_identical')


class NRF24Form(forms.Form):
    nrf24 = forms.CharField(max_length=255,
        label = _('NRF24-ID'),
        help_text=_("Your r0ket's NRF24 identification"))


class CLabPinForm(forms.Form):
    c_lab_pin1 = GastroPinField(label=_('New c-lab PIN'))
    c_lab_pin2 = GastroPinField(label=_('Repeat c-lab PIN'),
            help_text=_('Numerical only, 4 to 6 digits'))