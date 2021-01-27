# CS122: Course Search Engine Part 1
#
# Your name(s)
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])


def make_soup(url):
    '''
    Given a url, return the soup object of this url

    Input: url (a string)
    Output: the soup object
    '''
    request = util.get_request(url)
    if request:
        text = util.read_request(request)
        soup = bs4.BeautifulSoup(text, 'html5lib')
    return soup #, request


def linked_urls(starting_url, queue=queue.Queue()):
    links = queue
    soup = make_soup(starting_url)
    for link in soup.find_all('a'):
        relative_url = link['href']
        linked_url = util.convert_if_relative_url(starting_url, relative_url)
        filtered_link = util.remove_fragment(linked_url)
        links.put(filtered_link)

    return links

# when calling linked_urls in a webpage, remember to use get_request_URL(request object 
# for said webpage) as satrting_url. 

def code_to_identifier(code, course_map_filename="course_map.json"):
    '''
    Takes course name (stringt) and converts it to the identifier according to 
    the map
    '''
    dic_codes = json.load(open(course_map_filename))
    return dic_codes.get(code.replace("\xa0", " "))
    #return dic_codes.get(code.replace("&#160;", " "))

# dict(map(lambda x: (x[0], list(map(code_to_identifier, x[1]))), dic.items()))


def register_words(dic, text, coursetitles): #maybe add dic parameter and coursetitle parameter(list) and integrate indexing operation
    '''
    Given a body of text, returns a list of valid words in text.
    Thinking of adding a dictionary parameter and coursetitle parameter 
    so that this function adds new words as keys to the dictionary and 
    the corresponding coursetitle as values. Coursetitles would be a list, 
    so we can factor out a bulk of the coding necessary to differentiate sequences
    and individual courses. 
    '''
    matches = re.findall("[a-zA-Z0-9]+", text)
    for word in matches:
        if word.lower() not in INDEX_IGNORE:
            if dic.get(word.lower()):
                for course in coursetitles:
                    if course not in dic[word.lower()]:
                        dic[word.lower()].append(course)
            else:
                dic[word.lower()] = coursetitles

    return dic



def crawl_soup(soup, index={}):
    """
    Goes through soup object (one internet page) and indexes words found
    in that object. 
    Returns dictionary
    """
    main_tags = soup.find_all("div", class_="courseblock main")
    for tag in main_tags:
        sequences = util.find_sequence(tag)
        if sequences:  # if courseblock main is a sequence
            course_code = [find_course_names(subseq) for subseq in sequences]
            for ptag in tag.find_all("p", class_=["courseblocktitle", "courseblockdesc"]):
                index = register_words(index, ptag.text, [course_code])
            for subseq in sequences:
                index = crawl_soup(subseq, index)
            
        else:  # if it is not a sequence
            course_code = find_course_names(tag)
            for ptag in tag.find_all("p", class_=["courseblocktitle", "courseblockdesc"]):
                index = register_words(index, ptag.text, [course_code])
                    
    return index

def find_course_names(courseblockmaintag):
    title_tag = courseblockmaintag.find_all("p", class_="courseblocktitle")[0]
    course_code = re.search("[A-Z]{4}\xa0[0-9]{5}", title_tag.text).group()
    return course_code



def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generate a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping of
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index
    '''

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # YOUR CODE HERE


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
