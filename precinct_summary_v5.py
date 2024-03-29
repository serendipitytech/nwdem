import streamlit as st
import pandas as pd
import numpy as np
import base64

# Password for accessing the download
password = "95_NWDems!"

def create_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'

def summarize_voting_data(df, selected_elections, selected_precincts, selected_voter_status):
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
    
    # add a condition for voter status
    if selected_voter_status:
        df = df[df['Status'].isin(selected_voter_status)]

        
    summary_age = df.groupby(['Race', 'Sex', 'Age Range']).size().unstack(fill_value=0)
    race_order = ["African American", "Hispanic", "White", "Other"]
    sex_order = ["M", "F", "U"]
    summary_age = summary_age.reindex(race_order, level='Race')
    summary_age = summary_age.reindex(sex_order, level='Sex')
    summary_age = summary_age.reindex(sex_order, level='Sex')
    summary_age.index = summary_age.index.map(lambda x: f'{x[0]}, {sex_mapping[x[1]]}')  # Combine the multi-index levels into a single string
  

    
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
    voting_history = df_voting_history[selected_elections].sum(axis=1)
    df['Voting History'] = voting_history

    summary_voting_history = df.groupby(['Race', 'Sex', 'Voting History']).size().unstack(fill_value=0)
    summary_voting_history = summary_voting_history.reindex(race_order, level='Race')
    summary_voting_history = summary_voting_history.reindex(sex_order, level='Sex')
    summary_voting_history.index = summary_voting_history.index.map(lambda x: f'{x[0]}, {sex_mapping[x[1]]}')  # Combine the multi-index levels into a single string

     # Get the number of selected elections
    num_elections = len(selected_elections)

    # Rename the column names
    summary_voting_history.columns = [f'{i} of {num_elections}' for i in range(num_elections + 1)]

    row_totals_voting_history = summary_voting_history.sum(axis=1)
    column_totals_voting_history = summary_voting_history.sum(axis=0)
    
     # select columns for the detailed dataframes
    columns_for_detailed_age = ["VoterID", "Race", "Sex", "Birth_Date", "Precinct"]  # replace with your actual column names
    columns_for_detailed_voting_history = ["VoterID", "Race", "Sex", "Birth_Date", "Precinct"] + selected_elections  # replace with your actual column names


    return summary_age, row_totals_age, column_totals_age, df[columns_for_detailed_age], summary_voting_history, row_totals_voting_history, column_totals_voting_history, df[columns_for_detailed_voting_history]

def load_data():
    df = pd.read_csv('https://deltonastrong-assets.s3.amazonaws.com/nw_dems_streamlit.txt', delimiter=',', low_memory=False)
    return df

def main():
    df = load_data()
    st.set_page_config(layout="wide")  # Make the Streamlit app full width
    st.title("Welcome to the Voting Data Summary App")
    st.write("""
        The intent of this app is to quick some quick counts on voters in your precicint.
        - **Step 1:** Open the side bar if you do not see it now. There will be a small arrow icon in the top left corner that you click or tap to open the side bar.
        - **Step 2:** Select the elections you wish to consider from the dropdown menu on the left.
        - **Step 3:** Select the princtincts from the dropdown menu on the left.
        - **Note:** You can select multiple precincts and elections and the counts will update with those selections.
        """)
    st.sidebar.title("Filter Selections:")
    
    # add a selection for voter status
    voter_status = df['Status'].unique().tolist()
    selected_voter_status = st.sidebar.multiselect("Select Voter Status:", voter_status, default=['ACT'], key="voter_status")

    
    selected_elections = st.sidebar.multiselect("Select up to three elections:", [
        "11-08-2022 General Election(Nov/08/2022)",
        "08-23-2022 Primary Election(Aug/23/2022)",
        "20201103 General Election(Nov/03/2020)",
        "20200818 Primary Election(Aug/18/2020)",
        "20200317 Pres Preference Primary(Mar/17/2020)",
        "11-02-2021 Municipal Election(Nov/02/2021)",
        "Municipal Election(Aug/17/2021)",
        "20190521 Mail Ballot Election(May/21/2019)",
        "20190402 Edgewater Special General(Apr/02/2019)"
        "20191105 Lake Helen General(Nov/05/2019)",
        "Daytona Beach Special Primary(Sep/21/2021)",
        "20190430 Pt Orange Special Primary(Apr/30/2019)",
        "04-13-2021 Port Orange Primary(Apr/13/2021)",
        "20190611 Pt Orange Special Runoff(Jun/11/2019)",
        "20200519 Pierson Mail Ballot Elec(May/19/2020)",
        "City of Flagler Beach(Mar/02/2021)",
        "City of Flagler Beach(Mar/17/2020)",
        "03-07-2023 Flagler Beach(Mar/07/2023)",
        "03/07/2023 Flagler Beach(Mar/07/2023)",
        "2022 City of Flagler Beach Election(Mar/08/2022)",

    ],default=["11-08-2022 General Election(Nov/08/2022)",
        "08-23-2022 Primary Election(Aug/23/2022)",
        "20201103 General Election(Nov/03/2020)"], key="elections")

    
    precincts = df['Precinct'].unique().tolist()  # replace 'Precinct' with your actual precinct column name
    selected_precincts = st.sidebar.multiselect("Select Precincts:", precincts, key="precincts")

   # get the summaries and detailed records
    summary_age, row_totals_age, column_totals_age, detailed_age, summary_voting_history, row_totals_voting_history, column_totals_voting_history, detailed_voting_history = summarize_voting_data(df, selected_elections, selected_precincts, selected_voter_status)
    summary_age.index = summary_age.index.to_series().replace({'M': 'Male', 'F': 'Female', 'U': 'Unreported'}, regex=True)
    summary_voting_history.index = summary_voting_history.index.to_series().replace({'M': 'Male', 'F': 'Female', 'U': 'Unreported'}, regex=True)

    #Create filtered dataframe for download
    filtered_df = df[df['Precinct'].isin(selected_precincts)]



   # display the summaries and download links
    #st.subheader("Voting Data Summary by Age Ranges")
    #st.table(summary_age)
    #st.markdown(create_download_link(detailed_age, "detailed_age_data.csv"), unsafe_allow_html=True)
    #st.subheader("Voting History by Race and Sex")
    #st.table(summary_voting_history)
    #st.markdown(create_download_link(detailed_voting_history, "detailed_voting_history_data.csv"), unsafe_allow_html=True)

 # Display summaries and download links with totals
    st.subheader("Voting Data Summary by Age Ranges")
    summary_age.loc['Column Total'] = summary_age.sum()  # Add column totals
    st.table(summary_age)
    #st.markdown(create_download_link(detailed_age, "detailed_age_data.csv"), unsafe_allow_html=True)
    


    st.subheader("Voting History by Race and Sex")
    summary_voting_history.loc['Column Total'] = summary_voting_history.sum()  # Add column totals
    st.table(summary_voting_history)
    #st.markdown(create_download_link(detailed_voting_history, "detailed_voting_history_data.csv"), unsafe_allow_html=True)
    #st.markdown(create_download_link(filtered_df, "filtered_data.csv"), unsafe_allow_html=True)
    
    
    st.subheader("Secure CSV Download")
    st.write("If you need a password to download this data, please email t.shimkus@nwdemocrats.org")
    # Password input
    user_password = st.text_input("Enter Password:", type="password")

    #Create filtered list using sidebar precinct filter
    #selected_precincts = st.sidebar.multiselect("Select Precincts:", df['Precinct'].unique())
    # Filter the data based on selected precincts
    #filtered_df = df[df['Precinct'].isin(selected_precincts)]

    if st.button("Submit"):
        if user_password == password:
            st.success("Password Correct! You can now download the CSV file.  \nIf the preview below is blank, ensure you have selected at least one precicnt in the left menu.")

            # Display filtered data
            st.write(filtered_df)

            # Download link for filtered data
            st.markdown(create_download_link(filtered_df, "filtered_data.csv"), unsafe_allow_html=True)
        else:
            st.warning("Password Incorrect. Please try again.")

    
    #Display some information text in sidebar:
    st.sidebar.info("""
        You can select multiple precincts and elections to filter the data. We reccommend you select 3 of the major elections like national General or Primaries. This will help you determine who in the selected precincts are voting and how often
        """)
if __name__ == '__main__':
    main()
