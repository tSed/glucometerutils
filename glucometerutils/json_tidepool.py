# -*- coding: utf-8 -*-
"""Driver for exporting data into the Tidepool JSON format for ingestion.

Further information on the Tidepool JSON format:

http://developer.tidepool.org/data-model/device-data/

"""

__author__ = 'Samuel Martin'
__email__ = 's.martin49@gmail.com'
__copyright__ = 'Copyright © 2017, Samuel Martin'
__license__ = 'MIT'

import datetime

import json

import glucometerutils.common
from glucometerutils.common import GlucoseReading
from glucometerutils.common import KetoneReading

"""
JSON tidepool formats
[i  ]: ingestion format
[ s ]: storage format
[  c]: client format

common fields:
{
    "_active": true,                                #[ s ]     datum state
    "_groupId": "abcdef",                           #[ s ] n/a tidepool innards
    "_schemaVersion": 0,                            #[ s ]     tidepool data model version (= 1)
    "_version": 0,                                  #[ s ]     datum version number, start at 0
    "clockDriftOffset": 0,                          #[isc]     optional (= 0)
    "conversionOffset": 0,                          #[isc]     diff device time/display time (= 0)
    "createdTime": "2016-06-14T02:05:49.239Z",      #[ s ]     creation time
    "deviceId": "DevId0987654321",                  #[isc]     model + s/n
    "deviceTime": "2016-06-13T19:05:44",            #[isc]     device time
    "guid": "0f3f13b1-be2c-41b3-87b4-edc7e0a2fd36", #[isc] n/a uuid of the upload
    "id": "272383b5fe274fd3b66eb31b536555c9",       #[ sc]     uuid
    "time": "2016-06-14T02:05:44.239Z",             #[isc] n/a utctime of the of the upload
    "timezoneOffset": -420,                         #[isc] n/a diff localitime/utctime of upload
    "uploadId": "SampleUploadId"                    #[isc] n/a uploader id
}


Blood Ketones (bloodKetone)
{
    "type": "bloodKetone",                          #[isc] = bloodKetone
    "units": "mmol/L",                              #[isc] = mmol/L
    "value": 0.8,                                   #[isc] float number
    + common fields
}


Continuous Blood Glucose (cbg)
{
    "type": "cbg",                                  #[isc] = cbg
    "units": "mmol/L",                              #[isc] = mmol/L[isc]|mg/dL[ sc]
    "value": 24.811843519973536,                    #[isc] number; integer (mg/dL), float (mmol/L)
    + common fields
}


Self-Monitored Blood Glucose (smbg)
{
    "type": "smbg",                                 #[isc] = smbg
    "subType": "linked",                            #[isc] ? = manual|linked (for pump, n/a for reader)
    "units": "mmol/L",                              #[isc] = mmol/L[isc]|mg/dL[ sc]
    "value": 24.811843519973536,                    #[isc] number; integer (mg/dL), float (mmol/L)
    + common fields
}


glucometerutils export format = ingestion Tidepool format
"""

# TODO:
#   "clockDriftOffset": 0,                          #[i]     optional (= 0)
#   "conversionOffset": 0,                          #[i]     diff device time/display time (= 0)
#   "deviceId": "DevId0987654321",                  #[i]     model + s/n
#   "deviceTime": "2016-06-13T19:05:44",            #[i]     device time
#   "guid": "0f3f13b1-be2c-41b3-87b4-edc7e0a2fd36", #[i] n/a uuid of the upload
#   "time": "2016-06-14T02:05:44.239Z",             #[i] n/a utctime of the of the upload
#   "timezoneOffset": -420,                         #[i] n/a diff localitime/utctime of upload
#   "uploadId": "SampleUploadId"                    #[i] n/a uploader id
#
#   "type": "bloodKetone",                          #[i] = bloodKetone
#   "units": "mmol/L",                              #[i] = mmol/L
#   "value": 0.8,                                   #[i] float number
#
#   "type": "cbg",                                  #[i] = cbg
#   "units": "mmol/L",                              #[i] = mmol/L[isc]|mg/dL[i  ]
#   "value": 24.811843519973536,                    #[i] number; integer (mg/dL), float (mmol/L)
#
#   "type": "smbg",                                 #[i] = smbg
#   "subType": "linked",                            #[i] ? = manual|linked (only from pump)
#   "units": "mmol/L",                              #[i] = mmol/L[isc]|mg/dL[i  ]
#   "value": 24.811843519973536,                    #[i] number; integer (mg/dL), float (mmol/L)


def _generate_record(device_info, reading):
  """Return the dictionary of the JSON representation of the reading."""
  if isinstance(reading, KetoneReading):
    value_type = 'bloodKetone'
    value_unit = glucometerutils.common.UNIT_MMOLL
  elif isinstance(reading, GlucoseReading):
    if reading.measure_method == glucometerutils.common.CGM:
      value_type = 'cgb'
    else:
      value_type = 'smbg'
    value_unit = device_info.native_unit
  return {
    'clockDriftOffset': 0,
    'conversionOffset': 0,
    'deviceId': device_info.model.replace(' ', '') + '_' +
      device_info.serial_number.replace(' ', ''),
    'deviceTime': reading.timestamp.isoformat(),
    'type': value_type,
    'units': value_unit,
    'value': reading.value,
  }

def generate_tidepool_json(device_info, readings):
  """Return the JSON Tidepool string of the readings."""
  records = [_generate_record(device_info, r) for r in readings]
  return json.JSONEncoder().encode(records)
