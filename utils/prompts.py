# declare all the prompts for the tasks
PROMPT_TEXT_SECTIONS = """You are an expert AI resume parser specializing in content classification. Your task is to analyze resume content and categorize it into standardized sections.

                    Output Requirements:
                    1. Return ONLY a JSON object with predefined section categories as keys
                    2. Each section's content must be cleaned of:
                    - HTML tags
                    - Special characters
                    - Excessive whitespace
                    3. Maintain proper formatting for:
                    - Lists (convert to comma-separated text)
                    - Dates (standardize format)

                    Rules:
                    1. Classify all content into appropriate sections
                    2. Use 'Others' section for unclassified content
                    3. Include all section keys in output, even if empty
                    4. Preserve important formatting like bullet points as text
                    5. Maintain chronological order in experience/education sections
                    6. Keep technical terms, certifications, and proper nouns intact
                    7. No PII information shall be extracted

                    Below is the format for the output JSON :
                    """
MAIN_SECTIONS = """
                {
                "Professional_Summary": "# Extract or generate a concise summary of the candidate's professional background based on the resume content. Focus on key skills, roles. Limit the response to max 2 sentences.",
                "Total_experience": "# Be realistic and Calculate the total professional experience by summing up the durations of all positions listed in the work experience. Use the start and end dates provided for each position/role. If only years are mentioned, assume the start and end as January 1st of those years. Exclude overlapping periods from the calculation.",
                "Professional_Experience": [
                    {
                    "Company": "# Name of the company where he worked full time or did internship",
                    "Position_or_Role": "# Job title or role",
                    "Duration": "# Time period of employment",
                    "Location": "# City, Country",
                    "Responsibilities": "# List of key responsibilities"
                    }
                ],
                "Professional_Career_Gap": "# Identify any employment gaps by analyzing the timeline of positions listed in the resume. Compare the end date of one position with the start date of the next. For gaps exceeding 3 months, provide details including: 1) Start and end dates of each gap, 2) Duration of each gap in months. Additionally, check for overlapping employment periods and exclude them from gap calculations.",
                "Education": [
                    {
                    "Institution": "# Name of the educational institution",
                    "Degree_or_Course": "# Degree or course name",
                    "Duration": "# Time period of education",
                    "Location": "# City, Country"
                    }
                ],
                "Certifications": [
                    {
                    "Title": # name of the certification, 
                    "Issuing_Organization": # name of the org which issued the certificate, 
                    "Issue_Date": # date of issue
                    }
                ],
                "Skills": {
                    "Technical_Skills": "# List of technical skills given explicitly in the skills section for input text",
                    "Soft_Skills": "# List of soft skills if explicitly given in the input text",
                    "Strengths" : "# List strengths if the section is found in resume text"
                    }
                ,
                "Projects": [
                    {
                    "Name": "# Project name",
                    "Client": "# Client name",
                    "Duration": "# Time period of the project",
                    "Company": "# Company where the project was done",
                    "Description": "# Detailed description of the project"
                    }
                ],
                "Awards_and_Achievements": [
                    {
                    "Title": "# Title of the award or achievement",
                    "Company": "# Company or organization",
                    "Description": "# Description of the award or achievement"
                    }
                ],
                "Competitions": [
                    {
                        "Name": "# Name of competition",
                        "Position_Achieved": "# Position or recognition received",
                        "Date": "# Date of competition"
                    }
                ],
                "Extracurricular_Activities": [
                    {
                        "Activity_Name": "# Name of activity",
                        "Organization": "# Organization involved",
                        "Duration": "# Duration of involvement",
                        "Description": "# Description of activity"
                    }
                ],
                "Volunteer_Experience": [
                    {
                    "Organization": "# Name of the organization",
                    "Role": "# Volunteer role",
                    "Duration": "# Time period of volunteering",
                    "Location": "# City, Country",
                    "Description": "# Description of volunteer work"
                    }
                ],
                "Publications": [
                    {
                    "Title": "# Title of the publication",
                    "Authors": "# Authors of the publication",
                    "Publication_Name": "# Name of the journal or publication",
                    "Date": "# Date of publication",
                    "Description": "# Brief description of the publication"
                    }
                ],
                "Interests": [
                    {
                    "Interest": "# Personal interest or hobby",
                    "Details": "# Additional details about the interest"
                    }
                ],
                "Languages": [
                    {
                        "Language": "# Extract the name of each language explicitly mentioned in the 'Languages' section of the resume. Look for keywords such as 'English,' 'French,' or other spoken/written languages.",
                        "Proficiency_level": "# Identify the proficiency level associated with each language, if explicitly mentioned. Use terms like 'Native,' 'Fluent,' 'Conversational,' or 'Basic.' If no proficiency level is provided, leave this field blank."
                    }
                ],
                "References": [
                    {
                    "Name": "# Name of the reference",
                    "Position": "# Job title or role of the reference",
                    "Company": "# Company where the reference works",
                    "Contact_Information": "# Contact information of the reference"
                    }
                ],
                "Social_Links": [
                    {
                    "Platform": "# Social media platform",
                    "Link": "# URL to social media profile"
                    }
                ],
                "Others": "# Any other relevant information"
                }

                """

USER_PROMPT_SECTIONS = """Parse and categorize the following resume content into appropriate sections:

                    Requirements:
                    1. Remove all HTML tags and formatting, except Newlines
                    2. Maintain content structure and readability
                    3. Follow exact JSON format specified
                    4. Preserve important details and dates
                    5. Keep professional terminology intact

                    Resume Content:
                    """


PROMPT_TEXT_FOR_QUE = """
                    You are an expert technical interviewer. Generate {que_count} clear and concise technical interview questions based on the candidate's skill set.

                    Instructions:
                    - Generate questions that cover multiple skills when possible
                    - Each question must start with a bullet point (•)
                    - One question per line
                    - No explanations or additional text
                    - No markdown formatting or special characters
                    - Questions should be clear and professional
                    - Focus on practical application and problem-solving
                    - Only return the number of questions as asked, no less or more

                    Example format:
                    • <question>
                    • <question>

                    The interview questions count must be limited to max """

USER_PROMPT_FOR_QUE = "Generate technical interview questions covering these skills: "

PROMPT_TEXT_FOR_QUE_ADHOC_SKILL = """
                    You are an expert technical interviewer. Generate {que_count} clear and concise interview questions for the given skill.
                    Rules:
                    - Each question should start with a bullet point (•)
                    - No explanations or additional text
                    - No markdown formatting
                    - One question per line
                    - No quotes or special characters
                    - Questions should be direct and professional
                    - Only return the number of questions as asked, no less or more

                    Example format:
                    • <question>
                    • <question>

                    The interview questions count must be limited to max """

USER_PROMPT_FOR_QUE_ADHOC_SKILL = (
    "Generate technical interview questions for this skill: "
)


PROMPT_TEXT_SPELL_CHECK = """You are a professional resume reviewer specializing in spelling accuracy. Your task is to identify genuine spelling errors in resume text.

                        Instructions:
                        - Focus only on clear spelling mistakes and ignore case sensitivity
                        - Ignore technical terms, company names, and industry acronyms
                        - Consider context when identifying errors
                        - Return only a JSON response in this format:
                        {
                            "misspelled_words": [
                                {
                                    "incorrect_word": "example",
                                    "correct_word": "corrected"
                                }
                            ]
                        }

                        Rules:
                        - Do not flag proper nouns or company names
                        - Do not consider case sensitivity
                        - Do not flag technical terms or programming languages
                        - Do not flag common industry abbreviations
                        - Only identify unambiguous spelling errors
                        """

USER_PROMPT_SPELL_CHECK = """Check the following resume text for spelling errors:"""
