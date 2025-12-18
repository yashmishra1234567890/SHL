import streamlit as st
import requests

st.title("🧠 SHL GenAI Assessment Recommendation")

query = st.text_area("Enter Job Description")

import pandas as pd
import plotly.express as px

if st.button("Recommend"):
    try:
        response = requests.post(
            "http://localhost:8080/recommend",
            json={"query": query}
        )
        response.raise_for_status()
        res = response.json()

        st.subheader("Recommended Assessments")
        
        # Collect data for visualization
        all_test_types = []

        for i, r in enumerate(res["recommended_assessments"], 1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Title with Link
                st.markdown(f"### {i}. [{r['name']}]({r['url']})")
                
                # Test Type
                test_types = r['test_type']
                if isinstance(test_types, list):
                    test_types_str = ", ".join(test_types)
                    all_test_types.extend(test_types)
                else:
                    test_types_str = str(test_types)
                    all_test_types.append(test_types_str)
                    
                st.markdown(f"**Test Type:** {test_types_str}")
                
                # Description / Relevance
                # Using description as relevance context for now
                st.markdown(f"**Description:** {r['description']}")

            with col2:
                st.markdown(f"**Remote Testing:** {r.get('remote_support', 'N/A')}")
                st.markdown(f"**Adaptive/IRT:** {r.get('adaptive_support', 'N/A')}")
                
                duration = r.get('duration', 0)
                duration_str = f"{duration} minutes" if duration else "N/A"
                st.markdown(f"**Duration:** {duration_str}")

            st.markdown("---")

        # Visualization Section
        st.subheader("Visualization of Test Types")
        if all_test_types:
            # Clean up whitespace
            all_test_types = [t.strip() for t in all_test_types if t.strip()]
            type_counts = pd.Series(all_test_types).value_counts().reset_index()
            type_counts.columns = ["Test Type", "Count"]
            
            fig = px.bar(type_counts, x="Test Type", y="Count", title="Distribution of Test Types Recommendations")
            st.plotly_chart(fig)

        st.subheader("AI Explanation")
        st.write(res["explanation"])
        
    except requests.exceptions.JSONDecodeError:
        st.error("Error: Invalid JSON response from server.")
        st.text(f"Status Code: {response.status_code}")
        st.text(f"Raw Response: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
#to run the app, use the command:
# streamlit run app/ui.py