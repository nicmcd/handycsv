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
import copy
import gzip


class Csv(object):
  """
  This represents CSV file, a list if comma separated values.
  """

  def __init__(self, row_lengths=None, source=None):
    """
    Constructs an empty CSV with the specified row lengths.

    Args:
      row_lengths [int] : a list of ints for each row length
    """
    self.raw = []
    self._source = source

    if row_lengths is None:
      row_lengths = [1]
    else:
      if len(row_lengths) == 0:
        raise ValueError('must specifiy at least one row')
    for row_length in row_lengths:
      if row_length < 1:
        raise ValueError('rows must be >= 1 elements')
      self.raw.append([''] * row_length)

  @staticmethod
  def autotype(value):
    """
    Transforms the value automatically into an int, float, str
    """
    try:
      return int(value)
    except ValueError:
      try:
        return float(value)
      except ValueError:
        return str(value)

  @staticmethod
  def load(text, transpose=False):
    """
    Constructs a CSV from a string.
    Values default to int, then float, then str.

    Args:
      text (str)       : text of the Csv
      transpose (bool) : to transpose the Csv
    """
    csv = Csv()
    csv.raw = []

    # break text into lines
    lines = text.strip().split('\n')

    # break lines into raw data (columnar pieces)
    for line in lines:
      columns = line.split(',')
      columns = [x.strip() for x in columns]

      # transform values
      for idx in range(0, len(columns)):
        columns[idx] = Csv.autotype(columns[idx])

      # push new row into rows list
      csv.raw.append(columns)

    # transpose if required
    if transpose:
      csv = csv.transpose()

    return csv

  @staticmethod
  def read(filename, transpose=False):
    """
    Constructs a CSV from a CSV file.
    Values default to int, then float, then str.

    Args:
      filename (str)   : name of file to open (auto .gz if given)
      transpose (bool) : to transpose the Csv
    """
    # open file and get all lines
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'rb') as fd:
      text = fd.read().decode('utf-8')
    csv = Csv.load(text, transpose)
    csv._source = filename
    return csv

  @property
  def source(self):
    return self._source

  def copy(self):
    """Returns a copy of this CSV."""
    csv = Csv()
    csv.raw = copy.deepcopy(self.raw)
    csv._source = self._source
    return csv

  def num_rows(self):
    """
    Returns the number of rows.
    """
    return len(self.raw)

  def num_columns(self, row):
    """
    Return the number of columns for a specific row.

    Args:
      row (int) : row index
    """
    return len(self.raw[row])

  def row_lengths(self):
    """
    Returns a list of ints for row lengths.
    """
    return [len(self.raw[row]) for row in range(len(self.raw))]

  def __eq__(self, other):
    """
    Tests for equivalence to another Csv. Ignores 'source'.
    """
    return self.raw == other.raw

  def __str__(self):
    """
    Returns the string representation in CSV format.
    """
    csv = ''
    for row in self.raw:
      csv += ','.join([str(x) for x in row]) + '\n'
    return csv

  def pretty(self, precision=None, right_align=False):
    """
    Returns a pretty string representation.

    Args:
      precision (None or int) : precision of floating point values if specified
      right_align (bool) : use right alignment instead of left alignment
    """
    def stringify(x):
      if isinstance(x, float) and precision is not None:
        return ('{:.' + str(precision) + 'f}').format(x)
      else:
        return str(x)

    # Creates a properly stringified copy
    raw = []
    for r in range(len(self.raw)):
      raw.append([])
      for c in range(len(self.raw[r])):
        raw[r].append(stringify(self.get(r, c)))

    # Computes the max text width of each column
    max_columns = max(len(r) for r in raw)
    widths = [-1] * max_columns
    for r in range(len(raw)):
      for c in range(len(raw[r])):
        widths[c] = max(widths[c], len(raw[r][c]))

    # Modifies the string values with whitespace
    for r in range(len(raw)):
      for c in range(len(raw[r])):
        spaces = widths[c] - len(raw[r][c])
        assert spaces >= 0, 'Programmer error!!!'
        if spaces == 0:
          continue
        whitespace = ' ' * spaces
        if right_align:
          raw[r][c] = whitespace + raw[r][c]
        else:
          raw[r][c] = raw[r][c] + whitespace

    # Creates the final string
    pcsv = ''
    for row in raw:
      pcsv += (' '.join(row)).rstrip() + '\n'
    return pcsv

  def write(self, filename, transpose=False):
    """
    Write the CSV to a file.

    Args:
      filename (str)   : name of file to write (auto .gz if given)
      transpose (bool) : transpose before writing
    """
    csv = self.transpose() if transpose else self

    if not csv.raw:
      raise ValueError('unintialized CSV can not be written to a file')

    # open file to write
    opener = gzip.open if filename.endswith('.gz') else open
    with opener(filename, 'wb') as fd:
      fd.write(bytes(csv.__str__(), 'utf-8'))

  def get_row(self, row):
    """
    Returns a whole row.

    Args:
      row (int) : row index
    """
    return copy.deepcopy(self.raw[row])

  def get(self, row, column, default=None):
    """
    Gets a value by reference of row and column.

    Args:
      row    (int) : row index
      column (int) : column index
      default      : default value if location is '' or None
    """
    val = self.raw[row][column]
    if val is None or val == '':
      if default is None:
        return val
      else:
        return default
    else:
      return val

  def set(self, row, column, value):
    """
    Sets a value by reference of row and column.

    Args:
      row    (int) : row index
      column (int) : column index
      value        : value
    """
    self.raw[row][column] = value

  def get_column(self, column):
    """
    Retrieves a list of values from a full column.
    Requires all rows to have this column.

    Args:
      column (int) : column index

    Returns:
      (list) : the values in the column
    """
    column_values = []
    for row in range(self.num_rows()):
      column_values.append(self.raw[row][column])
    return column_values

  def remove_row(self, row):
    """
    This removes the specified row.

    Args:
      row (int) : row index
    """
    if len(self.raw) < 2:
      raise IndexError('Can\'t remove the only row')
    self.raw.pop(row)

  def remove_column(self, column):
    """
    This removes the specified column.
    Requires all rows to have this column.

    Args:
      column (int) : column index
    """
    for row in range(self.num_rows()):
      if len(self.raw[row]) <= column:
        raise IndexError('row {} doesn\'t have column {}'.format(row, column))
      if len(self.raw[row]) == 1:
        raise IndexError('row {} only has one element, '
                         'removing the column would make an empty row'
                         .format(row))
    for row in range(self.num_rows()):
      self.raw[row].pop(column)

  def is_rectangular(self):
    """
    Return True iff the Csv is rectangular.
    This tests that all rows are equal length
    """
    return len(set(self.row_lengths())) == 1

  def is_square(self):
    """
    Returns True iff the Csv is square.
    """
    return self.is_rectangular() and self.num_rows() == self.num_columns(0)

  def transpose(self):
    """
    Returns a tranpose of this object.
    All rows must have equal lengths.
    """
    # Checks row length equivalence
    if not self.is_rectangular:
      raise IndexError('row length mismatch between {} and {}'.format(0, row))

    # Gets a tranpose of the structure
    raw = [[None for _ in range(len(self.raw))]
           for _ in range(len(self.raw[0]))]

    # Copies the elements
    for row in range(len(self.raw)):
      for column in range(len(self.raw[0])):
        raw[column][row] = self.raw[row][column]

    # Create the new object
    csv = Csv()
    csv.raw = raw

    return csv

  def sort(self, column_index, ignore_header=False, reverse=False):
    """
    Returns a sorted version of this CSV object

    Args:
      column_index (int)   : the column upon which to base the sorting
      ignore_header (bool) : keep the first row in place
      reverse (bool)       : reverse the sort operation
    """
    # Makes a list of tuples containing the field and the full row
    scored_rows = []
    for row_idx in range(self.num_rows()):
      row = self.get_row(row_idx)  # copies the row
      scored_rows.append((row[column_index], row))

    # This new raw values
    raw = []

    # Handles ignore header
    if ignore_header:
      _, row = scored_rows.pop(0)
      raw.append(row)

    # Sort the scored rows
    scored_rows.sort(reverse=reverse)
    while scored_rows:
      _, row = scored_rows.pop(0)
      raw.append(row)

    # Create the new object
    csv = Csv()
    csv.raw = raw

    return csv
