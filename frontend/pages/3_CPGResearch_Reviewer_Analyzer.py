import pandas as pd
import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="CPG Robo Agent Product Review Analyzer", page_icon="📈")

st.markdown("# Product Review Analyzer Task")
st.write(
    """This demo illustrates the CPG Robo Assistant Product Reviews, which takes several product reviews , extract the core topics from the reviews , evaluates the sentiment and groups into common topic cluster"""
)

SERIES = {"Best Screen": "https://www.amazon.com/Neutrogena-Ultra-Dry-Touch-Sunscreen-Spectrum/product-reviews/B005IHT94S/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews", "Suncreen Market Research": "https://www.amazon.com/Pipette-Sunscreen-Spectrum-Non-nano-4-Fluid-Ounce/product-reviews/B085Z49QW6/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
          "Sunscreen Consumer Voice": "https://www.amazon.com/CeraVe-Mineral-Sunscreen-Titanium-Sensitive/product-reviews/B07KL7HPXV/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
          }



last_rows = np.random.randn(1, 1)

with st.form(key='eval', clear_on_submit=True):
    #     uploaded_file = st.file_uploader(
    #         "Upload file", type=["pdf"],
    #         help="Only PDF files are supported",
    #         )

    sub_section = st.multiselect('Select Documents for Research', SERIES.keys(), format_func=lambda y: SERIES[y],
                               help="Research Documents")


    submit_eval_button = st.form_submit_button(label='Derive Review Insights')

    if submit_eval_button and sub_section :
        review_progress_text = "Analyzing Reviews"
        review_crawl_bar = st.progress(0, text=review_progress_text)

        status_text = st.empty()
            # clear_submit()
        for i in range(1, 101):
                new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
                status_text.text("%i%% Complete" % i)
                review_crawl_bar.progress(i)
                last_rows = new_rows
                time.sleep(0.05)
        df = pd.read_csv('data/research/output.csv')
        dossier = st.dataframe(df, use_container_width=True)
        review_crawl_bar.empty()
    else:
        st.error("Please atleast choose one source to continue the research")







