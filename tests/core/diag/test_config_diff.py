# Copyright 2020 DataStax, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""validate the config_diff module"""
import unittest
from collections import OrderedDict
from pysper.core.diag import config_diff


class TestConfigDiff(unittest.TestCase):
    """test config diff"""

    def test_group_configurations(self):
        """all grouped"""
        node_config = OrderedDict(
            [
                ("node1", OrderedDict([("abc", "xyz")])),
                ("node2", OrderedDict([("abc", "xyz")])),
            ]
        )
        groups = config_diff.group_configurations(node_config)
        self.assertEqual(len(groups), 1)
        first_group = groups[0]
        self.assertEqual(first_group["nodes_list"], ["node1", "node2"])
        self.assertEqual(first_group["nodes"], 2)
        self.assertEqual(first_group["abc"], "xyz")

    def test_group_configurations_with_diffs(self):
        """one of each"""
        node_config = OrderedDict(
            [
                ("node1", OrderedDict([("abc", "zzz")])),
                ("node2", OrderedDict([("abc", "xyz")])),
            ]
        )
        groups = config_diff.group_configurations(node_config)
        self.assertEqual(len(groups), 2)
        first_group = groups[0]
        self.assertEqual(first_group["nodes_list"], ["node1"])
        self.assertEqual(first_group["nodes"], 1)
        self.assertEqual(first_group["abc"], "zzz")
        second_group = groups[1]
        self.assertEqual(second_group["nodes_list"], ["node2"])
        self.assertEqual(second_group["nodes"], 1)
        self.assertEqual(second_group["abc"], "xyz")

    def test_ignore_known_problem_configuration_fields(self):
        """garballed output sper60. this was a known issue but is too annoying to ignore.
        to handle this we're going to skip any of the parameters that provide instances
        """
        conf_string = (
            "[aggregated_request_timeout_in_ms=120000; "
            + "audit_logging_options=com.datastax.bdp.db.audit.AuditLoggingOptions@31j0fa0; "
            + "cross_node_timeout=false; data_file_directories=[Ljava.lang.String;@31801f; "
            + "system_info_encryption=org.apache.cassandra.config.SystemTableEncryptionOptions@590c73d3; "
            + "transparent_data_encryption_options="
            + "org.apache.cassandra.config.TransparentDataEncryptionOptions@311d3a138a; "
            + "user_defined_function_fail_timeout=1500; user_defined_function_warn_timeout=500; "
            + "user_function_timeout_policy=die; windows_timer_interval=1; write_request_timeout_in_ms=2000]"
        )
        node_config_params = [x.split("=") for x in conf_string.split("; ")]
        node_config = {x[0]: x[1] for x in node_config_params}
        conf = config_diff.filter_unique_config_flags(node_config)
        self.assertIsNotNone(conf.get("user_defined_function_fail_timeout", "1500"))
        self.assertNotIn("system_info_encryption", conf)
        self.assertNotIn("data_file_directories", conf)
        self.assertNotIn("audit_logging_options", conf)
        self.assertNotIn("transparent_data_encryption_options", conf)
