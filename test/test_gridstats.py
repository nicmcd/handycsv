"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import handycsv
import unittest
import tempfile


class TestGridStats(unittest.TestCase):

  @staticmethod
  def make_str(raw_vals):
    return ''.join(','.join([str(v) for v in row]) + '\n' for row in raw_vals)

  k4x4 = [
    ['-', 'a', 'b', 'c'],
    ['d', 0, 1, 2],
    ['e', 3, 4, 5],
    ['f', 6, 7, 8]
  ]

  def test_handy(self):
    text = TestGridStats.make_str(TestGridStats.k4x4)

    stats = handycsv.GridStats.load(text)
    self.assertEqual(stats.row_names(), ['d', 'e', 'f'])
    self.assertEqual(stats.column_names(), ['a', 'b', 'c'])
    self.assertEqual(stats.get('d', 'c'), 2)
    self.assertEqual(stats.get('f', 'b'), 7)

    with self.assertRaises(IndexError):
      stats.get('d', 'z')
    with self.assertRaises(IndexError):
      stats.get('z', 'b')

    self.assertEqual(str(stats), text)

    with self.assertRaises(IndexError):
      stats.set('d', 'z', 99)
    with self.assertRaises(IndexError):
      stats.set('z', 'b', 99)

    self.assertEqual(stats.get_row('d'), [0, 1, 2])
    self.assertEqual(stats.get_row('f'), [6, 7, 8])
    with self.assertRaises(IndexError):
      stats.get_row('z')

    self.assertEqual(stats.get_column('a'), [0, 3, 6])
    self.assertEqual(stats.get_column('c'), [2, 5, 8])
    with self.assertRaises(IndexError):
      stats.get_column('z')

    stats.set('d', 'c', 20)
    stats.set('f', 'b', 70)
    self.assertEqual(stats.row_names(), ['d', 'e', 'f'])
    self.assertEqual(stats.column_names(), ['a', 'b', 'c'])
    self.assertEqual(stats.get('d', 'c'), 20)
    self.assertEqual(stats.get('f', 'b'), 70)

    with self.assertRaises(IndexError):
      stats.remove_row('z')

    stats.remove_row('e')
    self.assertEqual(stats.row_names(), ['d', 'f'])
    self.assertEqual(stats.column_names(), ['a', 'b', 'c'])
    self.assertEqual(stats.get('d', 'c'), 20)
    self.assertEqual(stats.get('f', 'b'), 70)
    with self.assertRaises(IndexError):
      stats.get_row('e')
    with self.assertRaises(IndexError):
      stats.get('e', 'b')

    stats = handycsv.GridStats.load(text)

    with self.assertRaises(IndexError):
      stats.filter_rows('z', '4')
    with self.assertRaises(IndexError):
      stats.filter_rows('z', '4', invert=False)
    with self.assertRaises(IndexError):
      stats.filter_rows('z', '4', invert=True)

    self.assertEqual(stats.filter_rows('b', '4'), ['e'])
    self.assertEqual(stats.row_names(), ['d', 'f'])
    self.assertEqual(stats.column_names(), ['a', 'b', 'c'])
    self.assertEqual(stats.get('d', 'c'), 2)
    self.assertEqual(stats.get('f', 'b'), 7)
    with self.assertRaises(IndexError):
      stats.get_row('e')
    with self.assertRaises(IndexError):
      stats.get('e', 'b')

    stats = handycsv.GridStats.load(text)
    stats.set('d', 'b', 'foo')
    self.assertEqual(stats.filter_rows('b', '\d'), ['e', 'f'])

    stats = handycsv.GridStats.load(text)
    stats.set('d', 'b', 'foo')
    self.assertEqual(stats.filter_rows('b', '\d', invert=True), ['d'])

    stats = handycsv.GridStats.load(text)
    self.assertEqual(stats.filter_rows('b', 'foo'), [])

    stats = handycsv.GridStats.load(text)
    self.assertEqual(stats.filter_rows('b', 'foo', invert=True),
                     ['d', 'e', 'f'])

    stats = handycsv.GridStats.load(text)
    stats_t = stats.transpose()
    self.assertEqual(stats_t.row_names(), ['a', 'b', 'c'])
    self.assertEqual(stats_t.column_names(), ['d', 'e', 'f'])
    self.assertEqual(stats_t.get('c', 'd'), 2)
    self.assertEqual(stats_t.get('b', 'f'), 7)

    for ext in ['.csv', '.csv.gz']:
      _, csvfile1 = tempfile.mkstemp(prefix='TestGridStats', suffix=ext)
      _, csvfile2 = tempfile.mkstemp(prefix='TestGridStats', suffix=ext)
      stats.write(csvfile1, transpose=True)
      stats_t.write(csvfile2, transpose=True)

      self.assertEqual(handycsv.GridStats.read(csvfile1).source, csvfile1)
      self.assertEqual(handycsv.GridStats.read(csvfile2).source, csvfile2)

      self.assertEqual(stats, handycsv.GridStats.read(csvfile2))
      self.assertEqual(stats_t, handycsv.GridStats.read(csvfile1))

      self.assertEqual(stats,
                       handycsv.GridStats.read(csvfile1, transpose=True))
      self.assertEqual(stats_t,
                       handycsv.GridStats.read(csvfile2, transpose=True))

      os.remove(csvfile1)
      os.remove(csvfile2)

    skeleton = handycsv.GridStats.create('-', ['d', 'e', 'f'], ['a', 'b', 'c'])
    stats = handycsv.GridStats.load(text)
    self.assertEqual(skeleton.head(), stats.head())
    self.assertEqual(skeleton.row_names(), stats.row_names())
    self.assertEqual(skeleton.column_names(), stats.column_names())
