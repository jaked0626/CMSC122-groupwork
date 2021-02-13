
from math import radians, cos, sin, asin, sqrt
import sqlite3
import os

input_options = {"dept": {"SELECT": set(["dept", "course_num", "title"]),
                          "FROM JOIN": set(["courses"]), 
                          "ON": set([]),
                          "WHERE": "courses.dept = ?"},
                 "terms": {"SELECT": set(["dept", "course_num", "title"]),
                          "FROM JOIN": set(["courses"]), 
                          "ON": set(["courses.course_id = catalog_index.course_id"]),
                          "WHERE": "catalog_index.word = ?",
                          "GROUP_BY": "courses.course_id",
                          "HAVING": "COUNT(*) >= ?"},
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
                 "walking_time":  {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "building_code as building", "walking_time"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns", "gps"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id", "sections.building_code = gps.building_code"]),
                         "WHERE": "walking_time = ?"},
                 "building": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "building_code as building", "walking_time"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns", "gps"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id", "sections.building_code = gps.building_code"]),
                         "WHERE": "gps.building_code = ?"},
                 "enroll_lower": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "enrollment"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "sections.enrollment >= ?"},
                 "enroll_upper": {"SELECT": set(["dept", "course_num", "section_num", "day", "time_start", "time_end", "enrollment"]),
                         "FROM JOIN": set(["courses", "sections", "meeting_patterns"]), 
                         "ON": set(["courses.course_id = sections.course_id", "sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id"]),
                         "WHERE": "sections.enrollment <= ?"}}

outputs_to_fields = {"dept": "courses", "course_num": "courses", "title": "courses", "section_num": "sections", "day": "meeting_patterns", "time_start": "meeting_patterns", "time_end": "meeting_patterns", "building_code as building": "gps", "walking_time": "gps", "enrollment": "sections"}

ordered_outputs = ["dept", "course_num", "section_num", "day", "time_start", "time_end", "building", "walking_time", "enrollment", "title"]

def select_func(args_from_ui):
    query = set()
    query_str = []
    for input_, dic in input_options.items():
        if input_ in args_from_ui.keys():
            query.update(dic["SELECT"])
    
    if query:
        for select_category in ordered_outputs:
            if select_category in query:
                query_str.append(select_category)
        query_str = list(map(lambda x: "{}.{}".format(outputs_to_fields[x], x), query_str))
        query_str = "SELECT " + ", ".join(query_str)
        
    return query_str

def from_func(args_from_ui):
    'Creates the From and Join Command'
    query = set()

    for input_ in args_from_ui.keys():
        query.update(input_options[input_]["FROM JOIN"])
    if query:
        query = "FROM " + " JOIN ".join(query)
    else:
        query = []

    return query

def on_func(args_from_ui):
    'Creates the ON Command'
    query = set()

    for input_ in args_from_ui.keys():
        query.update(input_options[input_]["ON"])
    if query:
        query = "ON " + " AND ".join(query)
    else:
        query = []

    return query

def where_func(args_from_ui):

    if args_from_ui.get("terms"):
        args_from_ui["terms"] = args_from_ui["terms"].split() 

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

    query = "WHERE " +  " AND ".join(query)

    return query, tupleq
