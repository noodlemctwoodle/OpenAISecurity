import openai
import streamlit as st
import pickle
import os

from streamlit_chat import message


# Set page configuration and add header
st.set_page_config(
    page_title="RodBot + Azure Open AI",
    initial_sidebar_state="expanded",
    page_icon="🤖",
    menu_items={
        'Get Help': 'https://github.com/rod-trent/OpenAISecurity/tree/main/Code/Web%20Chat%20Bot',
        'Report a bug': "https://github.com/rod-trent/OpenAISecurity/issues",
        'About': "### RodBot + Azure Open AI",
    },
)

# Set title of the bot
st.title('RodBot')

# Hide Streamlit footer
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Azure Open AI Configuration
openai.api_type = "azure"
openai.api_key = st.secrets['openai_secret']
openai.api_base = st.secrets['openai_base_url']
openai.api_version = st.secrets['openai_api_version']
openai.gpt_type = st.secrets['openai_gpt_model']

# Configure Model
def generated_responses(prompt):  
    model_engine = st.secrets['chatgpt_model_name']  
    response = openai.Completion.create(  
        engine=model_engine,  
        prompt=prompt, 
        temperature=0.5, 
        max_tokens=500,
        top_p=0.45,  
        frequency_penalty=0,
        presence_penalty=0,
        stop=None           
    )
    message = response.choices[0].text
    return message

conversations_file = "conversations.pkl"

def load_conversations():
    try:
        with open(conversations_file, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []
    except EOFError:
        return []


def save_conversations(conversations, current_conversation):
    updated = False
    for i, conversation in enumerate(conversations):
        if conversation == current_conversation:
            conversations[i] = current_conversation
            updated = True
            break
    if not updated:
        conversations.append(current_conversation)

    temp_conversations_file = "temp_" + conversations_file
    with open(temp_conversations_file, "wb") as f:
        pickle.dump(conversations, f)

    os.replace(temp_conversations_file, conversations_file)


def exit_handler():
    print("Exiting, saving data...")
    # Perform cleanup operations here, like saving data or closing open files.
    save_conversations(st.session_state.conversations, st.session_state.current_conversation)

if 'conversations' not in st.session_state:
    st.session_state['conversations'] = load_conversations()

if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ''

if 'selected_conversation' not in st.session_state:
    st.session_state['selected_conversation'] = None

if 'input_field_key' not in st.session_state:
    st.session_state['input_field_key'] = 0

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# Initialize new conversation
if 'current_conversation' not in st.session_state or st.session_state['current_conversation'] is None:
    st.session_state['current_conversation'] = {'user_inputs': [], 'generated_responses': []}

input_placeholder = st.empty()
user_input = input_placeholder.text_input(
    'Ask any question', key=f'input_text_{len(st.session_state["current_conversation"]["user_inputs"])}'
)
  
submit_button = st.button("Submit")

if user_input or submit_button:
    # Added lines to attempt to fix no output bug
    output = generated_responses(user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

    st.session_state.current_conversation['user_inputs'].append(user_input)
    st.session_state.current_conversation['generated_responses'].append(output)
    save_conversations(st.session_state.conversations, st.session_state.current_conversation)
    user_input = input_placeholder.text_input(
        'You:', value='', key=f'input_text_{len(st.session_state["current_conversation"]["user_inputs"])}'
    )  # Clear the input field

# Add a button to create a new conversation
if st.sidebar.button("New Conversation"):
    st.session_state['selected_conversation'] = None
    st.session_state['current_conversation'] = {'user_inputs': [], 'generated_responses': []}
    st.session_state['input_field_key'] += 1

# Sidebar
st.sidebar.header("Conversation History")

for i, conversation in enumerate(st.session_state.conversations):
    if st.sidebar.button(f"Conversation {i + 1}: {conversation['user_inputs'][0]}", key=f"sidebar_btn_{i}"):
        st.session_state['selected_conversation'] = i
        st.session_state['current_conversation'] = st.session_state.conversations[i]

if st.session_state['selected_conversation'] is not None:
    conversation_to_display = st.session_state.conversations[st.session_state['selected_conversation']]
else:
    conversation_to_display = st.session_state.current_conversation

if conversation_to_display['generated_responses']:
    for i in range(len(conversation_to_display['generated_responses']) - 1, -1, -1):
        message(conversation_to_display["generated_responses"][i], key=f"display_generated_{i}")
        message(conversation_to_display['user_inputs'][i], is_user=True, key=f"display_user_{i}")