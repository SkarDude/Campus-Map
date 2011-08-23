from django.db import models
from tinymce import models as tinymce_models
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import m2m_changed
from django.core.exceptions import FieldError


class MapQuerySet(QuerySet):
	'''
	Model inheritance with content type and inheritance-aware manager
	thanks: http://djangosnippets.org/snippets/1034/
	'''
	
	campus_models = False
	
	def __getitem__(self, k):
		result = super(MapQuerySet, self).__getitem__(k)
		if isinstance(result, models.Model):
			return result.as_leaf_class()
		else:
			return result
	def __iter__(self):
		for item in super(MapQuerySet, self).__iter__():
			yield item.as_leaf_class()
	
	def get(self, *args, **kwargs):
		# same as getitem, idk why getitem isn't called when this is used
		result = QuerySet.get(self, *args, **kwargs)
		if isinstance(result, models.Model):
			return result.as_leaf_class()
		else:
			return result
	
	def filter(self, *args, **kwargs):
		'''
		allows to query over all MapObj's incliding child specfic fields.
		The queryset returned has only MapObj's in it, yet when each one is
		pulled, __getitem__ converts back to original object, creating a
		pseudo heterogenous queryset
		ex:
			can now do
				MapObj.objects.filter(abbreviation="MAP")
				MapObj.objects.filter(permit_type="Greek Row")
			yet these attributes are not apart of MapObj
		'''
		
		import campus
		
		# grab all the models that extend MapObj
		if not MapQuerySet.campus_models:
			MapQuerySet.campus_models = []
			for ct in ContentType.objects.filter(app_label="campus"):
				model = models.get_model("campus", ct.model)
				if issubclass(model, campus.models.MapObj):
					MapQuerySet.campus_models.append(model)
		
		# execute query over leaf instances of MapObj
		# return queryset containing MapObj's
		from django.db.models import Q
		map_query = Q(pk="~~~ no results ~~~")
		for m in self.campus_models:
			try:
				qs = QuerySet(m)
				results = qs.filter(*args, **kwargs)
				if m == campus.models.MapObj:
					for o in results:
						map_query = map_query | Q(id=o.id)
				else:
					for o in results:
						map_query = map_query | Q(id=o.mapobj_ptr_id)
			except FieldError:
				continue
		
		# return a QuerySet of MapObj's
		return QuerySet.filter(self, map_query)

class MapManager(models.Manager):
	def get_query_set(self):
		return MapQuerySet(self.model)

class MapObj(models.Model):
	objects           = MapManager()
	content_type      = models.ForeignKey(ContentType,editable=False,null=True)
	id                = models.CharField(max_length=80, primary_key=True, help_text='<strong class="caution">Caution</strong>: changing may break external resources (used for links and images)')
	name              = models.CharField(max_length=255)
	image             = models.CharField(max_length=50,  blank=True, help_text='Don&rsquo;t forget to append a file extension')
	description       = models.CharField(max_length=255, blank=True)
	profile           = tinymce_models.HTMLField(blank=True, null=True)
	googlemap_point   = models.CharField(max_length=255, null=True, blank=True, help_text='E.g., <code>[28.6017, -81.2005]</code>')
	illustrated_point = models.CharField(max_length=255, null=True, blank=True)
	poly_coords       = models.TextField(blank=True, null=True)
	
	def _title(self):
		if (self.name):
			return self.name
		else:
			return self.__repr__()
	title = property(_title)
	
	def _orgs(self, limit=4):
		''' retruns a subset of orgs '''
		from apps.views import get_orgs
		building_orgs = []
		count    = 0
		overflow = False
		for o in get_orgs()['results']:
			if self.pk == o['bldg_id']:
				building_orgs.append(o)
				count += 1
			if(limit > 0 and count >= limit):
				overflow = True
				break
		return {
			"results" : building_orgs,
			"overflow": overflow
		}
	orgs = property(_orgs)
	
	def json(self):
		"""Returns a json serializable object for this instance"""
		import json
		obj = dict(self.__dict__)
		
		for key,val in obj.items():
			
			if key == "_state":
				# prevents object.save() function from being destroyed
				# not sure how or why it does, but if object.json() is called
				# first, object.save() will fail
				obj.pop("_state")
				continue
			
			# with the validator, hopefully this never causes an issue
			if key == "poly_coords":
				if obj["poly_coords"] != None:
					obj["poly_coords"] = json.loads(str(obj["poly_coords"]))
				continue
			if key == "illustrated_point" or key == "googlemap_point":
				if obj[key] != None:
					obj[key] = json.loads(str(obj[key]))
				continue
			
			if isinstance(val, unicode):
				continue
			
			# super dumb, concerning floats http://code.djangoproject.com/ticket/3324
			obj[key] = val.__str__()
		
		return obj
	
	def _link(self):
		url = reverse('location', kwargs={'loc':self.id})
		return '<a href="%s%s/" data-pk="%s">%s</a>' % (url, slugify(self.name), self.id, self.title)
	link = property(_link)

	def _profile_link(self):
		url = reverse('location', kwargs={'loc':self.id})
		return '%s%s/' % (url, slugify(self.title))
	profile_link = property(_profile_link)
	
	
	def clean(self, *args, **kwargs):
		from django.core.exceptions import ValidationError
		import json
		
		# keep blanks out of coordinates
		if self.poly_coords       == "": self.poly_coords       = None
		if self.illustrated_point == "": self.illustrated_point = None
		if self.googlemap_point   == "": self.googlemap_point   = None
		
		# check poloy coordinates
		if self.poly_coords != None: 
			try:
				json.loads("{0}".format(self.poly_coords))
			except ValueError:
				raise ValidationError("Invalid polygon coordinates (not json serializable)")
		
		# check illustrated point
		if self.illustrated_point != None: 
			try:
				json.loads("{0}".format(self.illustrated_point))
			except ValueError:
				raise ValidationError("Invalid Illustrated Map Point (not json serializable)")
			
		# check google map point
		if self.googlemap_point != None: 
			try:
				json.loads("{0}".format(self.googlemap_point))
			except ValueError:
				raise ValidationError("Invalid Google Map Point (not json serializable)")
		
		super(MapObj, self).clean(*args, **kwargs)
	
	def save(self, *args, **kwargs):
		if(not self.content_type):
			self.content_type = ContentType.objects.get_for_model(self.__class__)
		super(MapObj, self).save(*args, **kwargs)
	
	def as_leaf_class(self):
		content_type = self.content_type
		model = content_type.model_class()
		if (model == MapObj):
			return self
		return model.objects.get(id=self.id)
	
	def __unicode__(self):
		return u'%s' % (self.name)
	
	class Meta:
		ordering = ("name",)

class Location(MapObj):
	'''
	I don't like this name.  Maybe "miscellaneous locations" or "greater ucf"
	'''
	pass

class RegionalCampus(MapObj):
	def _img_tag(self):
		import settings
		image_url = settings.MEDIA_URL + 'images/regional-campuses/' + self.id + '.jpg'
		return '<img src="%s" alt="%s">' % (image_url, self.description)
	img_tag = property(_img_tag)
	
	class Meta:
		verbose_name_plural = "Regional Campuses"

class Building(MapObj):
	abbreviation      = models.CharField(max_length=50, blank=True)
	sketchup          = models.CharField(max_length=50, blank=True, help_text="E.g., http://sketchup.google.com/3dwarehouse/details?mid=<code>54b7f313bf315a3a85622796b26c9e66</code>&prevstart=0")
	
	def _number(self):
		return self.id
	number = property(_number)
	
	def _title(self):
		if self.abbreviation:
			return "%s (%s)" % (self.name, self.abbreviation)
		else:
			return self.name
	title = property(_title)
	
	def clean(self, *args, **kwargs):
		super(Building, self).clean(*args, **kwargs)
		
		# change all numbers to be lowercase
		self.number = self.number.lower()
	
	def json(self):
		obj = MapObj.json(self)
		obj['number'] = self.number
		obj['profile_link'] = self.profile_link
		obj['link'] = self.link
		obj['title'] = self.title
		obj['orgs'] = self.orgs
		return obj
	
	class Meta:
		ordering = ("name", "id")

class ParkingLot(MapObj):
	permit_type = models.CharField(max_length=255, blank=True, null=True)
	number      = models.CharField(max_length=50, blank=True, null=True)
	
	def _kml_coords(self):
		if self.poly_coords == None:
			return None
		
		import json
		def flat(l):
			''' 
			recursive function to flatten array and create a a list of coordinates separated by a space
			'''
			str = ""
			for i in l:
				if type(i[0]) == type([]):
					str += flat(i)
				else:
					str += ("%.6f,%.6f ")  % (i[0], i[1])
			return str
		
		
		arr = json.loads(self.poly_coords)
		return flat(arr)
	kml_coords = property(_kml_coords)
	
	
	def _color_fill(self):
		
		colors = {
			"B Permits"       : "cc0400", #red
			"C Permits"       : "0052d9", #blue
			"D Permits"       : "009a36", #green
			"Housing Permits" : "ffba00", #orange
			"Greek Row"       : "eb00e3", #pink
		}
		
		rgb = colors.get(self.permit_type) or 'fffb00' #default=yellow
		opacity = .35
		
		# kml is weird, it goes [opacity][blue][green][red] (each two digit hex)
		kml_color = "%x%s%s%s" % (int(opacity*255), rgb[4:], rgb[2:4], rgb[0:2])
		return kml_color
	color_fill = property(_color_fill)
	
	def _color_line(self):
		# same as fill, up opacity
		color = self.color_fill
		opacity = .70
		kml_color = "%x%s" % (opacity * 255, color[2:])
		return kml_color
	color_line = property(_color_line)


class HandicappedParking(MapObj):
	class Meta:
		verbose_name_plural = "Handicap Parking"


class Sidewalk(models.Model):
	poly_coords = models.TextField(blank=True, null=True)
	
	def _kml_coords(self):
		if self.poly_coords == None:
			return None
		
		import json
		def flat(l):
			''' 
			recursive function to flatten array and create a a list of coordinates separated by a space
			'''
			str = ""
			for i in l:
				if type(i[0]) == type([]):
					return flat(i)
				else:
					str += ("%.6f,%.6f ")  % (i[0], i[1])
			return str
		
		
		arr = json.loads(self.poly_coords)
		return flat(arr)
	kml_coords = property(_kml_coords)
	
	
	def clean(self, *args, **kwargs):
		from django.core.exceptions import ValidationError
		import json
		
		# keep blanks out of coordinates
		if self.poly_coords       == "": self.poly_coords       = None
		
		# check poloy coordinates
		if self.poly_coords != None: 
			try:
				json.loads("{0}".format(self.poly_coords))
			except ValueError:
				raise ValidationError("Invalid polygon coordinates (not json serializable)")
		
		super(Sidewalk, self).clean(*args, **kwargs)

class BikeRack(MapObj):
	pass

class EmergencyPhone(MapObj):
	pass


'''
	This shit should be built into the exporter.  When looking at the groups
	in the export, fucking thing makes no sense wihtout this manager
'''
class GroupedLocationManager(models.Manager):
	def get_by_natural_key(self, content_type, object_pk):
		app_label, model = content_type.split(".")
		content_type = ContentType.objects.get(app_label=app_label, model=model)
		return self.get(content_type=content_type.pk, object_pk=object_pk)

class GroupedLocation(models.Model):
	objects      = GroupedLocationManager()
	
	object_pk    = models.CharField(max_length=255)
	content_type = models.ForeignKey(ContentType)
	content_object = generic.GenericForeignKey('content_type', 'object_pk')
	
	def __unicode__(self):
		loc      = self.content_object
		loc_name = str(loc)
		if not loc_name:
			loc_name = "#{0}".format(loc.pk)
		if hasattr(loc, 'abbreviation') and str(loc.abbreviation):
			loc_name = "{0} ({1})".format(loc_name, loc.abbreviation)
		if hasattr(loc, 'number') and str(loc.number):
			loc_name = "{0} | {1}".format(loc_name, loc.number)
		loc_class = loc.__class__.__name__
		return "{0} | {1}".format(loc_class, loc_name)
	
	def natural_key(self):
		content_type = ".".join(self.content_type.natural_key())
		return (content_type, self.object_pk)
	natural_key.dependencies = ['contenttypes.contenttype']
	
	class Meta:
		unique_together = (('object_pk', 'content_type'),)

class Group(MapObj):
	locations = models.ManyToManyField(GroupedLocation, blank=True)
	
	def json(self):
		obj = super(Group, self).json()
		locations = []
		for l in self.locations.all():
			locations.append(l.content_object.link)
		if len(locations):
			obj['locations'] = locations
		return obj
		
	@classmethod
	def update_coordinates(cls, **kwargs):
		sender = kwargs['instance']
		sender.googlemap_point   = sender.midpoint('googlemap_point')
		sender.illustrated_point = sender.midpoint('illustrated_point')
		sender.save()
	
	def midpoint(self, coordinates_field):
		import json
		midpoint_func = lambda a, b: [((a[0] + b[0])/2), ((a[1] + b[1])/2)]
		
		points = [p.content_object for p in self.locations.all()]
		points = [getattr(p, coordinates_field, None) for p in points]
		points = [json.loads(p) for p in points if p is not None]
		
		if len(points) < 1:
			return None
		if len(points) < 2:
			return json.dumps(points[0])
		
		midpoint = reduce(midpoint_func, points)
		midpoint = json.dumps(midpoint)
		return midpoint
	
	def __unicode__(self):
		return self.name

m2m_changed.connect(Group.update_coordinates, sender=Group.locations.through)
