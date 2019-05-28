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

import gzip

class ColumnStats(object):
  """
  This represents a 1D structure of statistic values indexed by row
  """

  def __init__(self):
    """
    Constructs a null structure
    """
    self.raw = {}
    self.source = None

  def create(self, rows):
    """
    Constructs an empty structure with the specified row names.

    Args:
      rows (list/set) : names of rows
    """
    self.raw = {}
    self.source = None
    for row in rows:
      self.raw[row] = None

  def load(self, text):
    """
    Constructs a statistics structure from 1D CSV txt.
    Values default to int, then float, then str

    Args:
      text (str) : 1D CSV txt
    """
    self.raw = {}

    # break text into lines
    lines = text.split('\n')

    # break lines into raw data (columnar pieces)
    for line in lines:
      cols = line.split(',')
      cols = [x.strip() for x in cols]

      # check consistency
      if len(self.raw) > 0:
        if len(cols) != 2:
          raise ValueError('number of columns is not constantly 2')

      # transform values
      for idx in range(0, len(cols)):
        col = cols[idx]
        try:
          col = int(col)
        except ValueError:
          try:
            col = float(col)
          except ValueError:
            col = str(col)
        cols[idx] = col

      # push new row into raw
      self.raw[cols[0]] = cols[1]

  def read(self, filename):
    """
    Constructs a statistics structure from a 1D CSV file
    Values default to int, then float, then str

    Args:
      filename (str) : name of file to open (auto .gz if given)
    """
    self.source = filename

    # open file and get all lines
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'rb') as fd:
      text = fd.read().decode('utf-8')
    return self.load(text)

  def row_names(self):
    """
    Returns:
      list of row names
    """
    return list(self.raw.keys)

  def write(self, filename):
    """
    Write the statisitcs to a 1D CSV file

    Args:
      filename (str) : name of file to write (auto .gz if given)
    """
    # open file to write
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'wb') as fd:
      for key in self.raw.keys():
        fd.write(bytes('{0},{1}\n'.format(key, self.raw[key]), 'utf-8'))

  def get(self, row, default=None):
    """
    Gets a value by reference of row and column

    Args:
      row     : row specifier
      default : default value to return if none exists

    Returns:
      value in grid
    """
    if row in self.raw:
      return self.raw[row]
    else:
      if default is not None:
        return default
      else:
        raise ValueError('row={0} doesn\'t exist'.format(row))

  def set(self, row, val):
    """
    Sets a value by reference of row

    Args:
      row     : row specifier
      col     : col specifier
    """
    self.raw[row] = val
