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
    fields = {'courses': {'Inputs': ['dept'], 'Outputs': ['dept', 'course_num','title']}, 
              'meeting_patterns': {'Inputs': ['day', 'time_start', 'time_end'], 'Outputs': ['day', 'time_start', 'time_end', 'section_num', 'course_num', 'dept']}, 
              'sections': {'Inputs': ['enroll_lower', 'enroll_upper'], 'Outputs': ['day', 'time_start', 'time_end', 'section_num', 'course_num', 'dept', 'enrollment']}, 
              'gps': {'Inputs': ['building', 'walking_time'], 'Outputs': ['day', 'time_start', 'time_end', 'section_num', 'course_num', 'dept', 'enrollment', 'building', 'walking_time']}, 
              'catalog_index': {'Inputs': ['word'], 'Outputs': ['dept', 'course_num','title']}} 

    if 'terms' in args_from_ui:
        args_from_ui['word'] = [args_from_ui['terms']][0].split()
        del args_from_ui['terms']

    frm = from_function(filtered(args_from_ui, fields))
    whr = where_function(args_from_ui, filtered(args_from_ui, fields))
    slct = select_function(filtered(args_from_ui, fields), fields)
    # replace with a list of the attribute names in order and a list
    # of query results.
    #([], [])
    return slct, frm, whr


def filtered(diction, fields):
    "filters args_from_ui into dictionaries with keys being the input's respective table"
    
    current_fields = {}
    for k in fields.keys():
        current_fields[k] = []
        for i in fields[k]['Inputs']:
            if diction.get(i) != None:
                current_fields[k].append(i)
    
    return current_fields

def select_function(current_fields, fields):
    slct_order = ['dept', 'course_num', 'section_num', 'day', 'time_start', 'time_end', 'building', 'enrollment', 'title'] #my attempt at telling python how to order it
    slct_fct = 'SELECT courses.dept, courses.course_num'
    for k in current_fields.keys():
        if current_fields[k]:
            for i in slct_order:
                if i in fields[k]['Outputs'] and '.{}'.format(i) not in slct_fct:
                    print(i)
                    slct_fct += ', {}.{}'.format(k, i)
    
    return slct_fct

def from_function(current_fields):
    'Creates the From and Join Command'

    frm_fct = 'FROM courses'
    for i in current_fields.keys():
        if current_fields[i] and i not in frm_fct:
            frm_fct += str(' JOIN' + ' {}'.format(i))

    return frm_fct

def where_function(args_from_ui, filtered):
    'creates the WHERE statement'
    whr_fct = 'WHERE'
    tester = ""
    for i in filtered.keys():
        if filtered[i]:
            for j in filtered[i]:
                if type(args_from_ui[j]) == list:
                    for value in args_from_ui[j]: #The following 3 if statements are there to put the necessary paranthesis around OR statements in the case of items with multiple entries 
                        if args_from_ui[j][-1] == value:
                            x = (str(' {}.{}'.format(i, j) + ' = ?' + ')' + ' AND'))
                        if args_from_ui[j][0] == value:
                            x = (str(' ({}.{}'.format(i, j) + ' = ?' + ' OR'))                 
                        if value != args_from_ui[j][-1] and value != args_from_ui[j][0]:
                            x = (str(' {}.{}'.format(i, j) + ' = ?' + ' OR'))
                        whr_fct += x
                if type(args_from_ui[j]) == int:
                    if 'lower' in j or 'start' in j:
                        whr_fct += str(' {}.{}'.format(i, j) + ' >= ?' + ' AND')
                    if 'upper' in j or 'end' in j:
                        whr_fct += str(' {}.{}'.format(i, j) + ' <= ?' + ' AND')
                elif ' {}.{}'.format(i, j) not in whr_fct:
                    whr_fct += str(' {}.{}'.format(i, j) + ' = ?' + ' AND')
    whr_fct = whr_fct.rsplit(' ', 1)[0]
    return whr_fct



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
