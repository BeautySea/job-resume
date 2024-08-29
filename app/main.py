from typing import Annotated, Union

import requests
from fastapi import FastAPI, UploadFile, File, status, Form, Header, Response

from pypdf import PdfReader
from docx import Document as Doc
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .calculators import get_readability_level, get_contact_score, calculate_ats_keyword_score, \
    get_readability_score, calculate_job_title_score, calculate_percentage, calculate_keyword_stuffing_score
from .prompts import extract_resume_schema, analyze_resume_schema

app = FastAPI()


URL = "https://quick-apply-b4e936c5c50c.herokuapp.com/api/v1/users/verifications"


def check_doc_type(document: Annotated[UploadFile, File()]):
    if document.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        docs = Doc(document.file)
        paragraphs = [paragraph.text for paragraph in docs.paragraphs]
        texts = " ".join(paragraphs)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False
        )
        pages = text_splitter.create_documents([texts])
        return pages, texts
    elif document.content_type == "application/pdf":
        reader = PdfReader(document.file)
        pages = [Document(page_content=page.extract_text()) for page_number, page in enumerate(reader.pages)]
        texts = " ".join(page.page_content for page in pages)
        return pages, texts


@app.post("/generate/", status_code=status.HTTP_201_CREATED)
async def generate_resume(resume: Annotated[UploadFile, File()],
                          authorization: Annotated[Union[str, None], Header(name="Authorization")], response: Response):
    verification_response = requests.get(url=URL, headers={"Authorization": authorization})
    if verification_response.text == "OK":
        pages, text = check_doc_type(resume)
        result = await extract_resume_schema(pages=pages)
        return {"data": result, "status": status.HTTP_201_CREATED}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"data": "Error", "status": status.HTTP_401_UNAUTHORIZED, "message": "Not Authorized"}


@app.post("/analyze/", status_code=status.HTTP_201_CREATED)
async def analyze_resume(resume: Annotated[UploadFile, File()], career_name: Annotated[str, Form()],
                         authorization: Annotated[Union[str, None], Header(name="Authorization")], response: Response):
    verification_response = requests.get(url=URL, headers={"Authorization": authorization})
    if verification_response.text == "OK":
        pages, text = check_doc_type(resume)
        results = await analyze_resume_schema(pages=pages, career_name=career_name)
        email_score, phone_score, linkedin_score = results[0].email_score, results[0].phone_score, results[0].linkedin_score
        contact_info = get_contact_score(email_score=email_score, phone_score=phone_score, linkedin_score=linkedin_score)

        keywords, keyword_count, job_title_count, general_keyword_count, category_keywords, category_keyword_count, total_work_experience_count\
            = (results[1].keywords, results[1].keyword_count, results[1].job_title_count, results[1].general_keyword_count,
               results[1].category_keywords, results[1].category_keyword_count, results[1].total_work_experience_count)

        keyword_score = calculate_percentage(text=text, count=keyword_count)
        general_keyword_score = calculate_percentage(text=text, count=general_keyword_count)
        category_keyword_score = calculate_percentage(text=text, count=category_keyword_count)
        keyword_stuffing_score, category_keyword_stuffing_score = (
            calculate_keyword_stuffing_score(text=text, keywords=keywords, category_keywords=category_keywords))

        job_title_score = calculate_job_title_score(job_title_count=job_title_count,
                                                    total_work_experience_count=total_work_experience_count)

        readability_score = get_readability_score(text=text)
        readability_level = get_readability_level(readability_score=readability_score)

        ats_keyword_score = calculate_ats_keyword_score(
            keyword_score=keyword_score,
            category_keyword_score=category_keyword_score, general_keyword_score=general_keyword_score,
            email_score=email_score, phone_score=phone_score, linkedin_score=linkedin_score,
            job_title_score=job_title_score, readability_score=readability_score,
            keyword_stuffing_score=keyword_stuffing_score, category_keyword_stuffing_score=category_keyword_stuffing_score
        )
        result = {
            "email_score": email_score,
            "phone_score": phone_score,
            "linkedin_score": linkedin_score,
            "contact_info_score": contact_info,

            "keyword_score": keyword_score,
            # "keywords": keywords,
            "keyword_stuffing_score": keyword_stuffing_score,
            "category_keyword_score": category_keyword_score,
            # "category_keywords": category_keywords,
            "category_keyword_stuffing_score": category_keyword_stuffing_score,
            "general_keyword_score": general_keyword_score,
            "job_title_score": job_title_score,

            "readability_score": readability_score,

            "readability_level": readability_level,

            "ats_keyword_score": ats_keyword_score,

            "ats_keywords_to_add": results[1].ats_keywords_to_add,
            "general_keywords_to_add": results[1].general_keywords_to_add,
        }
        return {"data": result, "status": status.HTTP_201_CREATED}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"data": "Error", "status": status.HTTP_401_UNAUTHORIZED, "message": "Not Authorized"}
