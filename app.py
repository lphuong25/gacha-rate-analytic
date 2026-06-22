import streamlit as st
import pandas as pd
import plotly.express as px

# import functions from analytics
from analytics import(
    calc_probability,
    generate_probability_curve,
    monte_carlo
)

# set up page with streamlit
st.set_page_config(
    page_title="Gacha Analytic Dashboard",
    layout="wide"
)


# load excel file
df = pd.read_excel("gachagame.xlsx")

# set up sidebar
st.sidebar.header("Settings")

game = st.sidebar.selectbox(
    "Choose Game",
    df["Name"]
)

st.title(f"Will you get an SSR in {game}?")

# Slider 1: real money
budget = st.sidebar.slider(
    "Cash Budget ($)", 0, 1000, 100, step=5
)

# Slider 2: in game saved pulls
saved_pulls = st.sidebar.slider(
    "Current Saved Pulls In Game", 0, 500, 0, step=1
)

# select game
row = df[df["Name"] == game].iloc[0]

# calculate the total number of pulls
budget_pulls = int(budget // row['Cost_per_pull'])
total_pulls = budget_pulls + saved_pulls
# probability
probability = (calc_probability(row, total_pulls))

# create columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Pulls From Cash", budget_pulls)

with col2:
    st.metric("Total Pulls Combined", total_pulls, delta=f"+{saved_pulls} Saved")

with col3:
    st.metric("Chance of at least 1 SSR", f"{probability:.2f}%")

# create charts
# probability vs budget
max_chart_pulls = int(max(row["Hard_pity"] * 1.2, 150))
pulls_axis, probs = generate_probability_curve(row, max_pulls=max_chart_pulls)
# create dataframe
curve_df = pd.DataFrame({
    "Total Pulls": pulls_axis,
    "Probability (%)": probs
})
# plot
fig = px.line(
    curve_df,
    x="Total Pulls",
    y="Probability (%)",
    title="Probability of Obtaining an SSR"
)

# add verticle line for current budget
fig.add_vline(
    x=total_pulls,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Your Current Limit: {total_pulls} Pulls",
    annotation_position="top left"
)

st.plotly_chart(
    fig,
    use_container_width = True
)

# monte carlo simulation
stats = monte_carlo(row)
# metrics
st.subheader ("Monte Carlo Results")

col1, col2, col3 = st.columns(3)

col1.metric("Average Pulls",
            f"{stats['mean']:.1f}")
col2.metric("Median Pulls",
            f"{stats['median']:.0f}")
col3.metric("Standard Deviation",
            f"{stats['std']:.1f}")

# histogram
hist_df = pd.DataFrame({"Pulls": stats["results"]})
# calculate failure rate
failed_simulations = sum(1 for p in stats["results"] if p > total_pulls)
failure_percent = (failed_simulations / len(stats["results"])) * 100

if failure_percent > 0:
    st.error(f"With {total_pulls} pulls, the rate that you might walk empty hand is {failure_percent:.1f}%")
    
else:
    st.success("Your total pulls is statically high enough to guarantee a hit")

fig = px.histogram(
    hist_df,
    x="Pulls",
    nbins=40,
    title = "Distribution of Pulls Needed for First SSR"
)

fig.add_vline(
    x=total_pulls,
    line_dash="solid",
    line_color="red",
    annotation_text=f"Your Available Pulls ({total_pulls} Pulls)"
)
st.plotly_chart(
    fig,
    use_container_width = True
)

