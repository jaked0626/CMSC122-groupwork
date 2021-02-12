### CS122, Winter 2021: Course search engine: search
###
### Your name(s)

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day a list with variable number of elements
           -> ["'MWF'", "'TR'", etc.]
      - time_start an integer in the range 0-2359
      - time_end an integer in the range 0-2359
      - walking_time an integer
      - enroll_lower an integer
      - enroll_upper an integer
      - building a string
      - terms a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''
    
    from_join = from_function(filtered(args_from_ui))

    # replace with a list of the attribute names in order and a list
    # of query results.
    return from_join #([], [])


def filtered(diction):
    "filters args_from_ui into dictionaries with keys being the input's respective table"
    
    fields = {'courses': ['dept', 'course_num','title'], 
              'meeting_patterns': ['day', 'time_start', 'time_end'], 
              'sections': ['section_num', 'enroll_lower', 'enroll_upper'], 
              'gps': ['building', 'walking_time'], 
              'catalog_index':['terms']} 
    
    current_fields = {}
    for k in fields.keys():
        current_fields[k] = []
        for i in fields[k]:
            if diction.get(i) != None:
                current_fields[k].append(i)

    
    return current_fields

def from_function(current_fields):
    'Creates the From and Join Command'

    frm_fct = 'FROM courses'
    for i in current_fields.keys():
        if current_fields[i] and i not in frm_fct:
            frm_fct += str(' JOIN' + ' {}'.format(i))

    return frm_fct

def where_function(args_from_ui):
    for i in args_from_ui.keys():

    return 1



########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


########### some sample inputs #################

EXAMPLE_0 = {"time_start": 930,
             "time_end": 1500,
             "day": ["MWF"]}

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}
