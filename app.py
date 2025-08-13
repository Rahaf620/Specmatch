from dotenv import load_dotenv
import os
import time
import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

if not OPENROUTER_API_KEY:
    st.error("❌ Missing OpenRouter API key! Please set it in your .env file.")
    st.stop()

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="AI Competitor Feature Gap Finder",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# Custom CSS for sleek professional look
# -----------------------------
st.markdown("""
<style>
/* Full-page dark gradient background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to bottom right, #0f111a, #1f2030);
    color: #f1f1f1;
    font-family: 'Segoe UI', sans-serif;
}

/* Header */
h1 {
    text-align: center;
    color: #ffffff;
    font-size: 40px;
    font-weight: 700;
    margin-bottom: 5px;
}
h4 {
    text-align: center;
    color: #cccccc;
    font-size: 18px;
    margin-top: 0px;
    margin-bottom: 30px;
}

/* Card styling */
.card {
    background-color: #1c1c2b;
    color: #f1f1f1;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}

/* Highlight recommended model */
.recommended {
    background-color: #0d5f3f;
    color: #ffffff;
    padding: 10px;
    border-radius: 12px;
    font-weight: bold;
}

/* Remove empty bubbles under text areas */
[data-baseweb="textarea"] {
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

/* Streamlit buttons */
.stButton>button {
    background-color: #0d5f3f;
    color: white;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 12px;
}
.stButton>button:hover {
    background-color: #0f8f5c;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1>⚡ AI Competitor Feature Gap Finder</h1>", unsafe_allow_html=True)
st.markdown("<h4>Compare products in real-time and discover feature gaps</h4>", unsafe_allow_html=True)
st.write("---")

# -----------------------------
# Input Section (stacked)
# -----------------------------
st.subheader("📥 Product Descriptions")

st.markdown('<div class="card">', unsafe_allow_html=True)
product_a = st.text_area("🅰️ Product A Description", height=250)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
product_b = st.text_area("🅱️ Product B Description", height=250)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Model selection
# -----------------------------
st.subheader("⚙️ Select AI Models")
models_all = ["gpt-4o-mini", "gpt-3.5-turbo", "claude-instant"]
models_selected = st.multiselect(
    "Pick the AI models to run",
    options=models_all,
    default=models_all
)

# -----------------------------
# Analyze Button
# -----------------------------
if st.button("🔍 Analyze"):
    if not product_a.strip() or not product_b.strip():
        st.error("Please enter both product descriptions.")
    elif not models_selected:
        st.error("Select at least one AI model to analyze.")
    else:
        with st.spinner("Analyzing with OpenRouter AI..."):
            prompt = f"""
Compare the following two products and list:
1. Features Product A has that Product B does not.
2. Features Product B has that Product A does not.
3. Potential opportunities for improvement.
4. Provide a rating (1-10) for how complete this analysis might be.

Product A: {product_a}
Product B: {product_b}
"""
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            results = {}
            for model in models_selected:
                start_time = time.time()
                json_data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }

                try:
                    response = requests.post(url, headers=headers, json=json_data)
                    elapsed_time = time.time() - start_time

                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]

                        usage = result.get("usage", {})
                        total_tokens = usage.get("total_tokens", 0)
                        price_per_token = 0.00002  # adjust per OpenRouter pricing
                        cost_estimate = total_tokens * price_per_token

                        results[model] = {
                            "content": content,
                            "speed": elapsed_time,
                            "cost": cost_estimate
                        }
                    else:
                        results[model] = {
                            "content": f"API error: {response.status_code}",
                            "speed": elapsed_time,
                            "cost": 0
                        }

                except Exception as e:
                    results[model] = {
                        "content": f"Error: {str(e)}",
                        "speed": 0,
                        "cost": 0
                    }

            # Recommendation logic
            recommended_model = max(
                results, key=lambda m: len(results[m]["content"]) / max(results[m]["speed"], 0.01)
            )

            # -----------------------------
            # Display Results
            # -----------------------------
            st.subheader("📊 Model Comparisons")
            for model, info in results.items():
                with st.expander(f"{model} ✅ Speed: {info['speed']:.2f}s | Cost: ${info['cost']:.6f}", expanded=True):
                    if model == recommended_model:
                        st.markdown('<div class="recommended">Recommended Model ✅</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card">{info["content"]}</div>', unsafe_allow_html=True)

            st.success(f"✅ Recommended model: {recommended_model}")

            # -----------------------------
            # Download CSV Report
            # -----------------------------
            report_data = []
            for model, info in results.items():
                report_data.append({
                    "Model": model,
                    "Content": info["content"],
                    "Speed (s)": round(info["speed"], 2),
                    "Estimated Cost ($)": round(info["cost"], 6)
                })
            df_report = pd.DataFrame(report_data)
            csv_buffer = BytesIO()
            df_report.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            st.download_button(
                label="📥 Download Full Report as CSV",
                data=csv_buffer,
                file_name="competitor_feature_gap_report.csv",
                mime="text/csv"
            )
