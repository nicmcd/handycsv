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


class ColumnStats(object):
  """
  This represents a 1D structure of statistic values indexed by row.
  """

  def __init__(self):
    """
    Constructs a null ColumnStats.
    """
    self.csv = None
    self.rows = None
    self.row_index = None

  def __init_row_info(self):
    """
    Initializes the row values and index from the Csv object.
    """
    self.rows = self.csv.get_column(0)
    if len(set(self.rows)) != len(self.rows):
      raise ValueError('duplicate row name found')
    self.row_index = dict(zip(self.rows, range(len(self.rows))))

  @staticmethod
  def create(rows):
    """
    Constructs an empty column structure.
    Fills all locations with ''

    Args:
      row [int, float, str] : the row specifiers
    """
    stats = ColumnStats()
    stats.csv = Csv(row_lengths=[2] * len(rows))
    for index, row in enumerate(list(rows)):
      stats.csv.set(index, 0, row)
    stats.__init_row_info()
    return stats

  @staticmethod
  def make_from_csv(csv):
    """
    Creates a ColumnStats using the given Csv object.

    Args:
      csv (Csv) : the Csv object used to create the ColumnStats
      source    : (optional) the source of the CSV data
    """
    stats = ColumnStats()
    stats.csv = csv
    if not stats.csv.is_rectangular:
      raise ValueError('ColumnStats must be rectangular')
    if stats.csv.num_columns(0) != 2:
      raise ValueError('ColumnStats have 2 columns per row')
    stats.__init_row_info()
    return stats

  @staticmethod
  def load(text, transpose=False):
    """
    Constructs a ColumnStats from a string
    Values default to int, then float, then str

    Args:
      text      (str)  : text of the grid
      transpose (bool) : to transpose the input
    """
    csv = Csv.load(text, transpose=transpose)
    return ColumnStats.make_from_csv(csv)

  @staticmethod
  def read(filename, transpose=False):
    """
    Constructs a ColumnStats from a CSV file
    Values default to int, then float, then str

    Args:
      filename  (str)  : name of file to open (auto .gz if given)
      transpose (bool) : to transpose the input
    """
    csv = Csv.read(filename, transpose=transpose)
    return ColumnStats.make_from_csv(csv)

  @property
  def source(self):
    return self.csv.source

  def row_names(self):
    """
    Returns list of row names
    """
    return self.rows

  def __eq__(self, other):
    """
    Tests for equivalence to another ColumnStats. Ignores 'source'.
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
    Write the ColumnStats to a CSV file

    Args:
      filename (str)   : name of file to write (auto .gz if given)
      transpose (bool) : transpose the ColumnStats before writing
    """
    self.csv.write(filename, transpose=transpose)

  def get(self, row, default=None):
    """
    Gets a value by reference of row

    Args:
      row     : row specifier
      default : default value to return if none exists

    Returns:
      value in grid
    """
    try:
      return self.csv.get(self.row_index[row], 1)
    except KeyError:
      pass
    if default is not None:
      return default
    else:
      raise IndexError('row={0} doesn\'t exist'.format(row))

  def set(self, row, value):
    """
    Sets a value by reference of row

    Args:
      row     : row specifier
      value   : value to be set
    """
    try:
      self.csv.set(self.row_index[row], 1, value)
    except KeyError:
      raise IndexError('row={0} doesn\'t exist'.format(row))

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

  def filter_rows(self, regex, invert=False):
    """
    This filter the data into a subset. It removes rows wherein the value
    matches the specified regular expression. If invert is False only the
    matching rows will be retained. If invert is True only the non matching
    rows will be retained.

    Args:
      regex  (str) : the regular expression to match

    Returns:
      removed ([str]) : the removed row identifiers
    """
    # check all rows
    removed = []
    for row in self.row_names():
      # determine if matched
      value_str = str(self.get(row))
      matched = re.match(regex, value_str)

      # mark to remove based on matched and invert
      if (not invert and matched) or (invert and not matched):
        removed.append(row)

    # remove the rows
    for row in removed:
      self.remove_row(row)

    return removed
