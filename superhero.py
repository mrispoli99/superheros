import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Set page config for a wider layout
st.set_page_config(page_title="Superhero Showdown", layout="wide")

st.title("🦸‍♂️ Mafoo's Superhero Showdown")
st.write("Select up to 5 superheroes to compare their stats!")

# --- Data Fetching ---
@st.cache_data
def load_superhero_data():
    url = "https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/all.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        heroes_dict = {f"{hero['name']} ({hero['biography']['publisher']})": hero for hero in data}
        return heroes_dict
    else:
        st.error("Failed to fetch superhero data.")
        return {}

heroes_data = load_superhero_data()

# --- User Interface ---
if heroes_data:
    hero_names = list(heroes_data.keys())
    
    selected_hero_names = st.multiselect(
        "Choose your fighters (Max 5):",
        options=hero_names,
        max_selections=5
    )
    
    if not selected_hero_names:
        st.warning("Please select at least one superhero to compare.")
    else:
        # --- Display Images ---
        st.subheader("The Contenders")
        cols = st.columns(len(selected_hero_names))
        
        selected_heroes_data = []
        for i, name in enumerate(selected_hero_names):
            hero = heroes_data[name]
            selected_heroes_data.append(hero)
            
            with cols[i]:
                st.image(hero['images']['sm'], use_container_width=True)
                st.markdown(f"**{hero['name']}**")
        
        st.divider()

        # --- Charting and Comparison ---
        st.subheader("Stat Comparison")
        
        # Defined Weights
        weight_int = 0.15
        weight_str = 0.20
        weight_spd = 0.10
        weight_dur = 0.10
        weight_pow = 0.40
        weight_com = 0.05

        chart_data_list = []
        rankings = []

        for hero in selected_heroes_data:
            stats = hero['powerstats']
            
            # Raw stat values (0-100)
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
            
            # Overall score is the sum of all weighted stat points
            weighted_score = w_intel + w_strength + w_speed + w_durability + w_power + w_combat
            
            rankings.append({"Name": hero['name'], "Weighted Score": weighted_score})
            
            # Since the user wants to see the percentage of the category max, 
            # we simply divide the raw stat by 100 (e.g., 67 strength = 67% of the possible strength points)
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
            text_auto=".1%"  # Displays numbers formatted as percentages with 1 decimal place
        )
        
        # Format the axes
        fig.update_layout(
            yaxis_title="Percentage of Category Max Achieved",
            yaxis_tickformat=".0%", # Format the y-axis ticks as whole percentages
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
