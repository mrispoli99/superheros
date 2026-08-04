import streamlit as st
import google.generativeai as genai
import json

# --- Page Config ---
st.set_page_config(page_title="Mafoo's Superhero Showdown", layout="centered")

st.title("🏆 Mafoo's Superhero Showdown: Ranked Edition")
st.write("Type in any 5 characters. The tool will rank them from most to least powerful and explain why!")

# --- API Configuration ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Missing Gemini API Key. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

# --- User Interface ---
user_query = st.text_input(
    "Enter your fighters:", 
    placeholder="e.g., Magneto, Omega-level Iceman, Batman, Professor X, and MCU Thanos"
)

if st.button("Rank the Multiverse"):
    if not user_query:
        st.warning("Please enter some characters first.")
    else:
        with st.spinner("Consulting the AI Multiverse..."):
            
            # The new prompt asks for a ranked list and a lore blurb instead of raw stats
            system_prompt = """
            You are an expert comic book historian. The user will provide a list of up to 5 characters.
            Evaluate their lore (using standard comic-book continuity unless specified otherwise) and rank them from 1 (most powerful/likely to win) to the lowest.
            Output the results STRICTLY as a JSON array of objects, sorted from Rank 1 to lowest. Place more emphasis on cosmic type abilities like strong telepathy and control
            of elements. 
            Format exactly like this:
            [
              {
                "rank": 1,
                "name": "Character Name",
                "blurb": "A concise 4-sentence explanation of why they earned this rank based on their powers and lore."
              }
            ]
            """
            
            try:
                # Initialize Gemini 3.6 Flash with JSON mode enforced
                model = genai.GenerativeModel(
                    "gemini-3.6-flash",
                    system_instruction=system_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                response = model.generate_content(user_query)
                ranked_heroes = json.loads(response.text)
                
                st.divider()
                st.subheader("The Official Rankings")
                
                # Loop through the JSON and display each hero in a clean format
                for hero in ranked_heroes:
                    with st.container():
                        st.markdown(f"### #{hero['rank']}: {hero['name']}")
                        st.write(hero['blurb'])
                        st.divider()
                        
            except Exception as e:
                st.error(f"An error occurred while consulting the AI: {e}")
