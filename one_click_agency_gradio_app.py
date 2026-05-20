"""
The One-Click Agency: Marketing Autopilot for Uncle Haq's Makerspace
Professional Gradio + Gemini Version

This is the simple website-style toolkit for the capstone project.
It can run in two ways:
1. Mock Demo Mode: no Gemini API key needed.
2. Gemini Mode: uses GEMINI_API_KEY to generate fresh AI output.

Windows quick start:
    python -m pip install -r requirements.txt
    python one_click_agency_gradio_app.py

Then open the local browser link, usually http://127.0.0.1:7860
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, Tuple

import gradio as gr

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # The app can still run if python-dotenv is not available.
    pass


DEFAULT_MODEL = "gemini-2.5-flash"


CUSTOM_CSS = """
/* Main page background */
.gradio-container {
    max-width: 1250px !important;
    margin: auto !important;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
    background: #eaf1f8 !important;
}

body, .app, .main {
    background: #eaf1f8 !important;
}

/* Header */
#app-header {
    background: linear-gradient(135deg, #f8fbff 0%, #e7f1ec 100%);
    border: 2px solid #264333;
    border-radius: 22px;
    padding: 28px 28px 24px 28px;
    text-align: center;
    margin: 18px 0 24px 0;
    box-shadow: 0 12px 28px rgba(20, 35, 50, 0.10);
}

#app-header h1 {
    color: #264333;
    font-size: 38px;
    line-height: 1.1;
    margin: 0 0 8px 0;
    font-weight: 800;
    letter-spacing: -0.5px;
}

#app-header p {
    color: #1c2d3f;
    font-size: 16px;
    margin: 0;
}

#app-header .tagline {
    display: inline-block;
    margin-top: 14px;
    padding: 8px 14px;
    border-radius: 999px;
    background: #264333;
    color: white;
    font-size: 13px;
    font-weight: 650;
}

/* Cards and panels */
.input-card, .output-card {
    background: #ffffff;
    border: 1px solid #d8e2ea;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 22px rgba(20, 35, 50, 0.08);
}

.section-title {
    color: #264333;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 6px;
}

.small-note {
    color: #4c5c68;
    font-size: 13px;
    margin-bottom: 14px;
}

/* Button */
button.primary, .gr-button-primary {
    background: #f28c28 !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 18px rgba(242, 140, 40, 0.25) !important;
}

button.primary:hover, .gr-button-primary:hover {
    background: #d97818 !important;
}

/* Inputs */
textarea, input, select {
    border-radius: 12px !important;
}

/* Output markdown */
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
    color: #264333 !important;
}

/* Footer */
#review-note {
    border-left: 6px solid #264333;
    background: #ffffff;
    border-radius: 14px;
    padding: 14px 18px;
    margin: 24px 0 8px 0;
    color: #1f2d3a;
    box-shadow: 0 6px 16px rgba(20, 35, 50, 0.06);
}
"""


def build_system_prompt(
    campaign_name: str,
    audience: str,
    program_details: str,
    date_location: str,
    tone: str,
    call_to_action: str,
    platform_focus: str,
) -> str:
    """Build the prompt that is sent to Gemini."""
    return f"""
You are the AI marketing assistant for Uncle Haq's Makerspace & STEAM Education Centre.
Create a ready-to-review marketing campaign package.

Brand voice:
- Warm, family-friendly, practical, and encouraging
- Sounds like a real local STEAM/makerspace program, not a big corporate advertisement
- Clear for parents and exciting for students
- Friendly and natural, with a little energy

Ethical and safety rules:
- Do not include private child information
- Do not invent exact prices, dates, addresses, claims, or outcomes unless the user provides them
- Keep the language inclusive and welcoming
- Make the output ready for human review before posting

Campaign details:
- Campaign name: {campaign_name}
- Target audience: {audience}
- Program details: {program_details}
- Date/location details: {date_location}
- Desired tone: {tone}
- Main call-to-action: {call_to_action}
- Main platform focus: {platform_focus}

Return ONLY valid JSON using exactly this structure:
{{
  "campaign_summary": "one short paragraph explaining the campaign purpose",
  "instagram_caption": "caption text",
  "facebook_post": "facebook post text",
  "email_subject": "email subject line",
  "email_body": "short email body",
  "flyer_copy": "short flyer copy",
  "hashtags": ["#example", "#example"],
  "image_prompt": "AI image generation prompt with no embedded text or watermark",
  "safety_checklist": ["check item", "check item", "check item"],
  "evaluation_scores": {{
    "brand_voice": 0,
    "clarity": 0,
    "accuracy": 0,
    "inclusiveness": 0,
    "image_prompt_fit": 0
  }},
  "human_review_notes": "short note explaining what a staff member should review before publishing"
}}

Use scores from 1 to 5. Make the content polished, natural, and easy for a small business owner to use.
""".strip()


def get_mock_campaign(campaign_name: str, audience: str, program_details: str) -> Dict[str, Any]:
    """Return demo content so the app can be used without a Gemini API key."""
    name = campaign_name.strip() or "Summer STEAM Camp"
    aud = audience.strip() or "parents of elementary and middle school students"
    details = program_details.strip() or "hands-on robotics, coding, circuits, and 3D printing activities"

    return {
        "campaign_summary": (
            f"This campaign promotes {name} as a friendly, hands-on learning experience for {aud}. "
            "The goal is to help families quickly understand the value of the program and feel excited to ask questions or register."
        ),
        "instagram_caption": (
            f"Ready for a fun learning experience? At Uncle Haq's Makerspace, students can explore {details} "
            "in a supportive, beginner-friendly environment. It is a great way for young makers to build confidence, "
            "try new tools, and turn ideas into real projects. Contact us to learn more and reserve a spot!"
        ),
        "facebook_post": (
            f"Uncle Haq's Makerspace is excited to share {name}, a hands-on STEAM program for curious students. "
            f"Students will explore {details} while practicing creativity, teamwork, and problem-solving. "
            "Families are welcome to reach out for registration details and any questions."
        ),
        "email_subject": f"Explore, Build, and Create at {name}",
        "email_body": (
            "Hello families,\n\n"
            f"We are excited to invite students to join {name} at Uncle Haq's Makerspace. "
            f"This program gives students the chance to explore {details} through fun, practical, beginner-friendly activities. "
            "Our goal is to make STEAM learning feel creative, welcoming, and hands-on.\n\n"
            "Please contact us for registration details or to ask any questions.\n\n"
            "Thank you,\nUncle Haq's Makerspace"
        ),
        "flyer_copy": (
            f"Join {name}! Students will explore hands-on STEAM activities including {details}. "
            "A creative and beginner-friendly program for young makers. Contact us to learn more and reserve a spot."
        ),
        "hashtags": ["#STEAMLearning", "#Makerspace", "#3DPrinting", "#CodingForKids", "#CreativeLearning"],
        "image_prompt": (
            "Create a realistic square social media background for a family-friendly STEAM program. "
            "Show an organized makerspace table with student-safe tools, a small robot, colorful circuit parts, "
            "a laptop with beginner code on screen, and a softly blurred 3D printer in the background. Use deep green #264333, "
            "teal, orange, light navy, and white accents. Bright natural light, clean composition, and open negative space for a headline. "
            "No embedded text, no watermark, no clutter."
        ),
        "safety_checklist": [
            "No private student or child information is included.",
            "Exact dates, prices, age ranges, and location should be confirmed before posting.",
            "The language is inclusive, family-friendly, and easy for parents to understand.",
            "The image prompt avoids showing identifiable children and avoids clutter.",
        ],
        "evaluation_scores": {
            "brand_voice": 5,
            "clarity": 5,
            "accuracy": 4,
            "inclusiveness": 5,
            "image_prompt_fit": 5,
        },
        "human_review_notes": (
            "Before publishing, a staff member should confirm the real schedule, price, age range, registration link, "
            "and any program-specific details."
        ),
    }


def extract_json(text: str) -> Dict[str, Any]:
    """Parse JSON from Gemini output, even if it returns a fenced code block."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        try:
            return json.loads(fenced.group(1).strip())
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("The AI response could not be parsed as JSON.")


def call_gemini(prompt: str, model_name: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Send the prompt to Gemini and return a JSON dictionary."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY was not found. Set your API key or keep Mock Demo Mode turned on.")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("google-genai is not installed. Run: python -m pip install -r requirements.txt") from exc

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model_name or DEFAULT_MODEL, contents=prompt)

    if not getattr(response, "text", None):
        raise RuntimeError("Gemini returned an empty response.")

    return extract_json(response.text)


def score_text(scores: Dict[str, Any]) -> str:
    if not scores:
        return "No scores returned."
    return "\n".join(f"- **{k.replace('_', ' ').title()}:** {v}/5" for k, v in scores.items())


def list_to_markdown(items: Any) -> str:
    if isinstance(items, list):
        return "\n".join(f"- {item}" for item in items)
    return str(items or "")


def hashtags_to_text(items: Any) -> str:
    if isinstance(items, list):
        return " ".join(items)
    return str(items or "")


def generate_campaign(
    campaign_name: str,
    audience: str,
    program_details: str,
    date_location: str,
    tone: str,
    call_to_action: str,
    platform_focus: str,
    model_name: str,
    mock_mode: bool,
) -> Tuple[str, str, str, str, str, str, str, str, str, str, str, str]:
    """Main function connected to the Generate button."""
    if not campaign_name.strip() or not program_details.strip():
        msg = "Please enter at least a campaign name and program details."
        return (msg, "", "", "", "", "", "", "", "", "", "{}", "Missing required input.")

    try:
        if mock_mode:
            data = get_mock_campaign(campaign_name, audience, program_details)
            status = "Demo output generated in Mock Demo Mode. No Gemini API call was made."
        else:
            prompt = build_system_prompt(
                campaign_name=campaign_name,
                audience=audience,
                program_details=program_details,
                date_location=date_location,
                tone=tone,
                call_to_action=call_to_action,
                platform_focus=platform_focus,
            )
            data = call_gemini(prompt, model_name=model_name or DEFAULT_MODEL)
            status = f"Campaign generated with {model_name or DEFAULT_MODEL}."

        data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = data.get("campaign_summary", "")
        instagram = data.get("instagram_caption", "")
        facebook = data.get("facebook_post", "")
        email = f"**Subject:** {data.get('email_subject', '')}\n\n{data.get('email_body', '')}"
        flyer = data.get("flyer_copy", "")
        hashtags = hashtags_to_text(data.get("hashtags", []))
        image_prompt = data.get("image_prompt", "")
        safety = list_to_markdown(data.get("safety_checklist", []))
        scores = score_text(data.get("evaluation_scores", {}))
        review = data.get("human_review_notes", "")
        raw_json = json.dumps(data, indent=2)

        return summary, instagram, facebook, email, flyer, hashtags, image_prompt, safety, scores, review, raw_json, status
    except Exception as exc:
        error = f"Something went wrong: {exc}"
        return (error, "", "", "", "", "", "", "", "", "", "{}", error)


def build_app() -> gr.Blocks:
    """Create the Gradio browser-based interface."""
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft(), title="The One-Click Agency") as demo:
        gr.HTML(
            """
            <div id="app-header">
                <h1>The One-Click Agency</h1>
                <p>AI Marketing Autopilot for Uncle Haq's Makerspace & STEAM Education Centre</p>
                
            </div>
            """
        )

        with gr.Row(equal_height=False):
            with gr.Column(scale=1, elem_classes=["input-card"]):
                gr.HTML("<div class='section-title'>Campaign Inputs</div><div class='small-note'>Fill this out like a simple marketing request form.</div>")

                campaign_name = gr.Textbox(
                    label="Campaign Name",
                    value="3D Printing Camp with Tinkercad",
                    placeholder="Example: 3D Printing Camp with Tinkercad",
                )
                audience = gr.Textbox(
                    label="Target Audience",
                    value="parents of children ages 8-13",
                    placeholder="Example: parents of children ages 8-13",
                )
                program_details = gr.Textbox(
                    label="Program Details",
                    lines=5,
                    value=(
                        "Students will learn the basics of 3D design using Tinkercad and create simple printable models. "
                        "They will explore shapes, resizing, grouping, and building objects step by step. By the end, students will design "
                        "a small custom project such as a keychain, name tag, mini character, or simple invention."
                    ),
                    placeholder="Describe the class, camp, activity, or event.",
                )
                date_location = gr.Textbox(
                    label="Date / Location Details",
                    value="Upcoming sessions at Uncle Haq's Makerspace",
                    placeholder="Example: July sessions at Uncle Haq's Makerspace",
                )
                tone = gr.Dropdown(
                    label="Tone",
                    choices=[
                        "Warm and family-friendly",
                        "Exciting and energetic",
                        "Professional but friendly",
                        "Simple and beginner-friendly",
                    ],
                    value="Warm and family-friendly",
                )
                platform_focus = gr.Dropdown(
                    label="Main Platform Focus",
                    choices=["Instagram + Facebook", "Email campaign", "Flyer and social media", "Full mini campaign"],
                    value="Full mini campaign",
                )
                call_to_action = gr.Textbox(
                    label="Call to Action",
                    value="Contact us for registration details and to reserve a spot.",
                    placeholder="Example: Register today / Contact us for details",
                )
                model_name = gr.Textbox(label="Gemini Model", value=DEFAULT_MODEL)
                mock_mode = gr.Checkbox(label="Mock Demo Mode - test without Gemini API key", value=True)
                generate_btn = gr.Button("Generate Campaign", variant="primary")

            with gr.Column(scale=2, elem_classes=["output-card"]):
                gr.HTML("<div class='section-title'>Generated Campaign Package</div><div class='small-note'>Review, edit, and approve before publishing.</div>")
                status = gr.Textbox(label="Status", interactive=False)

                with gr.Tabs():
                    with gr.Tab("Summary"):
                        summary_output = gr.Markdown()
                    with gr.Tab("Instagram"):
                        instagram_output = gr.Markdown()
                    with gr.Tab("Facebook"):
                        facebook_output = gr.Markdown()
                    with gr.Tab("Email"):
                        email_output = gr.Markdown()
                    with gr.Tab("Flyer"):
                        flyer_output = gr.Markdown()
                    with gr.Tab("Hashtags"):
                        hashtags_output = gr.Markdown()
                    with gr.Tab("Image Prompt"):
                        image_prompt_output = gr.Markdown()
                    with gr.Tab("Safety Check"):
                        safety_output = gr.Markdown()
                    with gr.Tab("Evaluation"):
                        scores_output = gr.Markdown()
                    with gr.Tab("Human Review"):
                        review_output = gr.Markdown()
                    with gr.Tab("Raw JSON"):
                        raw_json_output = gr.Code(language="json")

        generate_btn.click(
            fn=generate_campaign,
            inputs=[campaign_name, audience, program_details, date_location, tone, call_to_action, platform_focus, model_name, mock_mode],
            outputs=[
                summary_output,
                instagram_output,
                facebook_output,
                email_output,
                flyer_output,
                hashtags_output,
                image_prompt_output,
                safety_output,
                scores_output,
                review_output,
                raw_json_output,
                status,
            ],
        )

        gr.HTML(
            """
            <div id="review-note">
                <strong>Human review reminder:</strong> This toolkit creates draft marketing content. A staff member should confirm dates, prices,
                age ranges, location, registration links, and final wording before anything is posted publicly.
            </div>
            """
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch()
