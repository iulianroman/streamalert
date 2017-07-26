'''
Copyright 2017-present, Airbnb Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import base64
import json

from mock import Mock

from stream_alert.rule_processor.classifier import StreamClassifier
from stream_alert.rule_processor.payload import load_stream_payload

from unit.stream_alert_rule_processor import (
    REGION,
    FUNCTION_NAME
)


def _get_mock_context():
    """Create a fake context object using Mock"""
    arn = 'arn:aws:lambda:{}:123456789012:function:{}:production'
    context = Mock(invoked_function_arn=(arn.format(REGION, FUNCTION_NAME)),
                   function_name=FUNCTION_NAME)

    return context


def _get_valid_config():
    """Helper function to return a config that is valid

    Returns:
        [dict] contents of a valid config file
    """
    return {
        'logs': {
            'json_log': {
                'schema': {
                    'name': 'string'
                },
                'parser': 'json'
            },
            'csv_log': {
                'schema': {
                    'data': 'string',
                    'uid': 'integer'
                },
                'parser': 'csv'
            }
        },
        'sources': {
            'kinesis': {
                'stream_1': {
                    'logs': [
                        'json_log',
                        'csv_log'
                    ]
                }
            }
        }
    }


def _get_valid_event(count=1):
    record_data = {
        'unit_key_01': '100',
        'unit_key_02': 'another bogus value'
    }

    data_json = json.dumps(record_data)
    raw_record = _make_kinesis_raw_record('unit_test_default_stream', data_json)

    return {'Records': [raw_record for _ in range(count)]}


def _load_payload_by_service(config, service, entity, raw_record):

    # prepare the payloads
    payload = load_stream_payload(service, entity, raw_record)

    payload = payload.pre_parse().next()
    classifier = StreamClassifier(config=config)
    classifier.load_sources(service, entity)
    classifier.classify_record(payload)

    return payload


def _make_kinesis_raw_record(kinesis_stream, kinesis_data):
    """Helper for creating the kinesis raw record"""
    raw_record = {
        'eventID': 'e51da7591078af083690d89023c881fdea',
        'eventSource': 'aws:kinesis',
        'eventSourceARN': 'arn:aws:kinesis:us-east-1:123456789012:stream/{}'
                          .format(kinesis_stream),
        'kinesis': {
            'data': base64.b64encode(kinesis_data)
        }
    }
    return raw_record
