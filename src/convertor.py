import streamlit as st
import os
import openai
from datetime import datetime
from pathlib import Path
import os

# Retrieve API Key from Streamlit Secrets
openai_key = st.secrets["OPENAI_API_KEY"]

# Ensure API key is set
if not openai_key:
    raise Exception("API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize OpenAI Client
ai_client = openai.OpenAI(api_key=openai_key)

# UI setup
st.set_page_config(page_title="Cypress to Playwright Converter", layout="wide")

st.title(" Cypress to Playwright Test Converter using Gen AI")
# App Description
st.write(
   """
### 🔹 About This App
This app helps you **convert Cypress test scripts into Playwright scripts** using AI. 

### How It Works:
1️**Upload a Cypress test file (.js or .ts)**  
2️ **Click Convert** – AI will generate a Playwright version  
3️ **Preview the converted script**  
4️ **Download the Playwright test file**  

This makes it **easier to migrate from Cypress to Playwright** without manual effort. 
"""
)
# Add some spacing before showing the name
st.markdown("<br>", unsafe_allow_html=True)

# Display developer name in small font at the bottom
st.markdown(
    "<p style='font-size:18px; text-align:center; color:gray;'>Developed by Devesh Kumar</p>",
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader("Upload a Cypress test file (.js or .ts)", type=["js", "ts"])

def convert_to_playwright(cypress_code: str) -> str:
    prompt = f"""
You are a senior automation engineer. Your task is to convert Cypress tests to Playwright tests using '@playwright/test'.
Make sure:
- Use `import {{ test, expect }} from '@playwright/test';`
- Use `test('test name', async {{ page }}) => {{ ... }})` format
- Replace `cy.get(...)` with `page.locator(...)`
- Use `.fill()`, `.click()`, `.press()`, `.check()` etc. as needed
- Use `expect(page).toHaveURL(...)` instead of Cypress-style assertions
- Handle `cy.intercept`, `cy.wait`, and `cy.contains` if present

Convert the following Cypress code to Playwright:

{cypress_code}

Playwright Test:
"""
    response = ai_client.chat.completions.create(
        model="gpt-4",  # "gpt-4" gives the best result
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content


if uploaded_file:
    cypress_code = uploaded_file.read().decode("utf-8")
    st.subheader("Original Cypress Code")
    st.code(cypress_code, language="javascript")

    with st.spinner(" Converting with GPT..."):
        playwright_code = convert_to_playwright(cypress_code)

    st.subheader("Converted Playwright Code")
    st.code(playwright_code, language="typescript")

    # Save converted file
    os.makedirs("converted", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_filename = f"{uploaded_file.name.replace('.js', '').replace('.ts', '')}_playwright_{timestamp}.spec.ts"
    out_path = Path("converted") / out_filename

    with open(out_path, "w") as f:
        f.write(playwright_code)

    # Download button
    with open(out_path, "rb") as f:
        st.download_button(
            label="📥 Download Converted File",
            data=f,
            file_name=out_filename,
            mime="text/plain"
        )
