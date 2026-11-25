# Lab 3: Chatbot page
# TODO: Rename this file to fit your page. Keep the number at the front.
#
# A chatbot built with Pydantic AI (see the Pydantic AI pages on Canvas).
# It should:
#   - use a Pydantic AI Agent with instructions that fit your project's theme (no tools yet)
#   - use Streamlit's chat elements: st.chat_message and st.chat_input
#   - remember the conversation (message_history, saved in st.session_state)
#   - use try/except so an error shows a message instead of crashing the page
#   - stay on theme, without using any API or external data
#
# Your Gemini API key goes in .streamlit/secrets.toml as GOOGLE_API_KEY.

import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from streamlit.errors import StreamlitSecretNotFoundError
import os

st.title("Movie Chatbot")
if "movie_chat" not in st.session_state:
    st.session_state.movie_chat = []
    st.session_state.movie_history = []
for message in st.session_state.movie_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
try:
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
except StreamlitSecretNotFoundError:
    api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.info("Set GOOGLE_API_KEY in your Streamlit secrets to turn on the chatbot.")
prompt = st.chat_input("Ask for a movie suggestion", disabled=not api_key)
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking of a movie…"):
                model = GoogleModel("gemini-2.5-flash", provider=GoogleProvider(api_key=api_key))
                agent = Agent(
                    model,
                    instructions=(
                        "You are a movie recommendation chatbot. Suggest up to three "
                        "movies based on the user's mood, preferred genre, or past favorites. "
                        "Briefly explain each suggestion and avoid spoilers. Stay on the topic "
                        "of movies. For questions about data, direct the user to the Movie Picker page."
                    ),
                )
                result = agent.run_sync(prompt, message_history=st.session_state.movie_history)
        except Exception:
            st.error("The chatbot couldn't reply. Try sending your message again in a moment.")
        else:
            st.session_state.movie_history = result.all_messages()
            st.session_state.movie_chat.extend([
                {"role": "user", "text": prompt},
                {"role": "assistant", "text": result.output},
            ])
            st.markdown(result.output)
