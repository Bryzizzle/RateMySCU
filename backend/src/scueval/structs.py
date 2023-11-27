from dataclasses import dataclass
from enum import IntEnum, unique
from typing import NamedTuple, Optional, TypedDict, Union


class Bounds(NamedTuple):
    x0: Optional[float] = None
    y0: Optional[float] = None
    x1: Optional[float] = None
    y1: Optional[float] = None


@unique
class Items(IntEnum):
    """ An enumeration of all the given evaluation questions/items

    The enumeration is written in a 4-tuple (id, page, bounds, description)
    id being the "main" value integer used by each enum (this will allow for indexing using an int, not only the enum)
    """
    Q1 = 1, 1, Bounds(y0=380, y1=435), "The instructor communicated clearly the expectations for the course."
    Q2 = 2, 1, Bounds(y0=325, y1=380), "The instructor organized the course effectively."
    Q3 = 3, 1, Bounds(y0=270, y1=325), "The instructor designed a course that challenged me to think rigorously " \
                                       "about the material."
    Q4 = 4, 1, Bounds(y0=215, y1=270), "The instructor helped students to reach a clear understanding of key concepts."
    Q5 = 5, 1, Bounds(y0=160, y1=215), "The instructor managed class time in a manner that advanced my learning."
    Q6 = 6, 1, Bounds(y0=105, y1=160), "The instructor fostered a mutually respectful learning environment."
    Q7 = 7, 2, Bounds(y0=705, y1=760), "The instructor provided useful oral or written feedback."
    Q8 = 8, 2, Bounds(y0=650, y1=705), "The instructor was available and willing to help students outside class."
    Q9 = 9, 2, Bounds(y0=595, y1=650), "Overall, the instructor is an excellent teacher."
    Q10 = 10, 2, Bounds(y0=350, y1=410), "This course was conceptually challenging compared to most courses I have " \
                                         "taken at SCU:"

    @classmethod
    def page_items(cls, page: int) -> list["Items"]:
        return [item for item in cls if item.page == page]

    def __new__(cls, item_id: int, *args):
        member = int.__new__(cls, item_id)
        member._value_ = item_id

        return member

    def __init__(self, _, page: int, search_bounds: Bounds, description: str, *args):
        self._page = page
        self._bounds = search_bounds
        self._description = description

    @property
    def page(self):
        return self._page

    @property
    def bounds(self):
        return self._bounds

    @property
    def description(self):
        return self._description


@dataclass
class EvaluationMetadata:
    """ Stores information about an evaluation """
    instructor: str

    course_name: str
    course_desc: str

    section_code: str
    section_quarter: str
    section_year: str

    section_enrollment: int
    evaluation_responses: int
    response_rate: float


@dataclass
class EvaluationOverall:
    """ Stores information about the overall indicator of an evaluation"""
    average: float
    stddev: float


@dataclass
class EvaluationItem:
    """ Stores information about an feedback item in an evaluation """
    # The current item's identifier (in an Items enum)
    item_id: Items

    # Raw Percentage Values
    freq: tuple[float, float, float, float, float]

    # Summary Values
    responses: int
    average: float
    median: int
    stddev: float


@dataclass
class EvaluationHours:
    """ Stores information about the number of hours on work for this course in an evaluation """
    _hours: list[float]

    def __init__(self, h0_1: float, h2_3: float, h4_5: float, h6_7: float, h8_10: float, h11_14: float, h15: float):
        self._hours = [h0_1, h2_3, h4_5, h6_7, h8_10, h11_14, h15]

    @property
    def h0_1(self):
        return self.hours[0]

    @property
    def h2_3(self):
        return self.hours[1]

    @property
    def h4_5(self):
        return self.hours[2]

    @property
    def h6_7(self):
        return self.hours[3]

    @property
    def h8_10(self):
        return self.hours[4]

    @property
    def h11_14(self):
        return self.hours[5]

    @property
    def h15(self):
        return self.hours[6]

    @property
    def hours(self):
        return self._hours

@dataclass
class Evaluation:
    """ Stores data about a specific CourseEval Document """
    metadata: EvaluationMetadata
    overall: EvaluationOverall
    items: dict[Items, EvaluationItem]
    hours: EvaluationHours

    def __str__(self):
        md = self.metadata

        return f"{md.course_desc}({md.course_name}-{md.section_code}) {md.section_quarter} {md.section_year}"




