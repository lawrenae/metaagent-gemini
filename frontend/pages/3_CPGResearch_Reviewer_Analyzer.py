import pandas as pd
import streamlit as st
import numpy as np
from amazon_reviews_scrapper import get_reviews_for
import vertexai
import vertexai.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part

st.set_page_config(page_title="CPG Robo Agent Product Review Analyzer", page_icon="📈")

st.markdown("# Product Review Analyzer Task")
st.write(
    """This demo illustrates the CPG Robo Assistant Product Reviews, which takes several product reviews , extract the core topics from the reviews , evaluates the sentiment and groups into common topic cluster"""
)

SERIES = [
    "https://www.amazon.com/Dawn-Ultra-Dishwashing-Liquid-Original/product-reviews/B0BBPNPZTC/",
    "https://www.amazon.com/Dawn-Platinum-Dishwashing-Liquid-Refreshing/product-reviews/B0BBQ8S9VK/"
]

num_pages=4

last_rows = np.random.randn(1, 1)

_, row1_1, _ = st.columns((1,36,1))
    #     uploaded_file = st.file_uploader(
    #         "Upload file", type=["pdf"],
    #         help="Only PDF files are supported",
    #         )

with row1_1:
    sub_section = st.multiselect('Select Documents for Research', SERIES, 
                               help="Research Documents")


    submit_eval_button = st.button(label='Derive Review Insights')

    if submit_eval_button and sub_section :
        review_progress_text = "Analyzing Reviews"
        review_crawl_bar = st.progress(0, text=review_progress_text)


        status_text = st.empty()
        results = []

        total_count = len(SERIES) * num_pages +1
        index = 1

        for url in SERIES:
            page = 1
            while page <= num_pages:
                full_url = url
                if page > 1:
                    full_url = url + f"?pageNumber={page}"
                reviews = get_reviews_for(full_url)
                results.extend(reviews)

                status_text.text(f"{(round(index/total_count, 2))*100}% Complete")
                review_crawl_bar.progress(round(index/total_count,2))
                page+=1
                index+=1

        df = pd.DataFrame.from_records(results)

        dossier = st.dataframe(df)

        prompt = f"""
            You are a brand manager tasked with reading product reviews and looking for themes and trends. You have some specific tasks that you need to build as a report
            Make CERTAIN you respond ONLY with valid markdown.

            Tasks:

            Sentiment Identification:
            Identify the overall sentiment of the included data, and give a detailed explaination of different entries of the reviews and how it influences your understanding of how it is positive, negative or neutral.
            Sentiment score: give a final judgement of positive, neutral or negative.

            Themes:
            List the top ten most common themes found in the reviews

            Improvements:
            List out any suggestions for improvement made in the reviews.


            Precision is Paramount: Ensure that timestamps are as accurate as possible.
            Clarity: Organize your tables in a clear, easy-to-read format

            review data: {results}
        """

        # call vertex
        vertexai.init(project="genai-387615", location="us-central1")
        model = GenerativeModel("gemini-1.5-pro")
        analysis = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.9,
                "top_p": 1
            },
            safety_settings={
                  generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
                  generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                  generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                  generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            },
            stream=False,
        )
        print(analysis.text)
        st.markdown(analysis.text, unsafe_allow_html=True)
        review_crawl_bar.empty()

    else:
        st.error("Please atleast choose one source to continue the research")







