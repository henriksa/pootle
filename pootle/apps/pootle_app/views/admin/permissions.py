#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2012 Zuza Software Foundation
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

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from pootle_app.models import Directory
from pootle_app.models.permissions import (get_permission_contenttype,
                                           PermissionSet, GroupPermissionSet)
from pootle_app.views.admin import util
from pootle_misc.forms import GroupedModelChoiceField
from pootle_profile.models import PootleProfile


class PermissionFormField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, instance):
        return _(instance.name)


def admin_permissions(request, current_directory, template, context):
    content_type = get_permission_contenttype()
    permission_queryset = content_type.permission_set.exclude(
            codename__in=[
                'add_directory', 'change_directory', 'delete_directory',
            ],
    )

    project = context.get('project', None)
    language = context.get('language', None)

    base_queryset = PootleProfile.objects.filter(user__is_active=1).exclude(
            id__in=current_directory.permission_sets \
                                    .values_list('profile_id', flat=True),
    )
    querysets = [(None, base_queryset.filter(
        user__username__in=('nobody', 'default')
    ))]

    if project is not None:
        if language is not None:
            querysets.append((
                _('Project Members'),
                base_queryset.filter(projects=project, languages=language)
                             .order_by('user__username'),
            ))
        else:
            querysets.append((
                _('Project Members'),
                base_queryset.filter(projects=project)
                             .order_by('user__username'),
            ))

    if language is not None:
        querysets.append((
            _('Language Members'),
            base_queryset.filter(languages=language).order_by('user__username')
        ))

    querysets.append((
        _('All Users'),
        base_queryset.exclude(user__username__in=('nobody', 'default'))
                     .order_by('user__username'),
    ))


    class PermissionSetForm(forms.ModelForm):

        class Meta:
            model = PermissionSet

        directory = forms.ModelChoiceField(
                queryset=Directory.objects.filter(pk=current_directory.pk),
                initial=current_directory.pk,
                widget=forms.HiddenInput,
        )
        profile = GroupedModelChoiceField(
                querysets=querysets,
                queryset=PootleProfile.objects.all(),
                required=True,
        )
        positive_permissions = PermissionFormField(
                label=_('Permissions'),
                queryset=permission_queryset,
                required=False,
        )

    link = lambda instance: unicode(instance.profile)
    directory_permissions = current_directory.permission_sets \
                                             .order_by('profile').all()

    return util.edit(request, template, PermissionSet, context, link,
                     linkfield='profile', queryset=directory_permissions,
                     can_delete=True, form=PermissionSetForm)


def admin_groups(request, current_directory, template, context):
    content_type = get_permission_contenttype()
    permission_queryset = content_type.permission_set.exclude(
            codename__in=[
                'add_directory', 'change_directory', 'delete_directory',
            ],
    )

    project = context.get('project', None)
    language = context.get('language', None)

    profile_queryset = PootleProfile.objects.filter(user__is_active=1)\
            .exclude(user__username__in=('nobody', 'default'))\
            .order_by('user__username')

    class GroupUsersForm(forms.ModelForm):

        class Meta:
            model = GroupPermissionSet

        directory = forms.ModelChoiceField(
                queryset=Directory.objects.filter(pk=current_directory.pk),
                initial=current_directory.pk,
                widget=forms.HiddenInput,
        )
        group = forms.ModelChoiceField(
                 label=_('Group'),
                 queryset=Group.objects.all(),
                 required=True,
        )
        profiles = forms.ModelMultipleChoiceField(
                label=_('Users'), required=True, queryset=profile_queryset
        )

    link = lambda instance: unicode(instance.group)
    return util.edit(request, template, GroupPermissionSet, context, link=link,
            queryset=current_directory.group_permission_sets.order_by('group'),
            can_delete=True, form=GroupUsersForm, linkfield='group')
