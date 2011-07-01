from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('campus.views',
	url(r'^$', 'home', { 'points' : True }, name="home"),
	url(r'^locations/?$', 'locations', name="locations"),
	url(r'^locations/(?P<loc>[\w-]+)/([^/]+/)??$', 'location', name="location"),
	url(r'^sidewalks/?$', 'sidewalks', name="sidewalks"),
	url(r'^bikeracks/?$', 'bikeracks', name="bikeracks"),
	url(r'^emergency-phones/?$', 'emergency_phones', name="emergency_phones"),
	url(r'^parking/?$', 'parking', name="parking"),
	url(r'^regional-campuses/((?P<campus>[\w-]+)/)??$', 'regional_campuses', name="regional"),
)
