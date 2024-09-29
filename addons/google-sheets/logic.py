import gspread
from oauth2client.service_account import ServiceAccountCredentials

from src.serializers import *
from src.global_vars import *

def colnum_to_colletter(col_num):
    """Convert a column number (1-based) to a column letter."""
    col_letter = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
        return col_letter

def to_number(self, column_str : str):
    index = 0
    column_str = column_str.lower().strip()
    for c in column_str:
        index *= 26
        index += ord(c)-ord('a') + 1
    return index

class gsheets:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(config['addons/gsheets/key-file'], scope)
        
        self.settings = SerializedJSON(json_file=config['addons/gsheets/addon-config'])

        self.marksCache = {}
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(self.settings['marksheet-name'])
        self.sheet = self.spreadsheet.get_worksheet(0)
        self.categories = self.get_categories()[0]

    def get_categories(self):
        # Get the categories from the 2nd row and return a dictionary mapping names to column letters
        categories = self.sheet.row_values(2)
        
        return {category: colnum_to_colletter(idx + 1) for idx, category in enumerate(categories)}, categories

    def update_marks(self, roll_no, category, marks):
        msg = ''
        
        # Get the column index for the category
        category_index = to_number(self.categories.get(category))
        if category_index is None:
            msg = f"Category '{category}' not found in the sheet."
            raise ValueError(f"Category '{category}' not found in the sheet.")
        
        # Find the row index for the student roll-no
        roll_column = self.sheet.col_values(1)
        try:
            student_row = roll_column.index(roll_no) + 1
            student_data = self.userDatabase.getUser(rollno = roll_no.lower().strip())
            msg = f"Student: '{student_data.name}'\nMarks: '{marks}' added successfully to category: {category}"
        except ValueError as e:
            msg = f"Roll No '{roll_no}' not found in the sheet."
            raise ValueError(f"Roll No '{roll_no}' not found in the sheet. Details: {e}")
        
        # Retrieve the current marks from the cell
        current_marks = self.sheet.cell(student_row, category_index).value
        
        # Convert current marks to a number, defaulting to 0 if empty or non-numeric
        try:
            current_marks = float(current_marks) if current_marks else 0
        except ValueError:
            current_marks = 0

        # Calculate the new total marks
        new_marks = current_marks + marks
        
        # Update the cell with the new marks
        self.sheet.update_cell(student_row, category_index, new_marks)

        # Invalidate cache
        if roll_no in self.cache:
            del self.cache[roll_no]

        return msg

    def add_category(self, new_category):
        # Add a new category to the 2nd row
        self.sheet.update_cell(2, len(self.categories) + 1, new_category)
        # Refresh categories after adding a new one
        self.categories = self.get_categories()

    def add_student(self, roll_no, student_name):
        # Add a new student to the first available row
        next_row = len(self.sheet.col_values(1)) + 1
        self.sheet.update_cell(next_row, 1, roll_no)
        self.sheet.update_cell(next_row, 2, student_name)

    def get_student_marks(self, roll_no):
        student_data, msg = self.find_student(roll_no)
        if msg:
            raise ValueError(msg)

        # Retrieve marks from the student row
        marks = student_data[2:]  # Assumes marks start from the 3rd column #TODO: Change this in the future maybe?

        # Create a dictionary mapping category names to marks
        student_marks = {category: mark for category, mark in zip(self.categories, marks)}

        return student_marks
     # Exclude roll-no and name

    def get_all_data(self):
        # Retrieve all data from the sheet
        return self.sheet.get_all_values()

    def save_categories(self):
        # Save the categories in case they were modified
        self.sheet.insert_row(self.categories.keys(), 2)

    def refresh_categories(self):
        # Refresh the categories from the sheet in case of external changes
        self.categories = self.get_categories()

    def find_student(self, user: User):
        roll_no = user.rollno #Kinda Obv isn't it?
        
        if roll_no in self.cache:
            return self.cache[roll_no]

        # Get the column containing roll numbers
        roll_column = self.sheet.col_values(1)

        msg = ''

        try:
            student_row = roll_column.index(roll_no.upper()) + 1
        except ValueError:
            msg = f"Roll No '{roll_no}' not found in the sheet."
            raise ValueError(f"Roll No '{roll_no}' not found in the sheet.")
        
        # Retrieve the student's data (excluding the roll-no and name)
        student_data = self.sheet.row_values(student_row)

        if not msg:
            self.cache[roll_no] = student_data

        # Return the student's data
        return student_data, msg

