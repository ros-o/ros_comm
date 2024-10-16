# Software License Agreement (BSD License)
#
# Copyright (c) 2011, Willow Garage, Inc.
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

import os
import sys
import unittest

import roslib.packages

class RoslibSrvTest(unittest.TestCase):
  
    def test_SrvSpec(self):
        from roslib.msgs import MsgSpec
        from roslib.srvs import SrvSpec

        types = ['int32']
        names = ['a']
        constants = []
        text = 'int32 a'
        msg_a = MsgSpec(types, names, constants, text)

        types = ['int64']
        names = ['b']
        constants = []
        text = 'int64 b'
        msg_b = MsgSpec(types, names, constants, text)

        text = msg_a.text + '\n---\n' + msg_b.text
        spec = SrvSpec(msg_a, msg_b, text)
        self.assertEqual(msg_a, spec.request)
        self.assertEqual(msg_b, spec.response)
        self.assertEqual(text, spec.text)
        self.assertEqual('', spec.full_name)
        self.assertEqual('', spec.short_name)
        self.assertEqual('',spec.package)
        
        # tripwire
        self.assertTrue(repr(spec))
        self.assertTrue(str(spec))

        # exercise eq
        self.assertNotEqual(spec, 'spec')
        self.assertTrue(spec != 'spec')
        
        spec2 = SrvSpec(msg_a, msg_b, text)
        self.assertEqual(spec, spec2)
        self.assertFalse(spec != spec2)
        
        # - full_name
        spec2.full_name = 'something'
        self.assertNotEqual(spec, spec2)        
        spec2.full_name = ''        
        self.assertEqual(spec, spec2)
        # - short_name
        spec2.short_name = 'something'
        self.assertNotEqual(spec, spec2)        
        spec2.short_name = ''        
        self.assertEqual(spec, spec2)
        # - package
        spec2.package = 'something'
        self.assertNotEqual(spec, spec2)        
        spec2.package = ''        
        self.assertEqual(spec, spec2)
        
    def test_srv_file(self):
        from roslib.srvs import srv_file
        
        d = roslib.packages.get_pkg_dir('test_roslib_comm')
        filename = os.path.join(d, 'srv', 'AddTwoInts.srv')
        with open(filename, 'r') as f:
            text = f.read()

        self.assertEqual(filename, srv_file('test_roslib_comm', 'AddTwoInts'))
        
    def test_load_from_file(self):
        from roslib.srvs import load_from_file, set_verbose
        
        d = roslib.packages.get_pkg_dir('test_roslib_comm')
        filename = os.path.join(d, 'srv', 'AddTwoInts.srv')
        with open(filename, 'r') as f:
            text = f.read()
        
        name, spec = load_from_file(filename)
        self.assertEqual('AddTwoInts', name)
        self.assertEqual(['int64', 'int64'], spec.request.types)
        self.assertEqual(['a', 'b'], spec.request.names)
        self.assertEqual(text, spec.text)
        
        name2, spec2 = load_from_file(filename, package_context='foo')
        self.assertEqual('foo/AddTwoInts', name2)
        name2, spec2 = load_from_file(filename, package_context='foo/')
        self.assertEqual('foo/AddTwoInts', name2)
        name2, spec2 = load_from_file(filename, package_context='foo//')
        self.assertEqual('foo/AddTwoInts', name2)

        # test with verbose on
        set_verbose(True)
        name3, spec3 = load_from_file(filename)
        self.assertEqual(name, name3)
        self.assertEqual(spec, spec3)        

