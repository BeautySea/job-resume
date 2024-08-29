from typing import List, Dict, Union

from langchain_core.pydantic_v1 import BaseModel, Field


class First(BaseModel):
    personal_information: Union[Dict[str, str], None] = Field(
        description='Extract a Python dictionary of the personal information in the resume. The following keys are full_name, email, phone, address, linkedin, personal_website')
    education: Union[List[Dict[str, str]], None] = Field(
        description='Generate a List of dictionaries containing the education detail in the resume. The following keys in the dictionary are institution, degree, field_of_study, start_date, end_date.')


class Second(BaseModel):
    work_experience: Union[List[Dict[str, str]], None] = Field(
        description='Extract a List of dictionaries containing the work experience. The following keys in the dictionary are company, position, start_date, and end_date')
    certifications: Union[List[Dict[str, str]], None] = Field(
        description='Generate a List of dictionaries containing the certifications. The following keys in the dictionary are name, issuing_organization, issue_date, expiry_date')


class Third(BaseModel):
    skills: Union[List[Dict[str, str]], None] = Field(description='Generate a List of dictionaries containing the skills. The following keys in the dictionary are name, proficiency_level, years_of_experience')


class FirstATS(BaseModel):
    email_score: str = Field('email_score')
    phone_score: str = Field('phone_score')
    linkedin_score: str = Field('linkedin_score')


class SecondATS(BaseModel):
    keyword_count: Union[int, None] = Field('keyword_count')
    keywords: Union[List[str], None] = Field('keywords')
    job_title_count: Union[int, None] = Field('job_title_count')
    general_keyword_count: Union[int, None] = Field('general_keyword_count')
    category_keyword_count: Union[int, None] = Field('category_keyword_count')
    category_keywords: Union[List[str], None] = Field('category_keywords')
    total_work_experience_count: Union[int, None] = Field('total_work_experience')
    ats_keywords_to_add: List[str] = Field(
        'List of career and domain keywords to add to the resume to improve the ats_keyword_score')
    general_keywords_to_add: List[str] = Field(
        'list of the general keywords to add to the resume to improve the general_keyword_score')



