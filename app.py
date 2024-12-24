# Standard library imports
import os
import sys
import logging
from typing import Tuple, Optional

# Third-party imports
import gradio as gr
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from requests_toolbelt import MultipartEncoder

# Local imports
from configs.config import API_CONFIG, INTERFACE_CONFIG
from utils.constants import ERROR_MESSAGES, CUSTOM_STOPWORDS, MODEL_CHOICES
from utils.logging_config import configure_logging
from src.services.parser.exceptions import ResumeParsingError

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


class ResumeParser:
    def __init__(self):
        self.css_path = INTERFACE_CONFIG["CSS_PATH"]
        assert os.path.exists(self.css_path), "CSS file not found at the path"
        self.analyze_button = None
        self.loading_indicator = None
        self.questions_button = None
        self.num_questions = None
        self.questions_output = None
        self.wc_button = None
        self.num_words = None
        self.wordcloud_output = None
        self.wordcloud_summary = None
        self.model_choosen = ""

    def _handle_alert(self):
        # code to remove textbox is it exists on new file
        return gr.Textbox(value="", visible=False)

    def create_interface(self) -> gr.Blocks:
        """Creates and configures the Gradio interface"""
        with gr.Blocks(
            title="ResumeParser",
            css_paths=self.css_path,
            theme=INTERFACE_CONFIG["THEME"],
        ) as demo:
            gr.HTML(
                open(INTERFACE_CONFIG["HTML_PATH"], "r").read(),
                elem_id="markdown-title",
            )

            with gr.Row():
                file_upload = gr.File(
                    file_types=[".pdf"],
                    label="Upload PDF",
                    elem_id="upload_box",
                    file_count="multiple",
                    scale=1, 
                    min_width=100
                )

            with gr.Row():
                model_selected = gr.Dropdown(
                    choices=MODEL_CHOICES,
                    multiselect=False,
                    label="Select Model",
                    value="Select model from dropdown",
                    allow_custom_value=True,
                    elem_id="model_dropdown",
                )

                def update_model_choice(choice):
                    self.model_choosen = choice

                model_selected.change(
                    fn=update_model_choice,
                    inputs=[model_selected],
                    outputs=[],
                )
            # Parse Button
            with gr.Row():
                with gr.Column(scale=1):
                    pass
                with gr.Column(scale=1):
                    self.analyze_button = gr.Button("Parse", variant="primary", elem_id="parse_button")
                    self.loading_indicator = gr.HTML(
                        value='<div style="text-align: center; margin-top: 10px;"><h3 style="color: #2196F3;">⏳ Processing Resume...</h3></div>',
                        visible=False
                )
                with gr.Column(scale=1):
                    pass   
    
            # Output components
            with gr.Row():
                alert_output = gr.Textbox(
                    label="Alert", visible=False, elem_id="alert_box"
                )
            with gr.Row():
                parse_output_area = gr.HTML(label="Parsing Output")
            with gr.Row():
                issue_output_area = gr.HTML(label="Analysis Output")

            # Clear alert when new file is uploaded
            file_upload.change(
                fn=self._handle_alert, inputs=None, outputs=[alert_output]
            )

            # Analysis tools
            with gr.Row(equal_height=True):
                self._create_question_section()
                self._create_wordcloud_section()

            self._setup_event_handlers(
                file_upload,
                parse_output_area,
                alert_output,
                issue_output_area,
            )

        return demo

    def _create_question_section(self):
        """Creates the question generation section."""
        with gr.Column():
            with gr.Row(equal_height=True):
                self.questions_button = gr.Button(
                    "Fetch Questions",
                    variant="primary",
                    interactive=False,
                    elem_id="my_button",
                )
                with gr.Column():
                    self.num_questions = gr.Number(
                        value=5, label="Number of Questions", precision=0, maximum=10
                    )
                    self.skill_name = gr.Textbox(label="Skill Name")

            self.questions_output = gr.Textbox(
                label="Suggested interview questions", show_copy_button=True, lines=12
            )

    def _create_wordcloud_section(self):
        """Creates the wordcloud generation section."""
        with gr.Column():
            with gr.Row(equal_height=True):
                self.wc_button = gr.Button(
                    "Get WordCloud",
                    variant="primary",
                    interactive=False,
                    elem_id="my_button",
                )
                self.num_words = gr.Number(
                    value=5, label="Choose most frequent words", precision=0, maximum=10
                )
            self.wordcloud_output = gr.Plot(label="Resume WordCloud")
            self.wordcloud_summary = gr.Textbox(label="Top Keywords")

    def _fetch_skills_yoe(self, parse_html_table: str):

        try:
            soup = BeautifulSoup(parse_html_table, "html.parser")
            # Extract skills
            skills_row = soup.find("td", string="Technical Skills")
            if not skills_row:
                raise ValueError(ERROR_MESSAGES["SKILLS_NOT_FOUND"])

            skills = skills_row.find_next_sibling("td").get_text(strip=True)

            # Extract experience
            yoe_row = soup.find("td", string="Total Experience")
            if not yoe_row:
                raise ValueError(ERROR_MESSAGES["EXPERIENCE_NOT_FOUND"])
            yoe = yoe_row.find_next_sibling("td").get_text(strip=True)

            return skills, yoe

        except Exception as e:
            logger.error(f"Error in parsing html {e}")
            return None, None

    def process_resume(self, file: gr.File) -> Tuple[Optional[str], ...]:
        """Processes the uploaded resume file."""
        try:
            self.loading_indicator.visible = True  # Show loading before processing
            if file is None:
                return self._create_error_response(
                    ERROR_MESSAGES["FILE_UPLOAD_REQUIRED"]
                )

            # validate if multiple files are being uploaded, alert with an output
            if len(file) > 1:
                return self._create_error_response(ERROR_MESSAGES["MULTIPLE_FILES"])

            if not self.model_choosen:
                return self._create_error_response(
                    ERROR_MESSAGES["MODEL_SELECTION_ERROR"]
                )

            # Create MultipartEncoder for proper multipart/form-data formatting
            try:
                m = MultipartEncoder(
                    fields={
                        "file": (
                            "resume.pdf",
                            open(file[0].name, "rb"),
                            "application/pdf",
                        ),
                        "model": str(self.model_choosen),
                    }
                )
            except Exception as e:
                logger.error(f"File encoding error: {e}")
                return self._create_error_response(
                    ERROR_MESSAGES["MULTIPART_ENCODING_ERROR"]
                )

            try:
                response = requests.post(
                    API_CONFIG["PARSE_URL"],
                    data=m,
                    headers={"Content-Type": m.content_type},
                    timeout=660,
                )
                response.raise_for_status()
                if not response.ok:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    if "Only PDF files are supported" in error_detail:
                        return self._create_error_response(ERROR_MESSAGES["PDF_ONLY"])
                    elif "Failed to process resume file" in error_detail:
                        return self._create_error_response(
                            ERROR_MESSAGES["FILE_READ_ERROR"]
                        )
                    elif "Empty text extracted" in error_detail:
                        return self._create_error_response(ERROR_MESSAGES["EMPTY_TEXT"])
                    elif "Failed to parse resume content" in error_detail:
                        return self._create_error_response(
                            ERROR_MESSAGES["PARSE_ERROR"]
                        )
                    else:
                        return self._create_error_response(
                            f"{ERROR_MESSAGES['API_ERROR']}: {error_detail}"
                        )
            except requests.Timeout:
                return self._create_error_response(
                    ERROR_MESSAGES["API_TIMEOUT_ERROR"].format(str(5))
                )
            except requests.RequestException as e:
                error_detail = response.json().get("detail", str(e))
                return self._create_error_response(
                    f"{ERROR_MESSAGES['API_ERROR']}: {error_detail}"
                )

            result = response.json()
            if not result.get("result_table"):
                return self._create_error_response(ERROR_MESSAGES["EMPTY_TEXT"])

            logger.info(f'\n HTML RESULT SUMMARY - {result.get("result_table")}')
            logger.info(f'\n HTML RESULT ISSUES - {result.get("issue_table")}')

            self.loading_indicator.visible = False  # Hide loading after processing
            return self._create_success_response(result)

        except requests.Timeout:
            self.loading_indicator.visible = False
            return self._create_error_response(
                ERROR_MESSAGES["API_TIMEOUT_ERROR"].format(str(5))
            )

        except requests.RequestException as e:
            self.loading_indicator.visible = False
            if isinstance(e.response, requests.Response):
                error_detail = e.response.json().get("detail", str(e))
                return self._create_error_response(
                    f"{ERROR_MESSAGES['API_ERROR']}: {error_detail}"
                )
            return self._create_error_response(ERROR_MESSAGES["API_ERROR"])

        except ResumeParsingError as rpe:
            self.loading_indicator.visible = False
            logger.error(f"Resume parsing error: {rpe.message}")
            return self._create_error_response(
                f"{ERROR_MESSAGES['PARSE_ERROR']}: {rpe.message}"
            )
        except Exception as e:
            self.loading_indicator.visible = False
            logger.error(f"Unexpected error: {e}")
            return self._create_error_response(ERROR_MESSAGES["UNEXPECTED_ERROR"])

    def generate_wordcloud(
        self,
        num_words: int,
        temp_folder: str = "temp_uploads",
        filename: str = "raw_text.txt",
    ) -> Tuple[Optional[plt.Figure], str]:
        """Generates wordcloud and keyword summary."""
        try:
            file_path = os.path.join(temp_folder, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Text file not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            stopwords = set(STOPWORDS)
            stopwords.update(CUSTOM_STOPWORDS)

            wordcloud = WordCloud(
                width=400,
                height=200,
                scale=2,
                background_color="white",
                stopwords=stopwords,
            ).generate(text)

            # Display the generated image
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bicubic")
            ax.axis("off")

            # --- Generate Summary ---
            word_frequencies = wordcloud.words_
            top_words = sorted(
                word_frequencies.items(), key=lambda item: item[1], reverse=True
            )[:num_words]

            summary = "Top keywords:\n"
            for word, _ in top_words:
                summary += f"• {word}\n"

            # remove the last \n
            summary = summary[:-1]

            return fig, summary

        except Exception as e:
            logger.error(f"Error generating wordcloud: {e}")
            return None, ERROR_MESSAGES["WORDCLOUD_ERROR"]

    def generate_questions(
        self, parse_output_area: str, skill: str, num_questions: int
    ) -> str:
        """
        Generates interview questions based on parsed resume data.

        Args:
            parse_html_table (str): HTML table containing parsed resume data
            num_questions (int): Number of questions to generate

        Returns:
            str: Generated interview questions or error message
        """
        try:
            skills_list, yoe = self._fetch_skills_yoe(parse_output_area)
            logger.info(
                f"\n The skills fetched are {skills_list} and type {type(skills_list)} and yoe is {yoe}"
            )
            if yoe == "-" or yoe == "":
                yoe = "5 years"

            payload = {
                "model": self.model_choosen,
                "skills": skills_list,
                "adhoc_skill": skill,
                "num_questions": num_questions,
                "yoe": yoe,
            }

            # Send request to API
            response = requests.post(
                API_CONFIG["QUESTIONS_URL"], json=payload, timeout=240
            )
            response.raise_for_status()

            result = response.json()
            return result.get("questions", ERROR_MESSAGES["QUESTION_GENERATION_ERROR"])

        except requests.exceptions.RequestException as e:
            logger.error(f"API Error: {e}")
            return ERROR_MESSAGES["API_ERROR"]
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return ERROR_MESSAGES["QUESTION_GENERATION_ERROR"]

    def _create_error_response(self, error_message: str) -> Tuple:
        return (
            None,
            None,
            gr.update(value=error_message, visible=True),
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    def _create_success_response(self, result: dict) -> Tuple:
        return (
            result.get("result_table"),
            result.get("issue_table"),
            gr.update(visible=False, value=""),
            gr.update(interactive=True),
            gr.update(interactive=True),
        )

    def _setup_event_handlers(
        self,
        file_upload,
        parse_output_area,
        alert_output,
        issue_output_area,
    ):
        """Sets up all event handlers for the Gradio interface components."""

        self.analyze_button.click(
                fn=lambda: gr.update(visible=True),  # Show loading message
                outputs=[self.loading_indicator],
        ).then(
            fn=self.process_resume,
            inputs=file_upload,
            outputs=[
                parse_output_area,
                issue_output_area,
                alert_output,
                self.questions_button,
                self.wc_button,
            ],
            show_progress='minimal'
        ).then(
                fn=lambda: gr.update(visible=False),  # Hide loading
                outputs=[self.loading_indicator]
            )

        self.wc_button.click(
            fn=self.generate_wordcloud,
            inputs=self.num_words,
            outputs=[self.wordcloud_output, self.wordcloud_summary],
        )

        self.questions_button.click(
            fn=self.generate_questions,
            inputs=[parse_output_area, self.skill_name, self.num_questions],
            outputs=self.questions_output,
        )
