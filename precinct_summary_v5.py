import streamlit as st
import pandas as pd
import numpy as np
import base64

@st.cache
def load_data():
    df = pd.read_csv('https://deltonastrong-assets.s3.amazonaws.com/nw_dems_data_1.txt', delimiter=',', low_memory=False)
    return df

def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() 
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'

def summarize_voting_data(df, selected_elections, selected_precincts, selected_voter_status):
    race_mapping = {
        1: "Other",
        2: "Other",
        6: "Other",
        9: "Other",
        3: "African American",
        4: "Hispanic",
        5: "White"
    }
    df['Race'] = df['Race'].replace(race_mapping)
    df['Sex'] = df['Sex'].replace({"M": "Male", "F": "Female", "U": "Unreported"})

    df['Birth_Date'] = pd.to_datetime(df['Birth_Date'])
    df['Age'] = (pd.to_datetime('today') - df['Birth_Date']).dt.days // 365

    age_ranges = [17, 26, 35, 55, np.inf]
    age_labels = ['18-25', '26-34', '35-54', '55+']

    df['Age Range'] = pd.cut(df['Age'], bins=age_ranges, labels=age_labels)

    if selected_precincts:
        df = df[df['Precinct'].isin(selected_precincts)]
    
    if selected_voter_status:
        df = df[df['Voter Status'].isin(selected_voter_status)]

    summary_age = df.groupby(['Race', 'Sex', 'Age Range']).size().unstack(fill_value=0)
    summary_age.index = summary_age.index.map(lambda x: f'{x[0]}, {x[1]}')

    df_voting_history = df[selected_elections].applymap(lambda x: 1 if x in ['Y', 'Z', 'A', 'E', 'F'] else 0)
    df['Voting History'] = df_voting_history.sum(axis=1)

    summary_voting_history = df.groupby(['Race', 'Sex', 'Voting History']).size().unstack(fill_value=0)
    summary_voting_history.index = summary_voting_history.index.map(lambda x: f'{x[0]}, {x[1]}')

    # Get the number of selected elections
    num_elections = len(selected_elections)

    # Rename the column names
    summary_voting_history.columns = [f'{i} of {num_elections}' for i in range(num_elections + 1)]

    columns_for_detailed_age = ["VoterID", "Race", "Sex", "Birth_Date", "Precinct"]
    columns_for_detailed_voting_history = ["VoterID", "Race", "Sex", "Birth_Date", "Precinct"] + selected_elections

    return summary_age, df[columns_for_detailed_age], summary_voting_history, df[columns_for_detailed_voting_history]

def main():
    df = load_data()

    st.title("Welcome to the Voting Data Summary App")
    st.write("""
        The intent of this app is to provide quick counts on voters in your precincts. 
        The counts provided are intended to quickly identify the potential size of different groups of voters.
    """)

    elections = df.columns[18:]
    selected_elections = st.multiselect("Select the elections to analyze voting patterns", elections, default=[elections[-1]])

    precincts = df['Precinct'].unique()
    selected_precincts = st.multiselect("Select the precincts for the analysis", sorted(precincts), default=sorted(precincts))

    voter_status = df['Voter Status'].unique()
    selected_voter_status = st.multiselect("Select the voter status for the analysis", sorted(voter_status), default=sorted(voter_status))

    summary_age, detailed_age, summary_voting_history, detailed_voting_history = summarize_voting_data(df, selected_elections, selected_precincts, selected_voter_status)

    st.write("### Age Distribution")
    st.write(summary_age)
    if st.button("Download Age Distribution Detailed Data"):
        st.markdown(create_download_link(detailed_age, "detailed_age.csv"), unsafe_allow_html=True)

    st.write("### Voting History")
    st.write(summary_voting_history)
    if st.button("Download Voting History Detailed Data"):
        st.markdown(create_download_link(detailed_voting_history, "detailed_voting_history.csv"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
