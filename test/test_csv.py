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
import simplecsv
import unittest
import tempfile


class TestCsv(unittest.TestCase):

  @staticmethod
  def make_str(raw_vals):
    return ''.join(','.join([str(v) for v in row]) + '\n' for row in raw_vals)

  def check(self, csv, raw):
    # structure
    self.assertEqual(csv.num_rows(), len(raw))
    for row in range(csv.num_rows()):
      self.assertEqual(csv.num_columns(row), len(raw[row]))
    row_lens = csv.row_lengths()
    self.assertEqual(len(row_lens), len(raw))
    for index, row_len in enumerate(row_lens):
      self.assertEqual(row_len, len(raw[index]))

    # stringification
    self.assertEqual(str(csv), TestCsv.make_str(raw))

    # elements, get() and get_row()
    for row in range(csv.num_rows() + 1):
      if row == csv.num_rows():
        with self.assertRaises(IndexError):
          csv.num_columns(row)
        with self.assertRaises(IndexError):
          csv.get_row(row)
      else:
        self.assertEqual(csv.get_row(row), raw[row])
        if csv.num_columns(row) > 0:
          csv.get_row(row)[0] = 'foo'
          csv.get_row(row).append('bar')
          self.assertEqual(csv.get_row(row), raw[row])
        for col in range(csv.num_columns(row) + 1):
          with self.assertRaises(IndexError):
            csv.get(csv.num_rows(), 0)
          with self.assertRaises(IndexError):
            csv.get(csv.num_rows(), 0, default='foo')
          if col == csv.num_columns(row):
            with self.assertRaises(IndexError):
              csv.get(row, col)
          else:
            self.assertEqual(csv.get(row, col), raw[row][col])

    # copy and __eq__
    csv2 = csv.copy()
    self.assertTrue(csv.__eq__(csv2))
    self.assertEqual(csv, csv2)

  k4x2 = [
    ['-', 'a'],
    ['d', 0],
    ['e', 3],
    ['f', 6]
  ]

  def check_4x2(self, csv):
    self.check(csv, TestCsv.k4x2)

    # shape
    self.assertTrue(csv.is_rectangular())
    self.assertFalse(csv.is_square())

    # transpose
    csvt = csv.transpose()
    self.assertEqual(csvt.num_rows(), 2)
    self.assertEqual(csvt.num_columns(0), 4)
    self.assertEqual(csvt.get_row(0), ['-', 'd', 'e', 'f'])
    self.assertEqual(csvt.get_row(1), ['a', 0, 3, 6])

    # remove row
    with self.assertRaises(IndexError):
      csv.remove_row(4)
    csv.remove_row(1)
    self.assertEqual(csv.num_rows(), 3)
    self.assertEqual(csv.get_row(0), ['-', 'a'])
    self.assertEqual(csv.get_row(1), ['e', 3])
    self.assertEqual(csv.get_row(2), ['f', 6])

    # remove column
    with self.assertRaises(IndexError):
      csv.remove_column(2)
    csv.remove_column(1)
    self.assertEqual(csv.get_row(0), ['-'])
    self.assertEqual(csv.get_row(1), ['e'])
    self.assertEqual(csv.get_row(2), ['f'])

    # transpose (again)
    csvt = csv.transpose()
    self.assertEqual(csvt.num_rows(), 1)
    self.assertEqual(csvt.num_columns(0), 3)
    self.assertEqual(csvt.get_row(0), ['-', 'e', 'f'])

  k4x4 = [
    ['-', 'a', 'b', 'c'],
    ['d', 0, 1, 2],
    ['e', 3, 4, 5],
    ['f', 6, 7, 8]
  ]

  def check_4x4(self, csv):
    self.check(csv, TestCsv.k4x4)

    # shape
    self.assertTrue(csv.is_rectangular())
    self.assertTrue(csv.is_square())

    # transpose
    csvt = csv.transpose()
    self.assertEqual(csvt.num_rows(), 4)
    self.assertEqual(csvt.num_columns(0), 4)
    self.assertEqual(csvt.get_row(0), ['-', 'd', 'e', 'f'])
    self.assertEqual(csvt.get_row(1), ['a', 0, 3, 6])
    self.assertEqual(csvt.get_row(2), ['b', 1, 4, 7])
    self.assertEqual(csvt.get_row(3), ['c', 2, 5, 8])

    # remove row
    with self.assertRaises(IndexError):
      csv.remove_row(4)
    csv.remove_row(1)
    self.assertEqual(csv.num_rows(), 3)
    self.assertEqual(csv.get_row(0), ['-', 'a', 'b', 'c'])
    self.assertEqual(csv.get_row(1), ['e', 3, 4, 5])
    self.assertEqual(csv.get_row(2), ['f', 6, 7, 8])

    # remove column
    with self.assertRaises(IndexError):
      csv.remove_column(4)
    csv.remove_column(1)
    self.assertEqual(csv.get_row(0), ['-', 'b', 'c'])
    self.assertEqual(csv.get_row(1), ['e', 4, 5])
    self.assertEqual(csv.get_row(2), ['f', 7, 8])

    # transpose (again)
    csvt = csv.transpose()
    self.assertEqual(csvt.num_rows(), 3)
    self.assertEqual(csvt.num_columns(0), 3)
    self.assertEqual(csvt.get_row(0), ['-', 'e', 'f'])
    self.assertEqual(csvt.get_row(1), ['b', 4, 7])
    self.assertEqual(csvt.get_row(2), ['c', 5, 8])

  kIrregular = [
    ['-', 'a', 'b', 'c'],
    ['d', 0],
    [''],
    ['e', 3, 4, 5],
    ['f', '', 7]
  ]

  def check_irregular(self, csv):
    self.check(csv, TestCsv.kIrregular)

    # shape
    self.assertFalse(csv.is_rectangular())
    self.assertFalse(csv.is_square())

    # transpose
    with self.assertRaises(IndexError):
      csv.transpose()

    # remove row
    with self.assertRaises(IndexError):
      csv.remove_row(5)
    csv.remove_row(1)
    self.assertEqual(csv.num_rows(), 4)
    self.assertEqual(csv.get_row(0), ['-', 'a', 'b', 'c'])
    self.assertEqual(csv.get_row(1), [''])
    self.assertEqual(csv.get_row(2), ['e', 3, 4, 5])
    self.assertEqual(csv.get_row(3), ['f', '', 7])

    # remove column
    with self.assertRaises(IndexError):
      csv.remove_column(0)
    with self.assertRaises(IndexError):
      csv.remove_column(1)

    # transpose (again)
    with self.assertRaises(IndexError):
      csv.transpose()

  kEmpty = [['']]

  def check_empty(self, csv):
    self.check(csv, TestCsv.kEmpty)

    # shape
    self.assertTrue(csv.is_rectangular())
    self.assertTrue(csv.is_square())

    # transpose
    csvt = csv.transpose()
    self.check(csvt, TestCsv.kEmpty)

    # remove row
    with self.assertRaises(IndexError):
      csv.remove_row(0)

    # remove column
    with self.assertRaises(IndexError):
      csv.remove_column(0)
    with self.assertRaises(IndexError):
      csv.remove_column(1)

  def test_full(self):
    # default constructor test
    csv = simplecsv.Csv()
    self.check(csv, TestCsv.kEmpty)
    csv = simplecsv.Csv(row_lengths=[1])
    self.check(csv, TestCsv.kEmpty)

    # bad constructor args
    with self.assertRaises(ValueError):
      simplecsv.Csv(row_lengths=[])
    with self.assertRaises(ValueError):
      simplecsv.Csv(row_lengths=[0])
    with self.assertRaises(ValueError):
      simplecsv.Csv(row_lengths=[1, 0, 2])

    # specific test sweeps
    tests = [
      (TestCsv.k4x2, self.check_4x2),
      (TestCsv.k4x4, self.check_4x4),
      (TestCsv.kIrregular, self.check_irregular),
      (TestCsv.kEmpty, self.check_empty)
    ]

    for raw, checker in tests:
      # create the regular and gzipped version
      _, plain_file = tempfile.mkstemp(prefix='TestCsv', suffix='.csv')
      with open(plain_file, 'w') as fd:
        fd.write(TestCsv.make_str(raw))
      os.system('gzip -k {}'.format(plain_file))
      compressed_file = plain_file + '.gz'
      self.assertTrue(os.path.isfile(compressed_file))

      # read, check, write, and remove
      for csvfile in [plain_file, compressed_file]:
        # read
        csv = simplecsv.Csv.read(csvfile)

        # check
        self.assertEqual(csv.source, csvfile)
        checker(csv)

        # write
        _, plain_file2 = tempfile.mkstemp(prefix='TestCsv', suffix='.csv')
        os.remove(plain_file2)
        compressed_file2 = plain_file2 + '.gz'
        for outfile in [plain_file2, compressed_file2]:
          # write
          csv.write(outfile)

          # read
          csv2 = simplecsv.Csv.read(outfile)

          # check
          self.assertEqual(str(csv2), str(csv))

          # remove
          os.remove(outfile)

        # remove
        os.remove(csvfile)

    # strip trailing new lines
    tests = [
      ('a,b\nc\n\n\n', 'a,b\nc\n'),
      ('\n\n\n\n', '\n'),
    ]
    for intext, outtext in tests:
      # create plain and compressed versions
      _, plain_file = tempfile.mkstemp(prefix='TestCsv', suffix='.csv')
      with open(plain_file, 'w') as fd:
        fd.write(intext)
      os.system('gzip -k {}'.format(plain_file))
      compressed_file = plain_file + '.gz'
      self.assertTrue(os.path.isfile(compressed_file))

      # read, check, and remove
      for csvfile in [plain_file, compressed_file]:
        # read
        csv = simplecsv.Csv.read(csvfile)

        # check
        self.assertEqual(str(csv), outtext)

        # remove
        os.remove(csvfile)
