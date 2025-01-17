"""
ratemyprofessor

RateMyProfessor API
An extremely basic web scraper for the RateMyProfessor website.

:copyright: (c) 2021 Nobelz
:license: Apache 2.0, see LICENSE for more details.
"""
import requests
import re
import json
import base64
import os

from .professor import Professor, PartialProfessor
from .school import School, PartialSchool


with open(os.path.join(os.path.dirname(__file__), "json/header.json"), 'r') as f:
    headers = json.load(f)


def get_school_by_name(school_name: str):
    """
    Gets a School with the specified name.

    This only returns 1 school name, so make sure that the name is specific.
    For instance, searching "Ohio State" will return 6 schools,
    but only the first one will return by calling this method.

    :param school_name: The school's name.
    :return: The school that match the school name. If no schools are found, this will return None.
    """
    schools = get_schools_by_name(school_name)
    if schools:
        return schools[0]
    else:
        return None


def get_schools_by_name(school_name: str):
    """
    Gets a list of Schools with the specified name.

    This only returns up to 20 schools, so make sure that the name is specific.
    For instance, searching "University" will return more than 20 schools, but only the first 20 will be returned.

    :param school_name: The school's name.
    :return: List of schools that match the school name. If no schools are found, this will return an empty list.
    """
    school_name.replace(' ', '+')
    url = "https://www.ratemyprofessors.com/search/schools?q=%s" % school_name
    page = requests.get(url)
    data = re.findall(r'"legacyId":(\d+)', page.text)
    school_list = []

    for school_data in data:
        try:
            school_list.append(School(int(school_data)))
        except ValueError:
            pass
    
    return school_list


def get_professor_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Gets a Professor with the specified School and professor name.

    This only returns 1 professor, so make sure that the name is specific.
    This returns the professor with the most ratings.
    For instance, searching "Smith" using the School of Case Western Reserve University will return 5 results,
    but only one result will be returned.

    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: The professor that matches the school and name. If no professors are found, this will return None.
    """
    professors = get_professors_by_school_and_name(college, professor_name)
    max_professor = None

    for prof in professors:
        if max_professor is None or max_professor.num_ratings < prof.num_ratings:
            max_professor = prof

    return max_professor

def get_first_professor_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Gets a Professor with the specified School and professor name.
		
    This only returns 1 professor, so make sure that the name is specific.
    This returns the first professor listed on Rate My Professor, regardless of rating.
    For instance, searching "Smith" using the School of Case Western Reserve University will return 5 results,
    but only the top result will be returned.
    This method is faster than `get_professor_by_school_and_name`, but may provide worse/better results depending on your usecase.
		
    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: The professor that matches the school and name. If no professors are found, this will return None.
    """
		
    url = 'https://www.ratemyprofessors.com/search/professors/%s?q=%s' % (college.id, professor_name)
    page = requests.get(url)
    data = re.findall(r'"legacyId":(\d+)', page.text)
		
    for professor_data in data:
        try:
            return Professor(int(professor_data))
        except ValueError:
            pass
		
    return None



def get_professors_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Gets a list of professors with the specified School and professor name.

    This only returns up to 20 professors, so make sure that the name is specific.
    For instance, searching "Smith" with a school might return more than 20 professors,
    but only the first 20 will be returned.

    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: List of professors that match the school and name. If no professors are found,
             this will return an empty list.
    """
    # professor_name.replace(' ', '+')
    url = 'https://www.ratemyprofessors.com/search/professors/%s?q=%s' % (college.id, professor_name)
    page = requests.get(url)
    data = re.findall(r'"legacyId":(\d+)', page.text)
    professor_list = []

    for professor_data in data:
        try:
            professor_list.append(Professor(int(professor_data)))
        except ValueError:
            pass

    return professor_list



def fast_get_professor_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Quickly gets a `PartialProfessor` with the specified School and professor name.

    `PartialProfessor`s can be converted into `Professor` objects with `to_professor()`.

    This only returns 1 professor, so make sure that the name is specific.
    This returns the professor with the most ratings.
    For instance, searching "Smith" using the School of Case Western Reserve University will return 5 results,
    but only one result will be returned.

    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: The `PartialProfessor` that matches the school and name. If no professors are found, this will return None.
    """
    professors = fast_get_professors_by_school_and_name(college, professor_name)
    max_professor = None

    for prof in professors:
        if max_professor is None or max_professor.num_ratings < prof.num_ratings:
            max_professor = prof

    return max_professor

def fast_get_first_professor_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Quickly gets a `PartialProfessor` with the specified School and professor name.

    This function just calls `fast_get_professors_by_school_and_name` and returns the first result.
		
    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: The professor that matches the school and name. If no professors are found, this will return None.
    """
		
    professors = fast_get_professors_by_school_and_name(college, professor_name)

    if len(professors) > 0:
        return professors[0]
    else:
        return None


def fast_get_professors_by_school_and_name(college: School | PartialSchool, professor_name: str):
    """
    Quickly gets a list of `PartialProfessor`s with the specified School and professor name.

    `PartialProfessor`s can be converted into `Professor` objects with `to_professor()`.

    This only returns up to 20 professors, so make sure that the name is specific.
    For instance, searching "Smith" with a school might return more than 20 professors,
    but only the first 20 will be returned.

    :param college: The professor's school.
    :param professor_name: The professor's name.
    :return: List of `PartialProfessor`s that match the school and name. If no professors are found,
             this will return an empty list.
    """
    # professor_name.replace(' ', '+')
    url = 'https://www.ratemyprofessors.com/search/professors/%s?q=%s' % (college.id, professor_name)
    page = requests.get(url)
    data = re.findall(r'"__typename":"TeacherSearchConnectionEdge.+?(?=,"client:root:newSearch:teachers)', page.text)
    
    professor_dict_list = [json.loads('{"null": {' + x + '}') for x in data]
    professor_list = []

    for professor_data in professor_dict_list:
        professor_list.append(PartialProfessor([x for x in professor_data.values() if "legacyId" in x][0]))

    return professor_list
