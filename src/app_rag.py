from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from milvus.milvus_database import MilvusDatabase
import streamlit as st
import os
import pydeck as pdk
import pandas as pd
import time
from document_processors import load_multimodal_data, load_data_from_directory

import ollama
from llama_index.core import Document

from utils import set_environment_variables

MILVUS_SERVER = "192.168.0.5"


def init_st_state_session():
    if "latitude" not in st.session_state:
        st.session_state.latitude = 48.8566
    if "longitude" not in st.session_state:
        st.session_state.longitude = 2.3522
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "form_visible" not in st.session_state:
        st.session_state.form_visible = False
    if "first_prompting" not in st.session_state:
        st.session_state.first_prompting = True
    if "history" not in st.session_state:
        st.session_state["history"] = []


def initialize_settings():
    Settings.embed_model = NVIDIAEmbedding(
        model="nvidia/nv-embedqa-e5-v5", truncate="END"
    )
    # Settings.llm = NVIDIA(model="mistralai/mistral-7b-instruct-v0.2")
    Settings.llm = NVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1")

    Settings.text_splitter = SentenceSplitter(chunk_size=600)


prompt = """
        You are an agent specialized in document analysis. You will receive documents that you will need to analyze and catalog 
        in order to answer my questions. My goal is to find an event among all the scientific data you have in your context. 
        You must be precise and professional in your responses.The objective is to find correlations between the lithosphere, 
        the atmosphere, and the ionosphere." 
        """

prompt_command = """ 
        In the future, if user request a "position on map" (is at the left on the screen)  respond with the following format:
        { "action": "position_on_map", "latitude": <latitude>, "longitude": <longitude>, "zoom": <zoom> }

        - If zoom is not provided, default to 10.
        - Ignore any additional information like "north", "west", etc., and focus on latitude and longitude only.

        Examples:
        - User: "Point to map, long = 43 and lat = 4"
        Response: { "action": "position_on_map", "latitude": 4, "longitude": 43, "zoom": 10 }

        - User: "Position at lat 51.5074, long -0.1278, zoom 12"
        Response: { "action": "position_on_map", "latitude": 51.5074, "longitude": -0.1278, "zoom": 12 }

        This format helps the chatbot understand commands and reply with the correct map positioning data.
        Don't anwser the position now.
        """

prompt_command = """ 
         For this, in your data, you have a list of earthwake description like and radio link disturbances with STEC (Slant Total Electron Content) values.
        """


def instruction_prompting(query_engine):
    if st.session_state.first_prompting:
        prompting_container = st.container()
        with prompting_container:
            st.session_state.first_prompting = False
            # list_prompting = [prompt, prompt_command ]
            list_prompting = [prompt, prompt_command]
            for prompt_item in list_prompting:
                with st.chat_message("user"):
                    st.markdown(prompt_item)
                st.session_state["history"].append(
                    {"role": "user", "content": prompt_item}
                )

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    response_prompt = query_engine.query(prompt_item)
                    for token in response_prompt.response_gen:
                        full_response += token
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    st.markdown(response_prompt)
                    prompting_container = st.empty()

                st.session_state["history"].append(
                    {"role": "assistant", "content": response_prompt}
                )
    else:
        prompting_container = st.empty()


def chat_bot_engine(user_input, query_engine, st_history):
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response = query_engine.query(user_input)

            for token in response.response_gen:
                full_response += token
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st_history.append({"role": "assistant", "content": full_response})


def display_form():
    form_placeholder = st.empty()
    with form_placeholder.form(key="GPS"):
        # st.subheader("Set Coordinates")

        # Display input fields for coordinates
        latitude_input = st.text_input(
            "Set Latitude", value=str(st.session_state.latitude)
        )
        longitude_input = st.text_input(
            "Set Longitude", value=str(st.session_state.longitude)
        )

        # Form submission button
        submit_button = st.form_submit_button(label="Enter")

        # When submitting the form
        if submit_button:
            st.session_state.form_submitted = True
            st.session_state.form_visible = False

            try:
                # Update the coordinates in the session_state
                st.session_state.latitude = float(latitude_input)
                st.session_state.longitude = float(longitude_input)
                st.success("Coordinates updated successfully!")
                st.write("Form has been submitted, coordinates updated.")
                form_placeholder.empty()
            except ValueError:
                st.warning("Invalid latitude or longitude.")


# Show map on app
def show_map(latitude, longitude):
    color = [255, 0, 0, 80]  # Rouge translucide
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame({"lat": [latitude], "lon": [longitude]}),
        get_position="[lon, lat]",
        get_color=color,
        get_radius=100000,
    )
    view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=4)
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-v9",
    )


# Upload documents for RAG
def upload_item(db_milvus):
    upload_placeholder = st.container()
    with upload_placeholder:
        st.subheader("Upload a File")
        uploaded_files = st.file_uploader(
            "Drag and drop files here", accept_multiple_files=True
        )

        if uploaded_files and st.button("Process Files"):
            with st.spinner("Processing files..."):
                documents = load_multimodal_data(uploaded_files)
                st.session_state["index"] = db_milvus.create_index_document(documents)
                success_message = st.success("Directory processed and index created!")
                # time.sleep(2)
                upload_placeholder = st.empty()


# Main function to run the Streamlit app
def main():
    set_environment_variables()
    initialize_settings()
    init_st_state_session()

    db_milvus = MilvusDatabase(MILVUS_SERVER)

    # Page config
    st.set_page_config(page_title="Ionosphere seismics RAG", layout="wide")

    # Init database
    db_milvus = MilvusDatabase(MILVUS_SERVER)

    # Title
    st.title("Iono seismics AI")
    upload_item(db_milvus)

    col1, col2 = st.columns([1, 2])

    with col1:
        if "index" in st.session_state:
            st.header("Map")
            carte_placeholder = st.container()
            with st.container():

                if st.button("Open Form"):
                    # Display Form
                    st.session_state.form_visible = True

                # If visible show form
                if st.session_state.form_visible:
                    display_form()

                if not st.session_state.form_visible:
                    st.session_state.formholder = st.empty()

                # Update map
                carte_placeholder.pydeck_chart(
                    show_map(st.session_state.latitude, st.session_state.longitude)
                )

    with col2:
        if "index" in st.session_state:
            st.title("Ionospheric and seismic events ")
            if "history" not in st.session_state:
                st.session_state["history"] = []

            # Display chat messages
            user_input = st.chat_input("Enter your query:")

            chat_container = st.container()
            with chat_container:
                for message in st.session_state["history"]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            query_engine = st.session_state["index"].as_query_engine(
                similarity_top_k=20, streaming=True
            )

            # LLM request
            #instruction_prompting(query_engine)   
            chat_bot_engine(user_input, query_engine,st.session_state["history"])

            # Add a clear button
            if st.button("Clear Chat"):
                st.session_state["history"] = []
                st.rerun()

    st.markdown("---")  # Ligne horizontale pour séparer le contenu du footer
    st.write("© 2024 Iono seismics IA. Tous droits réservés.")


if __name__ == "__main__":
    main()
