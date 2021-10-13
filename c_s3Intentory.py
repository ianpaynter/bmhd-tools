import datetime
import numpy as np

class InvObject:

    def __init__(self):

        self.key_name = None
        self.size = None
        self.last_accessed = None

    # Flatten the object for saving
    def flatten(self):
        # Return output dictionary
        return {"key_name": self.key_name,
                "size": self.size,
                "last_accessed": f"{self.last_accessed.date()} {self.last_accessed.time()}"}

    # Load from line in s3 inventory csv
    def load_from_inventory(self, inv_line):
        self.key_name = inv_line[1].replace('"', '')
        self.size = int(inv_line[2].replace('"', ''))
        self.last_accessed = datetime.datetime.strptime(inv_line[3], '"%Y-%m-%dT%H:%M:%S.%fZ"')

    # Load from flattened dictionary in saved json
    def load_from_json(self, inv_dict):
        self.key_name = inv_dict['key_name']
        self.size = inv_dict['size']
        self.last_accessed = datetime.datetime.strptime(inv_dict['last_accessed'], '%Y-%m-%d %H:%M:%S')

class InventorySummary:

    def __init__(self):

        self.total_size = 0
        self.total_monthly_cost = 0
        self.total_objects = 0
        self.maximum_size = 0
        self.mean_size = 0

# Prettifying numbers for posting to slackbot
def prettify(number):
    # Convert the number to a string
    str_num = str(number)
    # If the number has a decimal
    if '.' in str_num:
        # Index the decimal
        end_ind = str_num.index('.')
    # Otherwise (no decimal)
    else:
        end_ind = len(str_num)
    # Take the length of the string up to that point
    str_len = len(str_num[0:end_ind])
    # Pretty string
    prettyString = ''
    # Get the bit before the first comma
    prettyString += str_num[0:str_len % 3]
    # For any remaining sections
    for sections in list(np.arange(0, np.floor(str_len / 3))):
        # Add a comma
        prettyString += ','
        # Add the section
        prettyString += str_num[int(str_len % 3 + (3 * sections)): int(str_len % 3 + 3 + (3 * sections))]
    # If there was a decimal
    if '.' in str_num:
        # Add the decimal section
        prettyString += str_num[end_ind:]
    # If there is a floating comma on the beginning (when the string is % 3 == 0 in length)
    if prettyString[0] == ',':
        # Remove it
        prettyString = prettyString[1:]
    # Return the string
    return prettyString
