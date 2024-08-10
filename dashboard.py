from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pytz

from receipts_xyz.v2.onchainsummer import get_onchainsummer_workouts


# @st.cache_data
# def load_data():
#     df = pd.read_csv('notebooks/onchainsummer.csv')
#     if "Unnamed: 0" in df.columns:
#         df = df.drop(columns=["Unnamed: 0"])
#     df = df.iloc[::-1].reset_index(drop=True)  # Reverse the order to have earliest date first
#     df['datetime'] = pd.date_range(end='2024-08-12 23:59:59', periods=len(df), freq='10T', tz='US/Eastern')
#     df['hour'] = df['datetime'].dt.floor('H')
    
#     # Convert intensity time from seconds to minutes
#     df['total_intensity_time'] = df['total_intensity_time'] / 60
    
#     df = df.rename(columns={'total_participants': '# participants'})
    
#     return df


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    workouts = get_onchainsummer_workouts()
    df = pd.DataFrame([_w.to_json() for _w in workouts])
    
    use_col = [
        "time",
        "total_participants", "total_moving_time", "total_run_distance", 
        "total_bike_distance", "total_strength_time", "total_intensity_time"
    ]
    df = df[use_col]
    
    df["datetime"] = df["time"].map(lambda x: datetime.fromtimestamp(x, pytz.timezone("US/Eastern")))
    df['hour'] = df['datetime'].dt.floor('H')
    
    # Convert intensity time from seconds to minutes
    df['total_intensity_time'] = df['total_intensity_time'] / 60
    
    df = df.rename(columns={'total_participants': '# participants'})
    
    return df

# Visualization components
def create_progress_gauge(current_intensity, target_intensity):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_intensity,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Intensity Minutes", 'font': {'size': 24}},
        delta={'reference': target_intensity, 'increasing': {'color': "RebeccaPurple"}},
        gauge={
            'axis': {'range': [None, target_intensity], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [{'range': [0, target_intensity], 'color': 'cyan'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target_intensity
            }
        }
    ))
    return fig


def create_time_series_plot(df, metric):
    y_label = metric.replace('_', ' ').title()
    if 'time' in metric:
        y_label += ' (mins)'
    elif 'distance' in metric:
        y_label += ' (km)'
    
    fig = px.line(df, x='hour', y=metric, title=f'{y_label} Over Time')
    fig.update_layout(yaxis_title=y_label)
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def create_time_comparison_plot(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['hour'], y=df['total_moving_time'] // 60, name='Moving Time'))
    fig.add_trace(go.Scatter(x=df['hour'], y=df['total_strength_time'] // 60, name='Strength Time'))
    
    fig.update_layout(
        title='Moving Time vs Strength Time Over Time',
        xaxis_title='Date',
        yaxis_title='Time (mins)',
        legend_title='Exercise Type'
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig


def calculate_time_left(end_date):
    et_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(et_tz)
    
    # If current time is past August 12th of the current year, set end date to next year
    if current_time > end_date:
        end_date = end_date.replace(year=end_date.year + 1)
    
    time_left = end_date - current_time

    if time_left.total_seconds() > 0:
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"Time left: {days} days, {hours} hours, {minutes} minutes"
    else:
        return "The challenge has ended."
    

def main():
    st.title('Onchain Summer Challenge Dashboard')
    
    df = load_data()
    st.write(f"Last updated: {datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')} ET")

    # Section 1: Main Objective Plot
    st.header('Progress Towards 50,000 Intensity Minutes')
    current_intensity = df['total_intensity_time'].iloc[-1]
    target_intensity = 50000
    fig_progress = create_progress_gauge(current_intensity, target_intensity)
    st.plotly_chart(fig_progress, use_container_width=True)

    # Calculate and display time left
    et_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(et_tz)
    end_date = datetime(current_time.year, 8, 12, 23, 59, 59, tzinfo=et_tz)
    
    time_left_message = calculate_time_left(end_date)
    st.write(time_left_message)

    # Section 2: Data over time
    st.header('Data Over Time')
    df_hourly = df.groupby('hour').last().reset_index()
    
    # Plot total participants over time
    fig_participants = create_time_series_plot(df_hourly, '# participants')
    st.plotly_chart(fig_participants, use_container_width=True)
    
    # Plot moving time vs strength time
    fig_time_comparison = create_time_comparison_plot(df_hourly)
    st.plotly_chart(fig_time_comparison, use_container_width=True)
    
    # Plot total intensity time over time
    fig_intensity = create_time_series_plot(df_hourly, 'total_intensity_time')
    st.plotly_chart(fig_intensity, use_container_width=True)
    
    # Plot run and bike distances over time
    fig_run = create_time_series_plot(df_hourly, 'total_run_distance')
    st.plotly_chart(fig_run, use_container_width=True)
    
    fig_bike = create_time_series_plot(df_hourly, 'total_bike_distance')
    st.plotly_chart(fig_bike, use_container_width=True)

    # Section 3: Exercise Type Distribution
    st.header('Exercise Type Distribution')
    last_row = df.iloc[-1]
    moving_time = last_row['total_moving_time']
    strength_time = last_row['total_strength_time']

    exercise_data = pd.DataFrame({
        'Exercise Type': ['Moving (Running/Cycling)', 'Strength'],
        'Time (minutes)': [moving_time, strength_time]
    })

    fig_pie = px.pie(exercise_data, values='Time (minutes)', names='Exercise Type', title='Distribution of Exercise Types')
    st.plotly_chart(fig_pie, use_container_width=True)

if __name__ == "__main__":
    main()
