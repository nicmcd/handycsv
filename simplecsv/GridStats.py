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
import re


class GridStats(object):
  """
  This represents a 2D grid of statistics values indexed by row and column
  """

  def __init__(self):
    """
    Constructs a null grid
    """
    self.raw = None
    self.rows = {}
    self.cols = {}
    self.source = None

  def create(self, head, rows, cols):
    """
    Constructs an empty grid with the specified row and column names.

    Args:
      head (str)      : element of [0,0]
      rows (list/set) : names of rows
      cols (list/set) : names of cols
    """
    self.raw = None
    self.rows = {}
    self.cols = {}

    # add head to the beginning of cols
    cols = [head] + cols

    # initialize empty 2D array
    self.raw = []
    for row in range(len(rows) + 1):
      self.raw.append([''] * len(cols))

    # fill in row and column names
    for row in range(len(rows)):
      self.raw[row + 1][0] = rows[row]
    for col in range(len(cols)):
      self.raw[0][col] = cols[col]

    # create row/col index data structures
    for rowIdx in range(len(rows)):
      if rows[rowIdx] in self.rows:
        raise ValueError('duplicate row name detected')
      self.rows[rows[rowIdx]] = rowIdx + 1
    for colIdx in range(len(cols)):
      if cols[colIdx] in self.cols:
        raise ValueError('duplicate column name detected')
      self.cols[cols[colIdx]] = colIdx

  def load(self, text):
    """
    Constructs a 2D grid from a 2D string
    Values default to int, then float, then str

    Args:
      text (str) : text of the grid
    """
    self.raw = None
    self.rows = {}
    self.cols = {}

    # break text into lines
    lines = text.strip().split('\n')

    # break lines into raw data (columnar pieces)
    self.raw = []
    for line in lines:
      cols = line.split(',')
      cols = [x.strip() for x in cols]

      # check consistency
      if len(self.raw) > 0:
        if len(cols) != len(self.raw[0]):
          raise ValueError('number of columns is not constant')

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

      # push new row into rows list
      self.raw.append(cols)

    # create row/col index data structures
    for rowIdx in range(1, len(self.raw)):
      if self.raw[rowIdx][0] in self.rows:
        raise ValueError('duplicate row name detected')
      self.rows[self.raw[rowIdx][0]] = rowIdx
    if len(self.raw) > 0:
      for colIdx in range(1, len(self.raw[0])):
        if self.raw[0][colIdx] in self.cols:
          raise ValueError('duplicate column name detected')
        self.cols[self.raw[0][colIdx]] = colIdx

  def read(self, filename):
    """
    Constructs a 2D grid from a 2D CSV file
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

  def head(self):
    """
    Returns:
      the head string
    """
    # empty
    if len(self.raw) == 0:
      return None
    # filled
    return self.raw[0][0]

  def column_names(self):
    """
    Returns:
      list of column names
    """
    # empty
    if len(self.raw) == 0:
      return []
    # filled
    return [self.raw[0][colIdx] for colIdx in range(1, len(self.raw[0]))]

  def row_names(self):
    """
    Returns:
      list of row names
    """
    # empty
    if len(self.raw) == 0:
      return []
    # filled
    return [self.raw[rowIdx][0] for rowIdx in range(1, len(self.raw))]

  def write(self, filename):
    """
    Write the 2D grid to a 2D CSV file

    Args:
      filename (str) : name of file to write (auto .gz if given)
    """
    if self.raw == None:
      raise ValueError('unintialized grid can not be written to a file')

    # open file to write
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'wb') as fd:
      for row in self.raw:
        fd.write(bytes(','.join([str(x) for x in row]) + '\n', 'utf-8'))

  def get(self, row, col, default=None):
    """
    Gets a value by reference of row and column

    Args:
      row     : row specifier
      col     : col specifier
      default : default value to return if none exists

    Returns:
      value in grid
    """
    try:
      return self.raw[self.rows[row]][self.cols[col]]
    except:
      pass
    if default is not None:
      return default
    else:
      raise ValueError('row={0} col={1} doesn\'t exist'.format(row, col))

  def set(self, row, col, val):
    """
    Sets a value by reference of row and column

    Args:
      row     : row specifier
      col     : col specifier
      val     : value
    """
    self.raw[self.rows[row]][self.cols[col]] = val

  def get_column(self, col):
    """
    Retrieves a list of values from a full column

    Args:
      col     : col specifier

    Returns:
      (list)  : the values in the column
    """
    return [self.get(row, col) for row in self.row_names()]

  def remove_row(self, row):
    """
    This removes the specified row.

    Args:
      row (str) : the row identifier
    """
    if row not in self.rows:
      raise ValueError('row "{}" is not an existing row'.format(row))

    found = False
    for arow in list(self.rows.keys()):
      if arow == row:
        assert not found
        self.raw.pop(self.rows[row])
        self.rows.pop(row)
        found = True
      elif found:
        self.rows[arow] -= 1
    assert found

  def filter_rows(self, column, regex, invert=False):
    """
    This filter the data into a subset. It removes rows wherein the value of the
    identified column matches the specified regular expression. If invert is
    False only the matching rows will be retained. If invert is True only the
    non matching rows will be retained.

    Args:
      col (str)   : the column specifier
      regex (str) : the regular expression to match

    Returns:
      removed ([str]) : the removed row identifiers
    """
    if column not in self.cols:
      raise ValueError('column "{}" is not an existing column'.format(column))

    removed = []
    for row in self.row_names():
      # determine if matched
      value_str = str(self.get(row, column))
      matched = re.match(regex, value_str)

      # remove if applicable
      if (not invert and matched) or (invert and not matched):
        self.remove_row(row)
        removed.append(row)

    return removed
