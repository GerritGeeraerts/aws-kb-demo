import streamlit as st
from streamlit import session_state

from utils import Chat, decrypt_with_private_key


def submit_button_state_toggle():
    st.session_state.submit_button_state_disabled = not st.session_state.submit_button_state_disabled

if 'chat_client' not in st.session_state:
    st.session_state.chat_client = Chat()

if 'submit_button_state_disabled' not in st.session_state:
    st.session_state.submit_button_state_disabled = False

if 'question' not in st.session_state:
    st.session_state.question = ""

if 'result' not in st.session_state:
    st.session_state.result = {}

if "encoded_kb_id" not in st.session_state:
    st.session_state.encoded_kb_id = None

st.title("Chat with your data 🤖")

st.session_state.encoded_kb_id = st.query_params.get('kb-id')
if not st.session_state.encoded_kb_id:
    st.write("Invalid url, contact sumsum")
    st.stop()

st.session_state.kb_id = decrypt_with_private_key(st.session_state.encoded_kb_id)
if not st.session_state.kb_id:
    st.write("Invalid url, contact sumsum")
    st.stop()

print(st.session_state.kb_id)

st.write("## Question:")
text_area = st.text_area("Enter Question here:", height=200, help="This question will be answered with your data", value=st.session_state.question)
submit = st.button("Submit", disabled=st.session_state.submit_button_state_disabled)


# form got submitted
if st.session_state.question and not st.session_state.result:
    with st.spinner('Processing...'):
        st.session_state.result = st.session_state.chat_client.inference(st.session_state.kb_id, st.session_state.question)
        st.session_state.submit_button_state_disabled = False
    st.rerun()

if st.session_state.question and st.session_state.result:
    st.write("## Answer:")
    answer = st.session_state.result.get('output', '')
    citations = st.session_state.result.get('citations', [])
    st.markdown(answer)
    st.write("### Citations:")
    for citation in citations:
        expander = st.expander(citation.get('url', ''))
        expander.write(citation.get('citation', ''))

if submit:
    st.session_state.question = text_area
    st.session_state.result = {}
    st.session_state.submit_button_state_disabled = True
    st.rerun()