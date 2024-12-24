import gradio as gr

INTERFACE_CONFIG = {
    "HTML_PATH": "src/templates/index.html",
    "CSS_PATH": "src/static/css/style.css",
    "THEME": gr.themes.Origin(
        primary_hue=gr.themes.colors.blue, radius_size=gr.themes.sizes.radius_xxl
    ),
}

# Application settings
APP_CONFIG = {
    "TEMP_DIR": "temp_uploads",
    "OUTPUT_TYPE": "html",
    "HOST": "127.0.0.1",
    "PORT": 8000,
}
