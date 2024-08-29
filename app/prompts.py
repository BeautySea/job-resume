import asyncio

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from decouple import config
import tiktoken

from app.schemas import First, Second, Third, FirstATS, SecondATS


def get_number_of_tokens(documents):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    encoding.encode(documents)
    number_tokens = len(encoding.encode(documents))
    return number_tokens


async def extract_resume_schema(pages):
    db = Chroma.from_documents(pages, OpenAIEmbeddings(
        openai_api_key=config("OPENAI_API_KEY")))

    first_documents = db.similarity_search(
        "Extract the personal_information and education in this resume. Education is different from certificate ",
        k=4)
    second_documents = db.similarity_search("Extract the  "
                                                      "work experience, skills and certifications in "
                                                      "this resume", k=10)

    first_output_parser = PydanticOutputParser(pydantic_object=First)
    second_output_parser = PydanticOutputParser(pydantic_object=Second)
    third_output_parser = PydanticOutputParser(pydantic_object=Third)

    first_format_instructions = first_output_parser.get_format_instructions()
    second_format_instructions = second_output_parser.get_format_instructions()
    third_format_instructions = third_output_parser.get_format_instructions()

    first_template = """
        Extract the personal_information and education in this resume. Education is different from certificate. 

        The resume is: {first_documents}  

        Format instructions: {format_instructions}

        """
    first_prompt = PromptTemplate(
        template=first_template,
        input_variables=["first_documents"],
        partial_variables={"format_instructions": first_format_instructions})

    second_template = """Extract the work_experience, and certifications in this resume. 
    
            The resume is: {second_documents}  

            Format instructions: {format_instructions}

            """
    second_prompt = PromptTemplate(
        template=second_template,
        input_variables=["second_documents"],
        partial_variables={"format_instructions": second_format_instructions})

    third_template = """Extract the skills in this resume. When there are more than one skill on a line, break a line of
     skills into each skill. The response for the 
        skills, should be one skill per line, proficiency_level, and years_of_experience. The years_of_experience of 
        the skill should be based on the number of years the skill was mentioned in the work_experience responsibility.
         
        
        For examples:
        
            AWS, Microsoft Azure
            Response: 
                skill: AWS
                proficiency_level: Advanced
                years_of_experience: 5
                
                skill: Microsoft Azure
                proficiency_level: Advanced
                years_of_experience: 4
                
                        
            Scripting experience (Linux, Python, Bash, PowerShell)
            Response:
                skill: Linux
                proficiency_level: Advanced
                years_of_experience: 5
                
                skill: Python
                proficiency_level: Advanced
                years_of_experience: 5
                
                skill: Bash
                proficiency_level: Advanced
                years_of_experience: 5
                
                skill: PowerShell
                proficiency_level: Advanced
                years_of_experience: 5    

                The resume is: {third_documents}  

                Format instructions: {format_instructions}

                """
    third_prompt = PromptTemplate(
        template=third_template,
        input_variables=["third_documents"],
        partial_variables={"format_instructions": third_format_instructions})

    llm = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"), temperature=0.0, model_name='gpt-3.5-turbo-0125')

    first = first_prompt | llm | first_output_parser
    second = second_prompt | llm | second_output_parser
    third = third_prompt | llm | third_output_parser

    tasks = [first.ainvoke({"first_documents": first_documents}),
             second.ainvoke({"second_documents": second_documents}),
             third.ainvoke({"third_documents": second_documents})]

    list_of_tasks = await asyncio.gather(*tasks)

    db.delete_collection()
    return list_of_tasks


async def analyze_resume_schema(pages, career_name):
    db = Chroma.from_documents(pages, OpenAIEmbeddings(openai_api_key=config("OPENAI_API_KEY")))

    first_documents = db.similarity_search(
        "Extract the personal_information and education in this resume. Education is different from certificate",
        k=4)
    second_documents = db.similarity_search("Extract the work experience in this resume.", k=10)

    first_output_parser = PydanticOutputParser(pydantic_object=FirstATS)
    second_output_parser = PydanticOutputParser(pydantic_object=SecondATS)

    first_format_instructions = first_output_parser.get_format_instructions()
    second_format_instructions = second_output_parser.get_format_instructions()

    first_template = """
                Extract the email_address. Check if the email_address don't exist, return No. If email_address exist, return Yes.
                Extract the phone_number. Check if the phone_number don't exist, return No. If phone_number exist, return Yes.
                Extract the linkedin. Check  if the linkedin don't exist, return No. If linkedin exist, return Yes.
    
        The resume is: {first_documents}  

        Format instructions: {format_instructions}

        """
    first_prompt = PromptTemplate(
        template=first_template,
        input_variables=["first_documents"],
        partial_variables={"format_instructions": first_format_instructions})

    second_template = """
                Compare this {career_name} with this resume, Analyze and measure this resume based on the following parameters:
                total_work_experience_count, keyword_count, job_title_keyword_count, 
                keyword_stuffing_count, general_keyword_count, category_keyword_count, ats_keywords_to_add, and, 
                general_keywords_to_add.
                
                The total_work_experience_count is defined by the total number of work_experience in the resume. Count
                the total_work_experience in the resume.
                 
                The keyword is defined by the strong action verbs used in the {career_name}. The keyword_count is the 
                number of keywords used in the {career_name} and are mentioned in the resume.  
                Count the total number of keywords used in the {career_name} and are mentioned in the resume. Extract 
                the keywords used in the {career_name} and are mentioned in the resume. 
                For example: 
                    career_name: Machine Learning Engineer
                    resume_accomplishment_statement: Led a team of four developers to build a chatbot application using 
                                                     Python, Transformers, and ChatGPT API that can answer user queries 
                                                     and provide person. Troubleshot and debugged software issues using 
                                                     various tools and methodologies.
                    keywords: led, build, Troubleshot, debugged
                    keyword_count: 4
                
                The job_title_keyword is defined by the job title used in the {career_name}. The job_title_keyword_count 
                is the number of job_title_keyword used in the {career_name} and are mentioned in the resume. Count the 
                total number of job_title_keyword used in the {career_name} and are mentioned in the resume. 
                For example:
                    career_name: Machine Learning Engineer
                    job_title: Machine Learning Engineer
                    resume_accomplishment_statement: Led a team of four developers to build a chatbot application using 
                                                     Python, Transformers, and ChatGPT API that can answer user queries 
                                                     and provide person. This is a Generative AI. Troubleshot and 
                                                     debugged software issues using various tools and methodologies.
                    job_title_keyword: Machine Learning Engineer
                    job_title_keyword_count: 1
                    
                The general_keyword is defined by the professional terms used in the {career_name}. The 
                general_keyword_count is the number of general_keyword used in the {career_name} and are mentioned in 
                the resume. Count the total number of general_keyword used in the {career_name} and are mentioned in the 
                resume.
                For example:
                    career_name: Machine Learning Engineer
                    resume_accomplishment_statement: Led a team of four developers to build a chatbot application using 
                                                     Python, Transformers, and ChatGPT API that can answer user queries 
                                                     and provide person. Troubleshot and debugged software issues using 
                                                     various tools and methodologies.
                    general_keywords: team, developers, chatbot, application, software, methodologies
                    general_keyword_count: 6
                
                The category_keyword is defined by the name of the tools, frameworks, libraries that are required in the
                {career_name}. The category_keyword_count is the number of category_keyword used in the {career_name} 
                and are mentioned in the resume. Count the total number of category_keyword used in the {career_name} 
                and are mentioned in the resume. 
                For example:
                    career_name: Machine Learning Engineer
                    resume_accomplishment_statement: Led a team of four developers to build a chatbot application using 
                                                     Python, Transformers, and ChatGPT API that can answer user queries 
                                                     and provide person. Troubleshot and debugged software issues using 
                                                     various tools and methodologies.
                    category_keywords: Python, Transformers, and ChatGPT API 
                    category_keyword_count: 3
                    
                Generate the list of strong action verbs only that are related with {career_name}. 
                This must not be in the resume. This is the ats_keywords_to_add. Maximum of 15
                
                Generate the list of professional terms that are related with {career_name}. This must not be in the resume. 
                This is the general_keyword_to_add. Maximum of 15.
                  
            The resume is: {second_documents}  

            Format instructions: {format_instructions}

            """
    second_prompt = PromptTemplate(
        template=second_template,
        input_variables=["second_documents", "career_name"],
        partial_variables={"format_instructions": second_format_instructions})

    llm = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"), temperature=0.0, model_name='gpt-3.5-turbo-0125')
    llm_second_prompt = ChatOpenAI(openai_api_key=config("OPENAI_API_KEY"), temperature=0.0, model_name='gpt-4-0125-preview')

    first = first_prompt | llm | first_output_parser
    second = second_prompt | llm_second_prompt | second_output_parser

    tasks = [
        first.ainvoke({"first_documents": first_documents}),
        second.ainvoke({"second_documents": second_documents, "career_name": career_name}),
    ]

    list_of_tasks = await asyncio.gather(*tasks)

    db.delete_collection()
    return list_of_tasks

