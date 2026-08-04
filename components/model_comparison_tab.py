import streamlit as st
import pandas as pd
import plotly.express as px


def render_model_comparison_tab(model_history):
    """
    Renders Tab 4: Model Performance & Accuracy Matrix evaluation table and grouped bar charts.

    Parameters:
        model_history (dict): Dictionary mapping model names to evaluation metric dictionaries.
    """
    with st.container(border=True):
        st.markdown('<div class="intercom-title">Model Performance & Accuracy Matrix</div>', unsafe_allow_html=True)
        
        if model_history:
            comp_data = []
            for model_name, m_dict in model_history.items():
                comp_data.append({
                    "Model": model_name,
                    "RMSE": m_dict.get('RMSE', 0),
                    "MAE": m_dict.get('MAE', 0),
                    "MAPE (%)": m_dict.get('MAPE', 0)
                })
            
            comp_df = pd.DataFrame(comp_data)
            
            c_left, c_right = st.columns([1, 1.2])
            
            with c_left:
                st.subheader("Evaluation Scores")
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
                st.caption("Lower error scores indicate higher predictive accuracy.")
                
            with c_right:
                st.subheader("Comparative Error Metric Chart")
                fig_comp = px.bar(
                    comp_df,
                    x="Model",
                    y=["RMSE", "MAE", "MAPE (%)"],
                    barmode="group",
                    template="plotly_dark",
                    color_discrete_sequence=["#38bdf8", "#f97316", "#10b981"]
                )
                fig_comp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=20),
                    height=320
                )
                st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.info("No models trained yet in this session. Go to the 'Forecast Engine' tab and train a model to log history.")
