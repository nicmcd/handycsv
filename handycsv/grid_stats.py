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
import gzip
import re

from .csv import Csv


class GridStats(object):
  """
  This represents a 2D grid of statistics values indexed by row and column.
  """

  def __init__(self):
    """
    Constructs a null GridStats.
    """
    self.csv = None
    self.rows = None
    self.row_index = None
    self.columns = None
    self.column_index = None

  def __init_row_info(self):
    """
    Initializes the row values and index from the Csv object.
    """
    self.rows = self.csv.get_column(0)[1:]
    if len(set(self.rows)) != len(self.rows):
      raise ValueError('duplicate row name found')
    self.row_index = dict(zip(self.rows, range(1, len(self.rows) + 1)))

  def __init_column_info(self):
    """
    Initializes the column values and index from the Csv object.
    """
    self.columns = self.csv.get_row(0)[1:]
    if len(set(self.columns)) != len(self.columns):
      raise ValueError('duplicate column name found')
    self.column_index = dict(zip(self.columns, range(1, len(self.columns) + 1)))

  @staticmethod
  def create(head, rows, columns):
    """
    Constructs an empty grid structure.
    Fills all locations with ''

    Args:
      head    (int, float, str) : the head value
      row     [int, float, str] : the row specifiers
      columns [int, float, str] : the column specifiers
    """
    stats = GridStats()
    stats.csv = Csv(row_lengths=[len(columns) + 1] * (len(rows) + 1))
    stats.csv.set(0, 0, head)
    for index, row in enumerate(list(rows)):
      stats.csv.set(index + 1, 0, row)
    for index, col in enumerate(list(columns)):
      stats.csv.set(0, index + 1, col)
    stats.__init_row_info()
    stats.__init_column_info()
    return stats

  @staticmethod
  def make_from_csv(csv):
    """
    Creates a GridStats using the given Csv object.

    Args:
      csv (Csv) : the Csv object used to create the GridStats
    """
    stats = GridStats()
    stats.csv = csv
    if not stats.csv.is_rectangular:
      raise ValueError('GridStats must be rectangular')
    stats.__init_row_info()
    stats.__init_column_info()
    return stats

  @staticmethod
  def load(text, transpose=False):
    """
    Constructs a GridStats from a string
    Values default to int, then float, then str

    Args:
      text      (str)  : text of the grid
      transpose (bool) : to transpose the input
    """
    csv = Csv.load(text, transpose=transpose)
    return GridStats.make_from_csv(csv)

  @staticmethod
  def read(filename, transpose=False):
    """
    Constructs a GridStats from a CSV file
    Values default to int, then float, then str

    Args:
      filename  (str)  : name of file to open (auto .gz if given)
      transpose (bool) : to transpose the input
    """
    csv = Csv.read(filename, transpose=transpose)
    return GridStats.make_from_csv(csv)

  @property
  def source(self):
    return self.csv.source

  def head(self):
    """
    Returns the head value
    """
    return self.csv.get(0, 0)

  def row_names(self):
    """
    Returns list of row names
    """
    return self.rows

  def column_names(self):
    """
    Returns list of column names
    """
    return self.columns

  def __eq__(self, other):
    """
    Tests for equivalence to another GridStats. Ignores 'source'.
    """
    return self.csv == other.csv

  def __str__(self):
    """
    Returns the string representation in CSV format.
    """
    return str(self.csv)

  def pretty(self, precision=None, right_align=False):
    """
    Returns a pretty string.
    """
    return self.csv.pretty(precision=precision, right_align=right_align)

  def write(self, filename, transpose=False):
    """
    Write the GridStats to a CSV file

    Args:
      filename (str)   : name of file to write (auto .gz if given)
      transpose (bool) : transpose the ColumnStats before writing
    """
    self.csv.write(filename, transpose=transpose)

  def get(self, row, column, default=None):
    """
    Gets a value by reference of row and column

    Args:
      row     : row specifier
      column  : column specifier
      default : default value to return if none exists

    Returns:
      value in grid
    """
    try:
      return self.csv.get(self.row_index[row], self.column_index[column])
    except KeyError:
      pass
    if default is not None:
      return default
    else:
      raise IndexError('row={0} column={1} doesn\'t exist'.format(row, column))

  def set(self, row, column, value):
    """
    Sets a value by reference of row and column

    Args:
      row     : row specifier
      column  : column specifier
      value   : value to be set
    """
    try:
      self.csv.set(self.row_index[row], self.column_index[column], value)
    except KeyError:
      raise IndexError('row={0} column={1} doesn\'t exist'.format(row, column))

  def get_row(self, row):
    """
    Retrieves a list of values from a full row

    Args:
      row : row specifier

    Returns:
      (list)  : the values in the row
    """
    try:
      return self.csv.get_row(self.row_index[row])[1:]
    except KeyError:
      raise IndexError('row={0} doesn\'t exist'.format(row))

  def get_column(self, column):
    """
    Retrieves a list of values from a full column

    Args:
      column : column specifier

    Returns:
      (list)  : the values in the column
    """
    try:
      return self.csv.get_column(self.column_index[column])[1:]
    except KeyError:
      raise IndexError('column={0} doesn\'t exist'.format(column))

  def remove_row(self, row):
    """
    This removes the specified row.

    Args:
      row (str) : the row identifier
    """
    try:
      row_index = self.row_index[row]
    except KeyError:
      raise IndexError('row={0} doesn\'t exist'.format(row))
    self.csv.remove_row(row_index)
    self.__init_row_info()

  def filter_rows(self, column, regex, invert=False):
    """
    This filter the data into a subset. It removes rows wherein the value of the
    identified column matches the specified regular expression. If invert is
    False only the matching rows will be retained. If invert is True only the
    non matching rows will be retained.

    Args:
      column (str) : the column specifier
      regex  (str) : the regular expression to match

    Returns:
      removed ([str]) : the removed row identifiers
    """
    if column not in self.column_index:
      raise IndexError('column "{}" is not an existing column'.format(column))

    # check all rows
    removed = []
    for row in self.row_names():
      # determine if matched
      value_str = str(self.get(row, column))
      matched = re.match(regex, value_str)

      # mark to remove based on matched and invert
      if (not invert and matched) or (invert and not matched):
        removed.append(row)

    # remove the rows
    for row in removed:
      self.remove_row(row)

    return removed

  def transpose(self):
    """
    Returns a tranpose of this GridStats object.
    """
    return GridStats.make_from_csv(self.csv.transpose())
