# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShuttleStop'
        db.create_table(u'campus_shuttlestop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stop_id', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shuttle_stops', to=orm['campus.ShuttleRoute'])),
        ))
        db.send_create_signal(u'campus', ['ShuttleStop'])

        # Adding field 'ShuttleRoute.color'
        db.add_column(u'campus_shuttleroute', 'color',
                      self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ShuttleStop'
        db.delete_table(u'campus_shuttlestop')

        # Deleting field 'ShuttleRoute.color'
        db.delete_column(u'campus_shuttleroute', 'color')


    models = {
        u'campus.bikerack': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BikeRack', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.building': {
            'Meta': {'ordering': "('name', 'id')", 'object_name': 'Building', '_ormbases': [u'campus.MapObj']},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'}),
            'sketchup': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'campus.dininglocation': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DiningLocation', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.disabledparking': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DisabledParking', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'}),
            'num_spaces': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'campus.emergencyphone': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EmergencyPhone', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.group': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Group', '_ormbases': [u'campus.MapObj']},
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['campus.GroupedLocation']", 'null': 'True', 'symmetrical': 'False'}),
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.groupedlocation': {
            'Meta': {'unique_together': "(('object_pk', 'content_type'),)", 'object_name': 'GroupedLocation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'campus.location': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Location', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.mapobj': {
            'Meta': {'ordering': "('name',)", 'object_name': 'MapObj'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'googlemap_point': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'primary_key': 'True'}),
            'illustrated_point': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'poly_coords': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'profile': ('tinymce.models.HTMLField', [], {'null': 'True'})
        },
        u'campus.parkinglot': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ParkingLot', '_ormbases': [u'campus.MapObj']},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'}),
            'permit_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'sketchup': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'campus.regionalcampus': {
            'Meta': {'ordering': "('name',)", 'object_name': 'RegionalCampus', '_ormbases': [u'campus.MapObj']},
            u'mapobj_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['campus.MapObj']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'campus.shuttlecategory': {
            'Meta': {'object_name': 'ShuttleCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'campus.shuttleroute': {
            'Meta': {'object_name': 'ShuttleRoute'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shuttle_routes'", 'to': u"orm['campus.ShuttleCategory']"}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        u'campus.shuttlestop': {
            'Meta': {'object_name': 'ShuttleStop'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shuttle_stops'", 'to': u"orm['campus.ShuttleRoute']"}),
            'stop_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        u'campus.sidewalk': {
            'Meta': {'object_name': 'Sidewalk'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poly_coords': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        u'campus.simplesetting': {
            'Meta': {'object_name': 'SimpleSetting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'value': ('tinymce.models.HTMLField', [], {'null': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['campus']