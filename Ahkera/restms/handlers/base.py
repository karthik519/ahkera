#   Copyright 2009 Thilo Fromm
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.db import models
from django.template import Context, loader
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404

from processor import RestMSXMLProcessor, RestMSProcessorException

class BaseHandler(models.Model):
    """Abstract base class for RestMS resources"""

    hash    = models.AutoField( primary_key = True )
    created = models.DateTimeField( auto_now_add = True, editable = False)
    modified= models.DateTimeField( auto_now = True, editable = False)

    # resource_type attribute is to be set by implementing classes
    #  to the RestMS resource typetype
    def _type_set(self):    raise AttributeError("Abstract")
    def _type_get(self):    raise AttributeError("Abstract")
    resource_type    = property(_type_get, _type_set)

    @classmethod
    def writeable(cls, attr):
        """Check wheter the field specified by attr is writeable"""
        # TODO Hack Alert: "editable" field property not exposed by Django?
        return cls._meta.get_field(attr).editable

    @models.permalink
    def get_absolute_url(self):
        """Return absolute resource URI (without protocol / domain)"""
        return ("restms.views.resource", [self.resource_type, str(self.hash)])

    class Meta: 
        app_label = 'restms'
        abstract = True

    def default_GET(self, request):
        """ Generic GET rendering the type's default template with the
            corresponding object """
        t = loader.get_template("".join([self.resource_type, "/get.xml"]))
        c = Context({self.resource_type : self,
                     'base_url'         : request.build_absolute_uri('/')})
        return HttpResponse(t.render(c))

    def default_PUT(self, request):
        """ Generic PUT updating the resource , then calling GET to render
            a response """
        raise AttributeError("NOT IMPLEMENTED")
        p = RestMSProcessor()

        try: p.update_resource(request, self)
        except RestMSProcessorException, e: return e.message

        self.save(force_update=True)
        return self.GET(request)

    def default_DELETE(self,request):
        """ Generic DELETE removing the resource"""
        self.delete()
        return HttpResponse()

