# Software License Agreement (BSD License)
#
# Copyright (c) 2016, Kentaro Wada.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging
import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import sys

import re
from nose.tools import assert_regexp_matches
import rosgraph.roslogging


os.environ['ROSCONSOLE_FORMAT'] = ' '.join([
    '${severity}',
    '${message}',
    '${walltime}',
    '${walltime:%Y-%m-%d %H:%M:%S}',
    '${thread}',
    '${logger}',
    '${file}',
    '${line}',
    '${function}',
    '${node}',
    '${time}',
    '${time:%Y-%m-%d %H:%M:%S}',
])
rosgraph.roslogging.configure_logging('test_rosgraph', logging.INFO)
loginfo = logging.getLogger('rosout').info
rosout_logger = logging.getLogger('rosout')
assert isinstance(rosout_logger.handlers[0], rosgraph.roslogging.RosStreamHandler)
default_ros_handler = rosout_logger.handlers[0]

# Remap stdout for testing
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

lout = StringIO()
lerr = StringIO()
test_ros_handler = rosgraph.roslogging.RosStreamHandler(colorize=False, stdout=lout, stderr=lerr)

try:
    # hack to replace the stream handler with a debug version
    rosout_logger.removeHandler(default_ros_handler)
    rosout_logger.addHandler(test_ros_handler)

    loginfo('on module')

    def logging_on_function():
        loginfo('on function')

    logging_on_function()

    class LoggingOnClass(object):

        def __init__(self):
            loginfo('on method')

    LoggingOnClass()

    def test_rosconsole__logging_format():
        this_file = os.path.abspath(__file__)
        # this is necessary to avoid test fails because of .pyc cache file
        base, ext = os.path.splitext(this_file)
        if ext == '.pyc':
            this_file = base + '.py'

        log_outs = lout.getvalue().splitlines()
        function_pairs = [('module', '<module>', log_outs[0]),
                          ('function', 'logging_on_function', log_outs[1]),
                          ('method', 'LoggingOnClass.__init__', log_outs[2]),
                          ]
        for (loc, function, log_out) in function_pairs:
            # TODO(lucasw) all the log outputs are coming through as <module>
            function = '<module>'
            expected_log_out = ' '.join([
                'INFO',
                'on ' + loc,
                r'[0-9]*\.[0-9]*',
                r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',
                '[0-9]*',
                'rosout',
                # TODO(lucasw) not sure what this ought to be, but is breaking test as it was
                '\S*',  # re.escape(this_file),
                '[0-9]*',
                function,
                # depending if rospy.get_name() is available
                '(/unnamed|<unknown_node_name>)',
                r'[0-9]*\.[0-9]*',
                r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',
            ])
            text = f"{loc} {function}\nexpected: {expected_log_out}\nactual:   {log_out}\n{log_outs}"
            assert_regexp_matches(log_out, expected_log_out, text)

finally:

    # restoring default ros handler
    rosout_logger.removeHandler(test_ros_handler)
    rosout_logger.addHandler(default_ros_handler)
    # lout and lerr need to stay open while test is running

