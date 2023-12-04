from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTItem, LTTextLineHorizontal

from typing import Iterator, Optional
from operator import attrgetter
import re

from .config import SearchParams as Params
from .exceptions import MissingElementError, ParseVerificationError
from .structs import EvaluationMetadata, EvaluationItem, EvaluationOverall, EvaluationHours, Evaluation, \
    Bounds, Items


def process_pdf(file_loc: str):
    # Extract PDF
    pages = list(extract_pages(file_loc))

    # Get all the text elements of Page 1 in list form
    page1_text_elems = [elem for elem in pages[0] if isinstance(elem, LTTextBoxHorizontal)]

    # Get all the text elements of Page 2 in list form
    page2_text_elems = [elem for elem in pages[1] if isinstance(elem, LTTextBoxHorizontal)]

    # Extract the Metadata from Page 1
    eval_metadata = extract_metadata(page1_text_elems)

    # Extract the Overall Indicator from Page 1
    eval_overall = extract_overall_item(page1_text_elems)
    # eval_overall = EvaluationOverall(average=-1.0, stddev=-1.0)  # Temporary Values

    # Extract the Feedback Items
    eval_items = extract_items(page1_text_elems, page2_text_elems)

    # Extract the Work Hours
    eval_hours = extract_hours(page2_text_elems)

    # Create an Evaluation object for the PDF
    evaluation = Evaluation(metadata=eval_metadata, overall=eval_overall, items=eval_items, hours=eval_hours)

    # print(evaluation)
    return evaluation


def extract_metadata(page_text_elems: list[LTTextBoxHorizontal]) -> EvaluationMetadata:
    header_iter: Optional[Iterator[LTTextBoxHorizontal]] = None

    # Loop through the elements and find the header element
    for elem in page_text_elems:
        if check_bounds(elem, Params.header_search_bounds) and len(elem.get_text()) > Params.minimum_header_len:
            # print(list(elem))
            header_iter = iter(elem)
            break

    # Ensure that the header element is found, if not, raise exception
    if header_iter is None:
        raise MissingElementError("Unable to find the header for the input PDF")

    # Iterate through the header to find each of the desired elements
    try:
        # Instructor Name
        while True:
            instructor_name = next(header_iter).get_text().strip()
            if len(instructor_name.split(" ")) == 2:
                break

        # Course Summary
        while True:
            course_summary = next(header_iter).get_text().strip()
            if re.match(r"^.+\(\w{4}\d{1,4}\w{0,2}-\d{5}\)$", course_summary):
                course_desc, course_info = course_summary.split("(", 2)
                course_name, section_code = course_info.removesuffix(")").split("-", 2)
                break

        # Course Term
        while True:
            course_term = next(header_iter).get_text().strip().split(" - ")
            if len(course_term) == 2 and course_term[0].rstrip() in ["Fall", "Winter", "Spring", "Summer"]:
                course_quarter, course_year = course_term
                break

        # Number of Enrolled Students
        while True:
            enrolled_num_str = next(header_iter).get_text().strip()
            if enrolled_num_str.startswith("No. of students enrolled = "):
                enrolled_num = int(enrolled_num_str.removeprefix("No. of students enrolled = "))
                break

        # Number of Responses
        while True:
            response_num_str = next(header_iter).get_text().strip()
            if response_num_str.startswith("No. of responses = "):
                response_num = int(response_num_str.removeprefix("No. of responses = "))
                break

        # Response Rate
        while True:
            response_rate_str = next(header_iter).get_text().strip()
            if response_rate_str.startswith("Response Rate = "):
                response_rate = float(response_rate_str.removeprefix("Response Rate = ").removesuffix(" %"))
                break
    except StopIteration:
        raise MissingElementError("Unable to find at least one of the expected elements in the header")

    # print(repr(instructor_name), repr(course_name), repr(course_desc), repr(section_code), repr(course_quarter),
    #       repr(course_year), repr(enrolled_num), repr(response_num), repr(response_rate))

    # Generate and Return an EvaluationMetadata class to store all the data
    return EvaluationMetadata(instructor=instructor_name,
                              course_name=course_name,
                              course_desc=course_desc,
                              section_code=section_code,
                              section_quarter=course_quarter,
                              section_year=course_year,
                              section_enrollment=enrolled_num,
                              evaluation_responses=response_num,
                              response_rate=response_rate)


def extract_overall_item(page_text_elems: list[LTTextBoxHorizontal]) -> EvaluationOverall:
    # Create bounds for the overall item
    overall_bounds = Bounds(Params.item_summary_bounds.x0, 605, Params.item_summary_bounds.x1, 635)
    overall_raw: Optional[LTTextBoxHorizontal] = None
    overall_list: list[LTTextLineHorizontal]

    # Find the matching element which corresponds to the data for "overall indicators"
    for elem in page_text_elems:
        if check_bounds(elem, overall_bounds):
            overall_raw = elem
            break

    # Ensure that we found a matching element
    if overall_raw is None:
        raise MissingElementError("Unable to find element for 'Overall Indicators' item")

    # Ensure that there is the correct number of data points (ave and dev)
    overall_list = list(overall_raw)
    if not len(overall_list) == 2:
        raise ParseVerificationError("Invalid number of elements for the 'Overall Indicators' item")

    # Verify and process the data we have extracted
    raw_ave = overall_list[0].get_text()
    raw_dev = overall_list[1].get_text()

    if raw_ave.startswith("av.=") and raw_dev.startswith("dev.="):
        try:
            ave = float(raw_ave.rstrip().removeprefix("av.="))
            dev = float(raw_dev.rstrip().removeprefix("dev.="))
        except TypeError:
            raise ParseVerificationError("Unable to parse elements in the 'Overall Indicators' item as floats")
    else:
        raise ParseVerificationError("Invalid prefix for elements in the 'Overall Indicators' item")

    # Generate the expected return format and return
    return EvaluationOverall(ave, dev)


def extract_items(page1_text_elems: list[LTTextBoxHorizontal],
                  page2_text_elems: list[LTTextBoxHorizontal]) -> dict[Items, EvaluationItem]:
    # Instantiate a dict to store the final EvaluationItem results before returning
    evaluation_items: dict[Items, EvaluationItem] = {i: [] for i in Items}

    # Instantiate a dict to store the elements within an item's boundaries
    item_elems: dict[Items, list[LTTextBoxHorizontal]] = {i: [] for i in Items}

    # Loop through the elements in the first page and separate them out by the provided y-bounds of each item
    item: Items
    for elem in page1_text_elems:
        for item in Items.page_items(1):
            if elem.y0 > item.bounds.y0 and elem.y1 < item.bounds.y1:
                item_elems[item].append(elem)
                break

    # Loop through the elements in the second page and separate them out by the provided y-bounds of each item
    for elem in page2_text_elems:
        for item in Items.page_items(2):
            if elem.y0 > item.bounds.y0 and elem.y1 < item.bounds.y1:
                item_elems[item].append(elem)
                break

    # Loop through all the items to separate and process its elements into EvaluationItem classes
    for item, elems in item_elems.items():
        # Instantiate temporary variables to store data before creating an Evaluation Item class
        item_percent_data: list[float] = []
        item_summary_data: list[LTTextBoxHorizontal] = []

        # Flags to indicate if the ID and description has been checked (if it is, skip checks)
        id_verified = False
        desc_verified = False

        # Loop through each element in the list and process them according to their x-bounds
        for elem in elems:
            # Verify the question ID (if not yet previously done)
            if (not id_verified) and elem.x0 > Params.item_id_bounds.x0 and elem.x1 < Params.item_id_bounds.x1:
                if not (elem.get_text().rstrip() == f"1.{item})" or elem.get_text().rstrip() == f"2.2)"):
                    raise ParseVerificationError(f"Question ID Verification failed for {repr(item)} "
                                                 f"with element {elem}.")
                id_verified = True
                continue

            # Verify the question description (if not yet previously done)
            if (not desc_verified) and elem.x0 > Params.item_description_bounds.x0 and \
                    elem.x1 < Params.item_description_bounds.x1:
                if not (elem.get_text().rstrip().replace("\n", " ") == item.description):
                    raise ParseVerificationError(f"Question Description Verification failed for {repr(item)} "
                                                 f"with element {elem}.")
                desc_verified = True
                continue

            # Extract the item's raw percentage data
            if elem.x0 > Params.item_data_bounds.x0 and elem.x1 < Params.item_data_bounds.x1:
                if (elem_strip := elem.get_text().rstrip()).endswith("%"):
                    item_percent_data.append(float(elem_strip.removesuffix("%")))
                continue

            # Extract the item's summary data
            if elem.x0 > Params.item_summary_bounds.x0 and elem.x1 < Params.item_summary_bounds.x1:
                item_summary_data.append(elem)

        # Ensure that the id and description attributes have been verified
        if not id_verified:
            raise ParseVerificationError(f"Did not find element to verify Question ID for {repr(item)} ")

        if not desc_verified:
            raise ParseVerificationError(f"Did not find element to verify Question Description for {repr(item)} ")

        # Ensure that there is the expected number of elements in the two lists
        if not len(item_percent_data) == 5:
            raise ParseVerificationError(f"Expected 5 percentage values, but parsed {len(item_percent_data)} for "
                                         f"{repr(item)}")

        if not len(item_summary_data) == 1:
            raise ParseVerificationError(f"Expected 1 summary string, but parsed {len(item_summary_data)} for "
                                         f"{repr(item)}")

        # Parse and verify the summary data
        item_summary: list[LTTextBoxHorizontal] = list(item_summary_data[0])
        prefix_list: list[str] = ["n=", "av.=", "md=", "dev.="]

        i: LTTextBoxHorizontal
        if all([i.get_text().startswith(prefix) for i, prefix in zip(item_summary, prefix_list)]):
            item_n, item_av, item_md, item_dev = \
                [i.get_text().rstrip().removeprefix(prefix) for i, prefix in zip(item_summary, prefix_list)]
        else:
            raise ParseVerificationError(f"Summary Data Structure Invalid for {repr(item)}")

        # Create an EvaluationItem object
        ipd = item_percent_data
        e = EvaluationItem(item_id=item, freq=(ipd[0], ipd[1], ipd[2], ipd[3], ipd[4]),
                           responses=item_n, average=item_av, median=item_md, stddev=item_dev)

        # Add the EvaluationItem object to the list
        evaluation_items[item] = e

    return evaluation_items


def extract_hours(page2_text_elems: list[LTTextBoxHorizontal]):
    # Create bounds for the overall item
    hours_bounds = Bounds(460, 415, 500, 535)

    # Find all matching elements
    hours_raw: list[LTTextBoxHorizontal] = [elem for elem in page2_text_elems if check_bounds(elem, hours_bounds)]

    # Explicitly sort the data by its y-coordinates
    hours_raw.sort(key=attrgetter("y0"), reverse=True)

    # Ensure that there is the correct number of data
    if not len(hours_raw) == 7:
        raise ParseVerificationError(f"Expected 7 work hour elements, but got {len(hours_raw)} elements.")

    # Clean up the data
    hours_data: list[float] = [float(elem.get_text().rstrip().removesuffix("%")) for elem in hours_raw]

    return EvaluationHours(*hours_data)


def check_bounds(elem: LTItem, bounds: Bounds):
    def lt(x, y): return True if y is None else x < y

    def gt(x, y): return True if y is None else x > y

    return gt(elem.x0, bounds.x0) and gt(elem.y0, bounds.y0) and lt(elem.x1, bounds.x1) and lt(elem.y1, bounds.y1)
