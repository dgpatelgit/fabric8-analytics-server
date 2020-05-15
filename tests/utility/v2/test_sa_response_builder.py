# Copyright © 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Dharmendra G Patel <dhpatel@redhat.com>
#
"""Test stack analyses response builder class."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch
from bayesian.exceptions import HTTPError
from bayesian.utility.v2.sa_response_builder import StackAnalysesResponseBuilder


class TestStackAnalysesResponseBuilder(unittest.TestCase):
    """Stack Analyses Response Builder Unit Tests."""

    @patch('bayesian.utility.v2.sa_response_builder.request_timed_out', return_value=False)
    def test_sa_response_builder_worker_error(self, _timed_out):
        """Test SA response builder with invalid values for stack result and recm data."""
        stack_result = -1
        recm_data = -1
        sa_response_builder = StackAnalysesResponseBuilder('DUMMY_REQUEST_ID', None,
                                                           stack_result, recm_data)
        # Expect HTTP 404 error.
        self.assertRaises(HTTPError, sa_response_builder.get_response)

    @patch('bayesian.utility.v2.sa_response_builder.request_timed_out', return_value=False)
    def test_sa_response_builder_inprogress(self, _timed_out):
        """Test SA response builder with None data."""
        stack_result = None
        recm_data = None
        sa_response_builder = StackAnalysesResponseBuilder('DUMMY_REQUEST_ID', None,
                                                           stack_result, recm_data)
        # Raises HTTP 202 error for request in progress
        self.assertRaises(HTTPError, sa_response_builder.get_response)

    @patch('bayesian.utility.v2.sa_response_builder.request_timed_out', return_value=True)
    def test_sa_response_builder_timeout(self, _timed_out):
        """Test SA response builder with missing recm data."""
        stack_result = None
        with open(str(Path(__file__).parent.parent.parent) +
                  '/data/backbone/v2_stack_result.json') as f:
            stack_result = json.load(f)
        recm_data = None
        sa_response_builder = StackAnalysesResponseBuilder('DUMMY_REQUEST_ID', None,
                                                           stack_result, recm_data)
        # Raises HTTP 408 error
        self.assertRaises(HTTPError, sa_response_builder.get_response)

    @patch('bayesian.utility.v2.sa_response_builder.request_timed_out', return_value=False)
    def test_sa_response_builder_500(self, _timed_out):
        """Test SA response builder with missing 'task_result' in stack result data."""
        stack_result = None
        with open(str(Path(__file__).parent.parent.parent) +
                  '/data/backbone/v2_stack_result.json') as f:
            stack_result = json.load(f)

        # Remove task_result block.
        del stack_result['task_result']

        recm_data = None
        with open(str(Path(__file__).parent.parent.parent) +
                  '/data/backbone/v2_recm_data.json') as f:
            recm_data = json.load(f)
        sa_response_builder = StackAnalysesResponseBuilder('DUMMY_REQUEST_ID', None,
                                                           stack_result, recm_data)
        # Raises HTTP 500 error
        self.assertRaises(HTTPError, sa_response_builder.get_response)

    @patch('bayesian.utility.v2.sa_response_builder.request_timed_out', return_value=False)
    def test_sa_response_builder_200(self, _timed_out):
        """Test SA response builder with all proper data."""
        stack_result = None
        with open(str(Path(__file__).parent.parent.parent) +
                  '/data/backbone/v2_stack_result.json') as f:
            stack_result = json.load(f)
        recm_data = None
        with open(str(Path(__file__).parent.parent.parent) +
                  '/data/backbone/v2_recm_data.json') as f:
            recm_data = json.load(f)
        sa_response_builder = StackAnalysesResponseBuilder('DUMMY_REQUEST_ID', None,
                                                           stack_result, recm_data)
        response = sa_response_builder.get_response()
        self.assertIsInstance(response, dict)
        self.assertIn('version', response)