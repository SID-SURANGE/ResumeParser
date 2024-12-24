import logging
from typing import Dict, Any, List
from datetime import datetime

from src.services.parser.exceptions import ResumeParsingError
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Handles extraction and organization of entities from resume sections.

    This class is responsible for extracting structured information from
    resume data including education, experience, skills, and other relevant fields.
    """

    def extract_entities(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and organizes entities from resume data.

        Args:
            resume_data (Dict[str, Any]): Dictionary containing resume sections

        Returns:
            Dict[str, Any]: Dictionary containing organized resume entities

        Raises:
            ResumeParsingError: If required data is missing or invalid
        """
        try:
            self._validate_resume_data(resume_data)

            # Extract basic fields
            entities = self._extract_basic_fields(resume_data)

            # Extract education information
            education_info = self._extract_education_info(resume_data)
            entities.update(education_info)

            # Validate extracted entities
            if not any(entities.values()):
                raise ResumeParsingError(
                    message="No valid entities extracted",
                    code=5004,
                    details={"entities": entities},
                )
            logger.info("ENTITIES DICT BEFORE CREATING HTML ", entities)
            return self._generate_html_table(entities)

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise ResumeParsingError(
                message="Failed to extract resume entities",
                code=5005,
                details={"error": str(e)},
            )

    def _validate_resume_data(self, resume_data: Dict[str, Any]) -> None:
        """
        Validates resume data before processing.

        Args:
            resume_data (Dict[str, Any]): Resume data to validate

        Raises:
            ResumeParsingError: If data format is invalid or required fields are missing
        """
        if not isinstance(resume_data, dict):
            raise ResumeParsingError(
                message="Invalid resume data format",
                code=5001,
                details={"type": type(resume_data).__name__},
            )

        required_fields = ["Professional_Summary", "Total_experience", "Skills"]
        for field in required_fields:
            if field not in resume_data:
                raise ResumeParsingError(
                    message=f"Missing required field: {field}",
                    code=5002,
                    details={"missing_field": field},
                )

    def _extract_basic_fields(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts basic fields from resume data.

        Args:
            resume_data (Dict[str, Any]): Resume data containing basic fields

        Returns:
            Dict[str, Any]: Dictionary containing extracted basic fields
        """
        # Combine job titles and companies into work experience
        work_experience = []
        professional_exp = resume_data.get("Professional_Experience", [])
        for exp in professional_exp:
            if exp.get("Position_or_Role") or exp.get("Company"):
                work_experience.append(
                    {
                        "title": exp.get("Position_or_Role", "-"),
                        "company": exp.get("Company", "-"),
                        "duration": exp.get("Duration", "-"),
                    }
                )

        return {
            "summary": resume_data.get("Professional_Summary", "-"),
            "total_exp": resume_data.get("Total_experience", "-"),
            "work_experience": work_experience,
            "career_gap": resume_data.get("Professional_Career_Gap", "-"),
            "awards": [
                award.get("Title")
                for award in resume_data.get("Awards_and_Achievements", [])
                if award.get("Title")
            ],
            "skills": resume_data.get("Skills", {}),
            "projects": resume_data.get("Projects", []),
            "certifications": resume_data.get("Certifications", []),
            "competitions": resume_data.get("Competitions", []),
            "publications": resume_data.get("Publications", []),
            "references": resume_data.get("References", []),
            "languages": resume_data.get("Languages", []),
        }

    def _parse_date(self, duration):
        # Split the duration string into start and end parts
        parts = duration.split(" to ")

        # Assume the end date is the last part, otherwise use the entire string
        end_date_str = parts[-1].strip()

        # Define possible date formats
        date_formats = ["%b %Y", "%Y", "%b %Y", "%b %Y"]

        # Try to parse the end date using different formats
        for fmt in date_formats:
            try:
                return datetime.strptime(end_date_str, fmt)
            except ValueError:
                continue
        return datetime.min  # Return a very old date if parsing fails

    def _extract_education_info(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts education information from resume data.

        Args:
            resume_data (Dict[str, Any]): Resume data containing education information

        Returns:
            Dict[str, Any]: Dictionary containing education information

        Raises:
            ResumeParsingError: If education data processing fails
        """
        try:
            education = resume_data.get("Education", [])
            if education:
                logger.info("------------education info", education)
                highest_degree = max(
                    education,
                    key=lambda x: self._parse_date(x.get("Duration", "")),
                    default={},
                )
                if not highest_degree:
                    logger.warning("No valid education entries found")

                return {
                    "highest_degree": highest_degree.get("Degree_or_Course", "-"),
                    "institution": highest_degree.get("Institution", "-"),
                    "graduation_date": highest_degree.get("Duration", "-"),
                }
            else:
                logger.warning("No education information found")
                return {
                    "highest_degree": "-",
                    "institution": "-",
                    "graduation_date": "-",
                }
        except Exception as e:
            logger.error(f"Error processing education data: {e}")
            raise ResumeParsingError(
                message="Failed to process education information",
                code=5003,
                details={"error": str(e)},
            )

    def _generate_html_table(self, entities: Dict[str, Any]) -> str:
        """Generates HTML table from extracted entities."""
        try:

            # Validate input
            if not entities:
                raise ResumeParsingError(
                    message="Empty entities dictionary provided",
                    code=6001,
                    details={"entities": entities},
                )

            work_experience = entities.get("work_experience", []) or []
            awards = entities.get("awards", []) or []
            projects = entities.get("projects", []) or []
            certifications = entities.get("certifications", []) or []
            competitions = entities.get("competitions", []) or []
            publications = entities.get("publications", []) or []
            references = entities.get("references", []) or []
            languages = entities.get("languages", []) or []

            # skill extraction
            skills_data = entities.get("skills", {}) or {}
            technical_skills = skills_data.get("Technical_Skills", "-")
            soft_skills = skills_data.get("Soft_Skills", "-")

            html_table = """
            <!DOCTYPE html>
            <html>
            <head>
            <title>Resume Parser</title>
            <style>
                .output-area { 
                    width: 100%; 
                }
                table {
                    width: 100%; 
                    table-layout: fixed;  /* Added for fixed layout */
                    border-collapse: collapse; 
                    max-height: 300px;  /* Adjust as needed */
                    overflow-y: auto;  /* Added for scrolling */
                }
                th, td {
                    border: 1px #e0e0e0 !important; 
                    padding: 10px;  
                }

                th {
                    background-color: #e0e0e0 !important;
                }
                
                th:first-child {  /* Target the first <th> element (Field) */
                    width: 20%;
                }
                th:last-child {  /* Target the last <th> element (Details) */
                    width: 80%;
                }
            </style>
            </head>
            <body>
            <div class="output-area">
                <table>
                <thead style="background-color: #e0e0e0 !important;">
                    <tr>
                    <th style="border: 1px #e0e0e0 !important; text-align: center; background-color: #e0e0e0 !important;">Field</th>
                    <th style="border: 1px #e0e0e0 !important; text-align: center; background-color: #e0e0e0 !important;">Details</th>
                    </tr>
                </thead>
                <tbody>
            """

            # Add the entities to the HTML table
            html_table += f"<tr><td>Professional Summary</td><td>{entities.get('summary', '-')}</td></tr>"
            html_table += f"<tr><td>Total Experience</td><td>{entities.get('total_exp', '-')}</td></tr>"

            # Handle lists (Work exp, Awards)
            html_table += """
            <tr>
                <td>Work Experience</td>
                <td>
            """
            if not work_experience:
                html_table += "-"
            else:
                for exp in work_experience:
                    html_table += f"""
                        <div style="margin-bottom: 15px;">
                            <strong>{exp['title']}</strong> at <em>{exp['company']}</em><br>
                            <span style="color: #666;">{exp['duration']}</span><br>
                        </div>
                    """
            html_table += """
                </td>
            </tr>
            """
            html_table += (
                f"<tr><td>Career Gap</td><td>{entities.get('career_gap','-')}</td></tr>"
            )
            html_table += f"<tr><td>Awards</td><td>{'-' if not awards else '<br>'.join(awards)}</td></tr>"

            html_table += f"<tr><td>Highest Degree</td><td>{entities.get('highest_degree', '-')}</td></tr>"
            html_table += f"<tr><td>Institution</td><td>{entities.get('institution', '-')}</td></tr>"
            html_table += f"<tr><td>Graduation Date</td><td>{entities.get('graduation_date','-')}</td></tr>"

            # Function to split strings or handle lists
            def split_or_pass(skills):
                if isinstance(skills, str):
                    return skills.split("\n")
                return skills

            technical_skills = split_or_pass(technical_skills)
            soft_skills = split_or_pass(soft_skills)

            # Remove empty strings and handle default case
            technical_skills = [
                skill for skill in technical_skills if skill and skill not in ["-", "•"]
            ]
            soft_skills = [
                skill for skill in soft_skills if skill and skill not in ["-", "•"]
            ]

            # Generate HTML for technical skills in a bulleted format
            html_table += f"""
            <tr>
                <td>Technical Skills</td>
                <td>
                    {'-' if len(technical_skills) == 0 else '<ul style="margin: 0; padding: 0; list-style-type: none;">' + ''.join([f'<li style="margin-bottom: 5px;">• {skill}</li>' for skill in technical_skills]) + '</ul>'}
                </td>
            </tr>
            """
            # Generate HTML for soft skills in a bulleted format
            html_table += f"""
            <tr>
                <td>Soft Skills</td>
                <td>
                    {'-' if len(soft_skills) == 0 else '<ul style="margin: 0; padding: 0; list-style-type: none;">' + ''.join([f'<li style="margin-bottom: 5px;">• {skill}</li>' for skill in soft_skills]) + '</ul>'}
                </td>
            </tr>
            """

            # Handle projects with only project name
            project_names = [proj.get("Name", "Unknown Project") for proj in projects]
            html_table += f"<tr><td>Projects</td><td>{'-' if not project_names else '<br>'.join([f'• {name}' for name in project_names])}</td></tr>"

            if isinstance(certifications, str):
                certifications = certifications.split(", ")

            certification_titles = []
            for cert in certifications:
                if isinstance(cert, dict):
                    cert_title = cert.get("Title", "-")
                    certification_titles.append(cert_title)
                else:
                    certification_titles.append(cert)

            html_table += f"""
            <tr>
                <td>Certifications</td>
                <td>
                    {'-' if not certification_titles else '<ul style="margin: 0; padding: 0; list-style-type: none;">' + ''.join([f'<li style="margin-bottom: 5px;">• {title}</li>' for title in certification_titles]) + '</ul>'}
                </td>
            </tr>
            """

            # Show competitions in a bulleted format
            competitions_list = [comp.get("Name") for comp in competitions]
            html_table += f"<tr><td>Competitions</td><td>{'-' if not competitions_list else '<br>'.join([f'• {name}' for name in competitions_list])}</td></tr>"

            # Show only the title of publications
            publication_titles = [
                pub.get("Title", "Unknown Publication") for pub in publications
            ]
            html_table += f"<tr><td>Publications</td><td>{'-' if not publication_titles else '<br>'.join(publication_titles)}</td></tr>"

            # Show only the position and company of each reference
            reference_info = [
                f"{ref.get('Position', 'Unknown Position')}, {ref.get('Company', 'Unknown Company')}"
                for ref in references
            ]
            html_table += f"<tr><td>References</td><td>{'-' if not reference_info else '<br>'.join(reference_info)}</td></tr>"

            # Show competitions in a bulleted format
            languages_list = [lang.get("Language") for lang in languages]
            languages_list = [lang for lang in languages_list if lang]
            html_table += f"<tr><td>Languages</td><td>{'-' if not languages_list else '<br>'.join([f'• {name}' for name in languages_list])}</td></tr>"

            # create the html structure for our response
            html_table += """
                </tbody>
                </table>
            </div>
            </body>
            </html>
            """

            return html_table

        except Exception as e:
            logger.error(f"Error generating HTML table: {e}")
            raise ResumeParsingError(
                message="Failed to generate HTML table",
                code=6003,
                details={"error": str(e)},
            )
