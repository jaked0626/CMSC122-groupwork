
from math import radians, cos, sin, asin, sqrt
import sqlite3
import os

input_options = {"dept": {"SELECT": set(["dept", "course_num", "title"]),
                          "FROM JOIN": set(["courses"]), 
                          "ON": set([]),
                          "WHERE": "courses.dept = ?"},
                 "terms": {"SELECT": set(["dept", "course_num", "title"]),
                          "FROM JOIN": set(["courses", "catalog_index"]), 
                          "ON": set(["courses.course_id = catalog_index.course_id"]),
                          "WHERE": "catalog_index.word = ?"},
                 "day": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "meeting_patterns.day = ?"},
                 "time_start": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "meeting_patterns.time_start >= ?"},
                 "time_end": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "meeting_patterns.time_end <= ?"},
                 "walking_time":  {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "building", "walking_time"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns", "gps AS a"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id", "sections.building_code = a.building_code"]),
                         "WHERE": "walking_time <= ?"},
                 "building": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "building", "walking_time"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns", "gps AS b"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id", "sections.building_code = b.building_code"]),
                         "WHERE": "a.building_code = ?"},
                 "enroll_lower": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "enrollment"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "sections.enrollment >= ?"},
                 "enroll_upper": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "enrollment"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "sections.enrollment <= ?"}}


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

    args_copy = dict(args_from_ui)
    if args_copy.get("terms"):
        args_copy["terms"] = args_copy["terms"].split()
    
    query1 = select_func(args_copy)
    print(1, query1)
    query2 = from_func(args_copy)
    print(2, query2)
    query3 = on_func(args_copy)
    print(3, query3)
    query4, variables1 = where_func(args_copy)
    print(4, query4)
    query5, variables2 = groupby_func(args_copy)
    print(5, query5)

    return ( " ".join(query1 + query2 + query3 + query4 + query5), variables1 + variables2)


def select_func(args_from_ui):
    outputs_to_fields = {"dept": "courses.", "course_num": "courses.", "title": "courses.", "section_num": "sections.", "day": "meeting_patterns.", "time_start": "meeting_patterns.", "time_end": "meeting_patterns.", "building": "b.building_code AS ", "walking_time": "time_between(a.lon, a.lat, b.lon, b.lat) AS ", "enrollment": "sections."}
    ordered_outputs = ["dept", "course_num", "section_num", "day", "time_start", "time_end", "building", "walking_time", "enrollment", "title"]
    query = set()
    query_str = []
    for input_, dic in input_options.items():
        if input_ in args_from_ui.keys():
            query.update(dic["SELECT"])
    
    if query:
        for select_category in ordered_outputs:
            if select_category in query:
                query_str.append(select_category)
        query_str = list(map(lambda x: "{}{}".format(outputs_to_fields[x], x), query_str))
        query_str = ["SELECT " + ", ".join(query_str)]
        
    return query_str


def from_func(args_from_ui):
    'Creates the From and Join Command'
    query = set()

    for input_ in args_from_ui.keys():
        query.update(input_options[input_]["FROM JOIN"])
    if query:
        query = ["FROM " + " JOIN ".join(query)]
    else:
        query = []

    return query

def on_func(args_from_ui):
    'Creates the ON Command'
    query = set()

    for input_ in args_from_ui.keys():
        query.update(input_options[input_]["ON"])
    if query:
        query = ["ON " + " AND ".join(query)]
    else:
        query = []

    return query

def where_func(args_from_ui): 

    query = []
    tupleq = tuple()
    for input_, value in args_from_ui.items():
        if isinstance(value, list):
            subquery = []
            for instance in value:
                subquery.append(input_options[input_]["WHERE"])
                tupleq += (instance,)
            query += ["(" + " OR ".join(subquery) + ")"]
        else: 
            query.append(input_options[input_]["WHERE"])
            tupleq += (value, )
    if query:
        query = ["WHERE " +  " AND ".join(query)]

    return query, tupleq

def groupby_func(args_copy):
    query = []
    tupleq = tuple()
    if args_copy.get("terms"):
        num_terms = len(args_copy["terms"])
        if num_terms > 1:
            query = ["GROUP BY courses.course_id HAVING COUNT(*) >= ?"]
            tupleq = (num_terms,)
    
    return query, tupleq



