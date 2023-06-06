import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")  # Make the Streamlit app full width

def summarize_voting_data(df, selected_elections, selected_precincts):
    #df = pd.read_csv(file_path, delimiter=',', low_memory=False)
    #df = df[df['Voter Status'] == 'ACT']

    race_mapping = {
        1: "Other",
        2: "Other",
        6: "Other",
        9: "Other",
        3: "African American",
        4: "Hispanic",
        5: "White"
    }
    df['Race'] = df['Race'].map(race_mapping)

    sex_mapping = {
        "M": "M",
        "F": "F",
        "U": "U"
    }
    df['Sex'] = df['Sex'].map(sex_mapping)

    df['Birth_Date'] = pd.to_datetime(df['Birth_Date'])
    df['Age'] = (pd.to_datetime('today').year - df['Birth_Date'].dt.year)


    age_ranges = {
        '18-28': (18, 28),
        '26-34': (26, 34),
        '35-55': (35, 55),
        '55+': (55, float('inf'))
    }

    df['Age Range'] = pd.cut(df['Age'], bins=[age_ranges[range_name][0]-1 for range_name in age_ranges.keys()] + [age_ranges['55+'][1]], labels=age_ranges.keys())

    if selected_precincts:
        df = df[df['Precinct'].isin(selected_precincts)]

    summary_age = df.groupby(['Race', 'Sex', 'Age Range']).size().unstack(fill_value=0)

    race_order = ["African American", "Hispanic", "White", "Other"]
    sex_order = ["M", "F", "U"]
    summary_age = summary_age.reindex(race_order, level='Race')
    summary_age = summary_age.reindex(sex_order, level='Sex')

    row_totals_age = summary_age.sum(axis=1)
    column_totals_age = summary_age.sum(axis=0)

    selected_columns = [
        "03-07-2023 Flagler Beach(Mar/07/2023)",
        "03/07/2023 Flagler Beach(Mar/07/2023)",
        "11-08-2022 General Election(Nov/08/2022)",
        "08-23-2022 Primary Election(Aug/23/2022)",
        "2022 City of Flagler Beach Election(Mar/08/2022)",
        "11-02-2021 Municipal Election(Nov/02/2021)",
        "Daytona Beach Special Primary(Sep/21/2021)",
        "Municipal Election(Aug/17/2021)",
        "04-13-2021 Port Orange Primary(Apr/13/2021)",
        "City of Flagler Beach(Mar/02/2021)",
        "20201103 General Election(Nov/03/2020)",
        "20200818 Primary Election(Aug/18/2020)",
        "20200519 Pierson Mail Ballot Elec(May/19/2020)",
        "20200317 Pres Preference Primary(Mar/17/2020)",
        "City of Flagler Beach(Mar/17/2020)",
        "20191105 Lake Helen General(Nov/05/2019)",
        "20190611 Pt Orange Special Runoff(Jun/11/2019)",
        "20190521 Mail Ballot Election(May/21/2019)",
        "20190430 Pt Orange Special Primary(Apr/30/2019)",
        "20190402 Edgewater Special General(Apr/02/2019)"
    ]

    df_voting_history = df[selected_columns].applymap(lambda x: 1 if x in ['Y', 'Z', 'A', 'E', 'F'] else 0)
    voting_history = df_voting_history[selected_elections].max(axis=1)
    df = df.assign(Voting_History=voting_history)

    summary_voting_history = df.groupby(['Race', 'Sex', 'Voting_History']).size().unstack(fill_value=0)
    summary_voting_history = summary_voting_history.reindex(race_order, level='Race')
    summary_voting_history = summary_voting_history.reindex(sex_order, level='Sex')

    row_totals_voting_history = summary_voting_history.sum(axis=1)
    column_totals_voting_history = summary_voting_history.sum(axis=0)

    return summary_age, row_totals_age, column_totals_age, summary_voting_history, row_totals_voting_history, column_totals_voting_history

def load_data():
    df = pd.read_csv('https://deltonastrong-assets.s3.amazonaws.com/nw_dems_data_1.txt', delimiter=',', low_memory=False)
    return df

def summary_tables():
    
    st.title("Voting Data Summary")
    
    selected_elections = st.multiselect("Select three elections:", [
        "03-07-2023 Flagler Beach(Mar/07/2023)",
        "03/07/2023 Flagler Beach(Mar/07/2023)",
        "11-08-2022 General Election(Nov/08/2022)",
        "08-23-2022 Primary Election(Aug/23/2022)",
        "2022 City of Flagler Beach Election(Mar/08/2022)",
        "11-02-2021 Municipal Election(Nov/02/2021)",
        "Daytona Beach Special Primary(Sep/21/2021)",
        "Municipal Election(Aug/17/2021)",
        "04-13-2021 Port Orange Primary(Apr/13/2021)",
        "City of Flagler Beach(Mar/02/2021)",
        "20201103 General Election(Nov/03/2020)",
        "20200818 Primary Election(Aug/18/2020)",
        "20200519 Pierson Mail Ballot Elec(May/19/2020)",
        "20200317 Pres Preference Primary(Mar/17/2020)",
        "City of Flagler Beach(Mar/17/2020)",
        "20191105 Lake Helen General(Nov/05/2019)",
        "20190611 Pt Orange Special Runoff(Jun/11/2019)",
        "20190521 Mail Ballot Election(May/21/2019)",
        "20190430 Pt Orange Special Primary(Apr/30/2019)",
        "20190402 Edgewater Special General(Apr/02/2019)"
    ], key="elections")
    
    precincts = st.session_state.df['Precinct'].unique().tolist()  # replace 'Precinct' with your actual precinct column name
    selected_precincts = st.multiselect("Select Precincts:", precincts, key="precincts")
    
    if not selected_elections or not selected_precincts:
        st.warning("Please select at least one election and one precinct.")
        return
    
    # Calling the function with selected elections and precincts as arguments
    summary_age, row_totals_age, column_totals_age, summary_voting_history, row_totals_voting_history, column_totals_voting_history = summarize_voting_data(st.session_state.df, selected_elections, selected_precincts)
    
    st.subheader("Voting Data Summary by Age Ranges")
    st.table(summary_age)

    st.subheader("Voting History by Race and Sex")
    st.table(summary_voting_history)
    
def record_details():
    st.title("Record Details")

    precincts = st.session_state.df['Precinct'].unique().tolist()  
    selected_precinct = st.selectbox("Select Precinct:", precincts, key="precinct")

    age_ranges = ['18-28', '26-34', '35-55', '55+']
    selected_age_range = st.selectbox("Select Age Range:", age_ranges, key="age_range")

    voting_histories = st.session_state.df['Voting_History'].unique().tolist()  
    selected_voting_history = st.selectbox("Select Voting_History:", voting_histories, key="Voting_Histroy")

    filtered_df = st.session_state.df[(st.session_state.df['Precinct'] == selected_precinct) & 
                                      (st.session_state.df['Age Range'] == selected_age_range) & 
                                      (st.session_state.df['Voting_History'] == selected_voting_history)]
    
    st.table(filtered_df)

def main():
    df = load_data()
    
    PAGES = {
        "Summary Tables": summary_tables,
        "Record Details": record_details
    }
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", list(PAGES.keys()))

    # Keep the data across pages
    st.session_state.df = df if 'df' not in st.session_state else st.session_state.df



    # Run the appropriate page function
    PAGES[page]()
    
if __name__ == '__main__':
    main()
