import os
import streamlit as st
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Make sure you set this env var

st.title("AI Competitor Feature Gap Finder - OpenRouter.ai")

product_a = st.text_area("Product A Description")
product_b = st.text_area("Product B Description")

if st.button("Submit"):
    if not product_a or not product_b:
        st.error("Please enter both product descriptions.")
    else:
        with st.spinner("Analyzing with OpenRouter AI..."):
            prompt = f"""
            Compare the following two products and list:
            1. Features Product A has that Product B does not.
            2. Features Product B has that Product A does not.
            3. Potential opportunities for improvement.
            
            Product A: {product_a}
            Product B: {product_b}
            """

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            json_data = {
                "model": "gpt-4o-mini",  # or the model your OpenRouter account supports
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(url, headers=headers, json=json_data)

            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                st.subheader("Gap Analysis")
                st.write(result)
            else:
                st.error(f"API request failed with status {response.status_code}: {response.text}")
