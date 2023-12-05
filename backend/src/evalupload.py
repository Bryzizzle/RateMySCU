import json
from io import BytesIO

from fastapi import UploadFile

from .scueval.structs import *
from .database import *
from .scueval.analyze import process_pdf


# CODE FOR UPLOADING EVALUATIONS FROM PDF TO DATABASE

# uplaod_system: temporary code for uploading placeholder evaluation to database
def upload_system(connection, pdf_file: UploadFile):
    try:
        print("activate upload")
        evaluation = process_pdf(BytesIO(pdf_file.file.read()))
        print("created evaluation")
        # evaluation = create_evaluation()
        upload_evaluation(evaluation, connection)
    except Exception as e:
        print(e)


# create_evaluation: temporary code for creating an evaluation to upload
def create_evaluation():
    try:
        print("Creating evaluation")
        metadata = EvaluationMetadata(instructor="instructor_name",
                                      course_name="course_name",
                                      course_desc="course_desc",
                                      section_code="section_code",
                                      section_quarter="course_quarter",
                                      section_year="2023",
                                      section_enrollment=2,
                                      evaluation_responses=1,
                                      response_rate=0.5)
        overall = EvaluationOverall(3.5, 0.4)
        hours = EvaluationHours(0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
        items: dict[Items, EvaluationItem] = {i: [] for i in Items}
        for item in Items:
            e = EvaluationItem(item_id=item, freq=(0.1, 0.2, 0.3, 0.4, 0.5),
                               responses=5, average=3.3, median=3.6, stddev=0.2)
            items[item] = e

        return Evaluation(metadata=metadata,
                          overall=overall,
                          items=items,
                          hours=hours)
    except Exception as e:
        print(e)


# upload_evaluation: creates SQL query to upload evaluation to postgres database
def upload_evaluation(eval: Evaluation, connection):
    try:
        print("Uploading evaluation")
        query = """INSERT INTO evals (classcode, classname, quarter, year, professor, 
            numstudents, numresponses, overall, hours, stats) VALUES ("""
        query_builder = []
        query_builder.append("'" + eval.metadata.section_code + "'")
        query_builder.append("'" + eval.metadata.course_name + "'")
        query_builder.append("'" + eval.metadata.section_quarter + "'")
        query_builder.append(eval.metadata.section_year)
        query_builder.append("'" + eval.metadata.instructor + "'")
        query_builder.append(str(eval.metadata.section_enrollment))
        query_builder.append(str(eval.metadata.evaluation_responses))
        query_builder.append(str(eval.overall.average))
        eval_hours = str(eval.hours.hours).replace("[", "").replace("]", "")
        query_builder.append("'{" + eval_hours + "}'")
        query_builder.append("'" + str(extract_stats_json(eval.items)) + "'")
        query += ", ".join(query_builder) + ");"
        print(query)
        no_response_query(connection, query)
    except Exception as e:
        print(e)


# extract_stats_json: extracts the evaluation items from the evaluation as JSON
def extract_stats_json(items: dict[Items, EvaluationItem]):
    try:
        stats = {}
        statsList = []
        for item in Items:
            elements = {}
            elements["desc"] = item.description
            elements["n"] = items[item].responses
            elements["avg"] = items[item].average
            elements["med"] = items[item].median
            elements["dev"] = items[item].stddev
            statsList.append(elements)
        stats["stats"] = statsList
        return json.dumps(stats)
    except Exception as e:
        print(e)
