import base64

import streamlit as st
import time
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="CPG Robo Agent Search", page_icon="☕")



col1, col2 = st.columns(2)

# Start of UI Components

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">'
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css",crossorigin="anonymous">',
    unsafe_allow_html=True)

st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js" integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

st.markdown("""

<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #253662;">
  <a class="navbar-brand" href="https://cloud.google.com/ai/generative-ai" target="_blank">Cymbal Product Research  Demo</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

</nav>

 <style>
    div.stButton > button:first-child {
        background-color: #769449
        color:#000000;
    }
    div.stButton > button:hover {
        background-color: #F5F5F5;
        color:#000000;
        }
    div.stDownloadButton > button:first-child {
        background-color: #88cc23;
        color:#000000;
    }
    div.stDownloadButton > button:hover {
        background-color: #F5F5F5;
        color:#000000;
        }


    </style>
""", unsafe_allow_html=True)

st.markdown('''
<style>
.stApp header {
    z-index: 0;
}
</style>
''', unsafe_allow_html=True)




with open("image.png", "rb") as image:
            encoded = base64.b64encode(image.read()).decode()



            res1_start = f""" 
                <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Title</title>
                <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js" integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+" crossorigin="anonymous"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css",crossorigin="anonymous">
            </head>
            <body>
            <section class="pt-5 pb-5">
                <div class="container">
                    <div class="row">
                        <div class="col-6">
                            <h4 class="mb-3">Hire Minions Your Personal Research Assistant</h4>
                        </div>
                        <div class="col-6 text-right">
                            <a class="btn btn-primary mb-3 mr-1" href="#carouselExampleIndicators2" role="button" data-slide="prev">
                                <i class="fa fa-arrow-left"></i>
                            </a>
                            <a class="btn btn-primary mb-3 " href="#carouselExampleIndicators2" role="button" data-slide="next">
                                <i class="fa fa-arrow-right"></i>
                            </a>
                        </div>
                        <div class="col-12">
                            <div id="carouselExampleIndicators2" class="carousel slide" data-ride="carousel" data-interval="false">

                                <div class="carousel-inner">

                """
            res1_end = """
               </div>
                        </div>
                    </div>
                </div>
                </div>
            </section>
            </body>
            </html>
                """

            res1 = f"""

                                 <div class="carousel-item active">
                                        <div class="row">

                                            <div class="col-md-8 mb-4">

                                                <div class="card">
                                                    <a href="http://localhost:8501/RoboAgent_Configurator"><img class="img-fluid" width="100%" height="180" alt="100%x280" src="data:image/jpeg;base64,{encoded}"></a>
                                                    <div class="card-body">
                                                        <h5 class="card-title">CPG Product Researcher</h5>
                                                        <p class="card-text">Minion Researcher 1</p>
                                                       <h5 class="card-title">About Me</h5>
                                                        <p class="card-text">I am an experienced market research professional with over 7 years of experience in various industries,
including fintech, consumer packaged goods, healthcare/nutrition, pharmaceuticals, food & beverage,
agriculture, education, apparel, personal care products, AI, and more.</p>
                                                        <br>
                                                        <h4 class="card-title">Hourly Rate</h4>
                                                         <p class="card-text"> xx $ </p>
                                                         <br>
                                                        <h4 class="card-title">Skills</h4>
                                                        <button type="button" class="btn btn-primary">

                                                        Research documents

                                                        </button> &nbsp;
                                                        <button type="button" class="btn btn-danger">

                                                        Market analysis

                                                        </button>
                                                        <br>

                                                    </div>

                                                </div>
                                            </div>
                                        </div>
                                </div>
<div class="carousel-item">
                                        <div class="row">

                                            <div class="col-md-8 mb-4">

                                                <div class="card">
                                                    <img class="img-fluid" width="80%" alt="100%x280" src="data:image/jpeg;base64,{encoded}">
                                                    <div class="card-body">
                                                        <h5 class="card-title">CPG Product Researcher</h5>
                                                        <p class="card-text">Minion Researcher 2</p>
                                                       <h5 class="card-title">About Me</h5>
                                                        <p class="card-text">An online marketer since 2008, I've been in all kinds of shoes and went the full journey from an employee to a freelancer, consultant, and now an agency owner. I focus the most on content strategy, SEO, and content production, - and I've helped grow hundreds of websites with these services. When I'm not growing websites I am either hiking or spending time with my kids</p>
                                                        <br>
                                                        
                                                        <h4 class="card-title">Hourly Rate</h4>
                                                         <p class="card-text"> xx $ </p>
                                                         <br>
                                                        <h4 class="card-title">Skills</h4>
                                                        <button type="button" class="btn btn-primary">

                                                        Consumer Insights

                                                        </button> &nbsp;
                                                        <button type="button" class="btn btn-danger">

                                                        Market Strategy

                                                        </button>
                                                        <br>

                                                    </div>

                                                </div>
                                            </div>
                                        </div>
                                </div>


                                """

            res1 = res1_start + res1 + res1_end
            components.html(res1, height=1200, )

            # st.markdown(
            #     """
            #     Welcome to Cymbal Product Research & Innovation Assistant app , powered by Google LLM.
            #     **👈 Select a tasks from the sidebar** to see some demonstration
            #     of what Google LLM can do!
            #
            # """
            # )

            footer = """  <footer>
                                        <div class="text-center p-4" style="background-color: rgba(0, 0, 0, 0.05);">
                                © 2023 Copyright:
    <a class="text-reset fw-bold" href="https://moma.corp.google.com/person/asanthan">Developed by Arun Santhanagopalan</a>
  </div>
                                        </footer>
                                        """
            components.html(footer)



