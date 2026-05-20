THE ONE-CLICK AGENCY - WINDOWS RUNNING STEPS

This package includes:
1. one_click_agency_gradio_app.py  = the main Python website-style app
2. requirements.txt                = the Python packages to install
3. run_app_windows.bat             = optional double-click runner
4. .env.example                    = optional API key template

PART A - RUN WITHOUT GEMINI API KEY FIRST

1. Extract the ZIP file.
2. Open the extracted folder.
3. Click the folder address bar at the top.
4. Type cmd and press Enter.
5. In Command Prompt, run:

   python -m pip install -r requirements.txt

   If that does not work, try:

   py -m pip install -r requirements.txt

6. Run the app:

   python one_click_agency_gradio_app.py

   If that does not work, try:

   py one_click_agency_gradio_app.py

7. Copy the local link that appears. It usually looks like:

   http://127.0.0.1:7860

8. Paste the link into Chrome.
9. Keep Mock Demo Mode checked.
10. Change the inputs in the browser and click Generate Campaign.

PART B - RUN WITH GEMINI API KEY

Option 1: Set the key in Command Prompt temporarily

1. Stop the app by pressing CTRL + C in Command Prompt.
2. Type this command with your real Gemini key:

   set GEMINI_API_KEY=your_actual_gemini_api_key_here

3. Run the app again:

   python one_click_agency_gradio_app.py

4. Open the local link again.
5. Uncheck Mock Demo Mode.
6. Click Generate Campaign.

Option 2: Use a .env file

1. Open .env.example.
2. Replace your_actual_gemini_api_key_here with your real key.
3. Save the file as .env in the same folder.
4. Run:

   python one_click_agency_gradio_app.py

5. Uncheck Mock Demo Mode in the browser.
6. Click Generate Campaign.

TO STOP THE TOOL

Go back to Command Prompt and press:

CTRL + C

WHAT TO SHOW YOUR PROFESSOR

- The browser interface
- The campaign input form
- The Generate Campaign button
- The output tabs: Instagram, Facebook, Email, Flyer, Image Prompt, Safety Check, Evaluation, and Human Review
- Explain that Mock Demo Mode is for testing without an API key, and Gemini Mode uses the real AI API.
