#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pootle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pootle; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from pootle_app.models.directory import Directory
from pootle_app.models.permissions import get_permission_contenttype
from pootle_app.views.admin.util import user_is_admin, edit
from pootle_app.views.admin.permissions import admin_permissions, \
        admin_groups, PermissionFormField

from django import forms
from django.contrib.auth.models import Group

@user_is_admin
def view(request):

    directory = Directory.objects.root
    template_vars = {
        'directory': directory,
    }
    return admin_permissions(request, directory, "admin/admin_general_permissions.html", template_vars)

@user_is_admin
def group_users(request):

    directory = Directory.objects.root
    template_vars = {
        'directory': directory,
    }
    return admin_groups(request, directory, "admin/admin_general_groups.html", template_vars)

@user_is_admin
def group_permissions(request):
    content_type = get_permission_contenttype()
    permission_queryset = content_type.permission_set.exclude(
            codename__in=[
                'add_directory', 'change_directory', 'delete_directory',
            ],
    )

    class GroupPermissionsForm(forms.ModelForm):

        class Meta:
            model = Group

        permissions = PermissionFormField(
                label=_('Permissions'),
                queryset=permission_queryset,
                required=False,
        )

    return edit(request, "admin/admin_general_group_permissions.html", Group, {},
                     can_delete=True, form=GroupPermissionsForm,
                     queryset=Group.objects.all().order_by('name'))
