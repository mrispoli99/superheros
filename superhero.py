import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import json

# --- Page Config ---
st.set_page_config(page_title="Superhero Showdown AI", layout="wide")
st.title("🦸‍♂️ Mafoo's Superhero Showdown")
st.write("Type in any 5 characters separated by a comma (even fuzzy descriptions!) and AI will evaluate them based on comic lore.")

# --- API Configuration ---
# Streamlit automatically looks in its secrets manager for this key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Missing Gemini API Key. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

# --- Defined Weights ---
weight_int = 0.15
weight_str = 0.20
weight_spd = 0.10
weight_dur = 0.10
weight_pow = 0.40
weight_com = 0.05

# --- User Interface ---
user_query = st.text_input(
    "Enter your fighters:", 
    placeholder="e.g., Magneto, Omega-level Iceman, Batman, Professor X, and MCU Thanos"
)

if st.button("Evaluate Multiverse Matchup"):
    if not user_query:
        st.warning("Please enter some characters first.")
    else:
        with st.spinner("Consulting the AI Multiverse..."):
            
            # This prompt forces the AI to output exactly the data format our chart needs
            system_prompt = """
            You are an expert comic book historian. The user will provide a list of up to 5 characters or descriptions of characters.
            Identify the characters (using their most standard comic-book continuity versions unless the user specifies otherwise).
            Evaluate their lore and assign a score from 1 to 100 for these six attributes: intelligence, strength, speed, durability, power, and combat.
            Output the results STRICTLY as a JSON array of objects. 
            Format exactly like this:
            [
              {
                "name": "Character Name",
                "powerstats": {
                  "intelligence": 90,
                  "strength": 20,
                  "speed": 30,
                  "durability": 40,
                  "power": 100,
                  "combat": 60
                }
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
                
                # Parse the AI's JSON response
                selected_heroes_data = json.loads(response.text)
                
                st.divider()
                st.subheader("Stat Comparison")
                
                chart_data_list = []
                rankings = []

                for hero in selected_heroes_data:
                    stats = hero['powerstats']
                    
                    intel = int(stats.get('intelligence', 0))
                    strength = int(stats.get('strength', 0))
                    speed = int(stats.get('speed', 0))
                    durability = int(stats.get('durability', 0))
                    power = int(stats.get('power', 0))
                    combat = int(stats.get('combat', 0))
                    
                    # Calculate weighted points for the overall score
                    w_intel = intel * weight_int
                    w_strength = strength * weight_str
                    w_speed = speed * weight_spd
                    w_durability = durability * weight_dur
                    w_power = power * weight_pow
                    w_combat = combat * weight_com
                    
                    weighted_score = w_intel + w_strength + w_speed + w_durability + w_power + w_combat
                    rankings.append({"Name": hero['name'], "Weighted Score": weighted_score})
                    
                    # Append rows for the chart (Percent of Max)
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Intelligence", "Percent of Max": intel / 100})
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Strength", "Percent of Max": strength / 100})
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Speed", "Percent of Max": speed / 100})
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Durability", "Percent of Max": durability / 100})
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Power", "Percent of Max": power / 100})
                    chart_data_list.append({"Hero": hero['name'], "Stat Category": "Combat", "Percent of Max": combat / 100})

                df_chart = pd.DataFrame(chart_data_list)
                
                # Create Grouped Bar Chart
                fig = px.bar(
                    df_chart, 
                    x="Stat Category", 
                    y="Percent of Max", 
                    color="Hero", 
                    barmode="group",
                    text_auto=".1%"
                )
                
                fig.update_layout(
                    yaxis_title="Percentage of Category Max Achieved",
                    yaxis_tickformat=".0%",
                    xaxis_title="",
                    height=500
                )
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
                    
                with col2:
                    st.write("### Overall Ranking")
                    
                    df_ranks = pd.DataFrame(rankings)
                    df_ranks = df_ranks.sort_values(by="Weighted Score", ascending=False).reset_index(drop=True)
                    df_ranks.index += 1
                    
                    st.dataframe(
                        df_ranks, 
                        use_container_width=True,
                        column_config={
                            "Name": st.column_config.TextColumn("Hero Name"),
                            "Weighted Score": st.column_config.NumberColumn(
                                "Weighted Score",
                                format="%.1f"
                            )
                        }
                    )
            except Exception as e:
                st.error(f"An error occurred while consulting the AI: {e}")