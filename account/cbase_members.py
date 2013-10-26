#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ldap
import copy

from django.conf import settings

"""
Example configuration:

CBASE_LDAP_URL = 'ldap://lea.cbrp3.c-base.org:389/'
CBASE_BASE_DN = 'ou=crew,dc=c-base,dc=org'
"""

def retrieve_member(request):
    # TODO: Put password in encrypted session storage
    return MemberValues(request.user.username, request.session['ldap_password'])


class MemberValues(object):
    """
    Dictionary-like abstraction of the c-base member attributes.
    """
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._old = self._get_user_values()

        # Make a complete copy of the old values so we can later check
        # which
        self._new = copy.deepcopy(self._old)

    def get(self, key, default=None):
        value_list = self._new.get(key, default)
        if value_list:
            value = value_list[0]
        else:
            value = default

        # Decode
        if value == 'TRUE':
            return True
        elif value == 'FALSE':
            return False
        else:
            return value

    def set(self, key, value):
        converted_value = value
        if isinstance(value, bool):
            if value == True:
                converted_value = 'TRUE'
            else:
                converted_value = 'FALSE'
        self._new[key] = [converted_value.encode('latin-1')]

    def save(self):
        """
        Save the values back to the LDAP server.
        """
        dn = "uid=%s,ou=crew,dc=c-base,dc=org" % self._username

        l = ldap.initialize(settings.CBASE_LDAP_URL)
        l.simple_bind_s(dn, self._password)

        mod_attrs = []
        for new_key, new_value in self._new.items():
            # Replace is the default.
            action = ldap.MOD_REPLACE
            if new_key not in self._old.keys():
                action = ldap.MOD_ADD
                mod_attrs.append((action, '%s' % new_key, new_value ))
                continue
            # Set the attribute and wait for the LDAP server to complete.
            if self._old[new_key][0] != new_value[0]:
                action = ldap.MOD_REPLACE
                mod_attrs.append((action, '%s' % new_key, new_value ))
                continue

        print "modattrs: ",mod_attrs
        result = l.modify_s(dn, mod_attrs)
        print "result is: ", result
        l.unbind_s()

    def change_password(self, new_password):
        """
        Change the password of the member.
        You do not need to call save() after calling change_password().
        """
        l = ldap.initialize(settings.CBASE_LDAP_URL)
        user_dn = self._get_bind_dn()
        l.simple_bind_s(user_dn, self._password)
        l.passwd_s(user_dn, self._password, new_password)
        l.unbind_s()

    def to_dict(self):
        result = {}
        for key, value in self._new.items():
            result[key] = self.get(key)
        return result

    def _get_bind_dn(self):
        """
        Adds the uid=userid, to the base dn and returns that.
        """
        bind_dn = 'uid=%s,' % self._username
        bind_dn += settings.CBASE_BASE_DN
        return bind_dn

    def _get_user_values(self):
        """
        Get an attribute from the ldap storage.
        """
        # Create a new LDAP bind (aka connection or session)
        session = ldap.initialize(settings.CBASE_LDAP_URL)
        session.simple_bind_s(self._get_bind_dn(), self._password)

        # Set the attribute and wait for the LDAP server to complete.
        searchScope = ldap.SCOPE_SUBTREE

        # retrieve all attributes
        retrieveAttributes = None
        searchFilter = "uid=%s" % self._username

        dn = settings.CBASE_BASE_DN
        result = session.search_s(dn, searchScope, searchFilter, retrieveAttributes)
        # TODO: latin1
        print "result is: ", result
        # TODO: if len(result)==0
        return result[0][1]
        session.unbind_s()