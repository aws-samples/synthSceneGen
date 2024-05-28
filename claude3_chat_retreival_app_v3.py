import streamlit as st #all streamlit commands will be available through the "st" alias
st.set_page_config(layout="wide") # Set the layout to "wide" mode

import claude3_rag_python_faiss_stream_v3 as glib #reference to local lib script
#import claude3_rag_python_faiss_load as glib2 #reference to local lib script
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import invoke_container as inv
import os
from PIL import Image
from math import ceil
import time
import imageio

#import pandas as pd
#from pathlib import Path
#context = Path('code.txt').read_text()
#inv.delete_prev_images() #Clear the older files and Images

#st.set_page_config(page_title="Chatbot") #HTML title
st.title("Chatbot to generate CARLA simulation code") #page title
# Move the chat interface to the sidebar
with st.sidebar:
    st.subheader("Generate Code")
    st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 600px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
    )
    if 'memory' not in st.session_state:
        st.session_state.memory = glib.get_memory()

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])

    input_container = st.container()
    with input_container:
        input_text = st.text_area("Chat with your bot here", placeholder="Type your message...", key="input_text", height=100)
        submit_button = st.button("Submit")

    if submit_button:
        user_input = input_text
        input_container.empty()  # Clear the input text field

        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

            st.session_state.chat_history.append({"role":"user", "text":input_text}) #append the user's latest message to the chat history
            response_container = st.container()
            st_callback = StreamlitCallbackHandler(response_container)
            chat_response = glib.get_rag_chat_response(input_text=input_text, memory=st.session_state.memory, streaming_callback=st_callback) #call the model through the supporting library
            st_callback._current_thought._container.update(
            label="",
            state="complete",
            expanded=True,
            )
            
            st.session_state.chat_history.append({"role":"assistant", "text":chat_response}) #append the bot's latest message to the chat history

        st.rerun()  # Rerun the app to reset the input text field

    
st.subheader("Validate Code") #subhead for this column
    #input_text = st.chat_input("Copy the generated code here") #display a chat input box
input_code = st.text_area("Input text", height=300, label_visibility="collapsed")
process_button = st.button("Run", type="primary") #display a primary button
if process_button:
        loading_placeholder = st.empty()
        loading_placeholder.markdown("Saving script to a file. . .")
        inv.save_code_to_file(input_code)
        loading_placeholder.markdown("Saved File. Now Validating Code against server. . .")
        #loading_placeholder.markdown("Validating Code against server. . .")
        #st.markdown("Validating. . .")
        output = inv.validate_code()
        #with st.expander("Show Validation Output"):
        #loading_placeholder.markdown(output,height=50)
        st.markdown(f"""<div style="height: 100px; overflow-y: scroll;">{output}</div>""", unsafe_allow_html=True)
        #st.markdown("Completed. Images will show up below")
    
st.subheader("Image Gallery")
image_dir = "/home/ubuntu/environment/carla-output/images"  # Replace with the path to your image directory
images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.jpg'))])
image_cache=[]
n_images = len(images)
if n_images == 0:
    st.warning("No Images. Run the Validation code to see images in the folder.")
else:
    # Create a list of image paths
    image_paths = [os.path.join(image_dir, image_file) for image_file in images]
    # Create a radio button to select between "Image Gallery" and "Image Animation"
    selection = st.radio("Select an option", ["Image Gallery", "Image Animation"],index=1)

    if selection == "Image Gallery":
        n_cols = 5  # Number of columns for the image grid
        n_rows = ceil(n_images / n_cols)  # Calculate the number of rows needed
        # Read the images and create an animation
        #images = [imageio.v2.imread(path) for path in image_paths]
        for i in range(n_rows):
            cols = st.columns(n_cols)
            for j in range(n_cols):
                idx = i * n_cols + j
                if idx < n_images:
                    image_path = os.path.join(image_dir, images[idx])
                    image = Image.open(image_path)
                    #image = image.resize((600, 480))  # Resize the image to 300x250 pixels
                    cols[j].image(image, caption=images[idx])
    else:
        animation_path = "/home/ubuntu/environment/carla-output/images/animation.gif"
        width, height = 800, 600

        if not os.path.isfile(animation_path):
            images_ani = [imageio.v2.imread(path) for path in image_paths]
            output_params = ["-vcodec", "libx264", "-pix_fmt", "yuv420p", "-s", f"{width}x{height}"]
            animation = imageio.v2.mimsave(animation_path, images_ani, fps=3, output_params=output_params)

        file = open(animation_path, "rb")
        contents = file.read()
        st.image(contents, caption="Image Animation", width=width)
        file.close()
