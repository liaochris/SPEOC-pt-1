#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd


# In[9]:


import os 


# In[10]:


file_path = '/Users/isabellasmojver/Downloads/'


# In[93]:


import pandas as pd
import os
import re

# List of speculator names
speculator_names = [
    "Richard Platt", "William Duer", "William Constable", "Andrew Craigie",
    "Clement Biddle", "Elias Boudinot", "Robert Morris", "Gouverneur Morris",
    "Daniel Parker", "Herman LeRoy", "William Bayard", "John Delafield",
    "Watson and Greenleaf", "C. and J. Shaw", "Nicholas Low", "Robert Gilchrist",
    "Peter Stadnitski", "Matthys Ooster", "Karel D'Amour", "Kindreck Vollenhoven",
    "Hendrick Vollenhoven", "Etienne L'Espinasse", "Christian van Eighen",
    "Nicholas Van Staphorst", "Gerrit Nutges", "Johan van Franckenstein",
    "Richard Smith", "James Jarvis", "Christopher Gore", "Samuel Rogers",
    "Francis Baring", "Edmund Boehm", "Thomas Hinchman", 
    "Charles John Michael de Wolf", "Francis Vanderborcht", "James Seagrove",
    "Robert Hazlehurst & Co.", "Robert Hazlehurst", "Leonard Bleecker",
    "Nathaniel Prime", "Samuel Breck", "David Sears", "Nathan Bond",
    "William Philips", "William Philips, Jr.", "John Peck", "Jonathan Mason",
    "Jonathan Mason, Jr.", "William Burley", "John Sprague", "Mordecai Lewis", "William Bingham",
    "Matthew McConnell", "Blair McClenachan", "Solomon Lyons", "Peter Wikoff",
    "Charles Pettit", "John Olden", "John M. Taylor", "Walter Stewart",
    "Andrew Summers, Jr.", "Mrs. McClenachan", "Christopher Marshall",
    "Christopher Marshall, Jr.", "Charles Marshall", "Andrew Caldwell",
    "John Caldwell", "Nicholas Brown", "Philip Allen", "Zachariah Allen",
    "Jabez Bowen", "Clarke and Nightingale", "Nightingale", "Joseph Clarke",
    "Welcome Arnold", "John Harbach", "Hazard", "Addoms", "Robert Bridges", "Edward Fox",
    "Dr. Robert Blackwell", "Thomas Willing"
]

file_path = '/Applications/SPEOC-pt-1/cleaning_CD/pre1790/data/agg_debt_grouped.csv'

# Read the CSV file
df = pd.read_csv(file_path, low_memory=False)
print("File successfully loaded.")

# Function to check if a full name matches any speculator name
def is_speculator(first_name, last_name):
    if pd.isna(first_name) or pd.isna(last_name):
        return False
    full_name = f"{first_name} {last_name}".lower()
    return any(speculator.lower() in full_name for speculator in speculator_names)

df['is_speculator'] = df.apply(lambda row: is_speculator(row['to whom due | first name'], row['to whom due | last name']), axis=1)

speculator_rows = df[df['is_speculator']]

if not speculator_rows.empty:
    print(f"\nFound {len(speculator_rows)} rows with potential speculator names:")
    columns_to_display = ['to whom due | first name', 'to whom due | last name']
    
    # Save results to CSV
    speculator_rows.to_csv('speculator_matches_agg_debt_grouped.csv', index=False)
    print("\nFull results saved to 'speculator_matches_agg_debt_grouped.csv'")
else:
    print("No speculator names found in the file.")

print("\nSummary of potential matches:")
for speculator in speculator_names:
    count = speculator_rows.apply(lambda row: speculator.lower() in f"{row['to whom due | first name']} {row['to whom due | last name']}".lower(), axis=1).sum()
    if count > 0:
        print(f"{speculator}: {count} potential matches")


# In[26]:


import pandas as pd
import os
import re

speculators = [
    "Richard Platt", "William Duer", "William Constable", "Andrew Craigie",
    "Clement Biddle", "Elias Boudinot", "Robert Morris", "Gouverneur Morris",
    "Daniel Parker", "Herman LeRoy", "William Bayard", "John Delafield",
    "Watson and Greenleaf", "C. and J. Shaw", "Nicholas Low", "Robert Gilchrist",
    "Peter Stadnitski", "Matthys Ooster", "Karel D'Amour", "Kindreck Vollenhoven",
    "Hendrick Vollenhoven", "Etienne L'Espinasse", "Christian van Eighen",
    "Nicholas Van Staphorst", "Gerrit Nutges", "Johan van Franckenstein",
    "Richard Smith", "James Jarvis", "Christopher Gore", "Samuel Rogers",
    "Francis Baring", "Edmund Boehm", "Thomas Hinchman", 
    "Charles John Michael de Wolf", "Francis Vanderborcht", "James Seagrove",
    "Robert Hazlehurst & Co.", "Robert Hazlehurst", "Leonard Bleecker",
    "Nathaniel Prime", "Samuel Breck", "David Sears", "Nathan Bond",
    "William Philips", "William Philips, Jr.", "John Peck", "Jonathan Mason",
    "Jonathan Mason, Jr.", "William Burley", "John Sprague", "Mordecai Lewis", "William Bingham",
    "Matthew McConnell", "Blair McClenachan", "Solomon Lyons", "Peter Wikoff",
    "Charles Pettit", "John Olden", "John M. Taylor", "Walter Stewart",
    "Andrew Summers, Jr.", "Mrs. McClenachan", "Christopher Marshall",
    "Christopher Marshall, Jr.", "Charles Marshall", "Andrew Caldwell",
    "John Caldwell", "Nicholas Brown", "Philip Allen", "Zachariah Allen",
    "Jabez Bowen", "Clarke and Nightingale", "Nightingale", "Joseph Clarke",
    "Welcome Arnold", "John Harbach", "Hazard", "Addoms", "Robert Bridges", "Edward Fox",
    "Dr. Robert Blackwell", "Thomas Willing"
]

print(f"Number of speculators defined: {len(speculators)}")

# List of CSV files 
csv_files = {
    'Pierce_Certs_cleaned_2019.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_DE.csv': {'first': 'First', 'last': 'Last'},
    'loan_office_certificates_9_states.csv': {'first': 'First', 'last': 'Last'},
    'Marine_Liquidated_Debt_Certificates.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_CT.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_MA_cleaned.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_NH.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_NJ.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_NY.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_PA_stelle.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_PA_story.csv': {'first': 'First', 'last': 'Last'},
    'liquidated_debt_certificates_RI.csv': {'first': 'First', 'last': 'Last'},
}

# Directory containing the CSV files
directory = '/Users/isabellasmojver/Downloads/'

speculator_files = {name: set() for name in speculators}

def find_speculator(name):
    name = str(name).lower()
    for speculator in speculators:
        if re.search(r'\b' + re.escape(speculator.lower()) + r'\b', name):
            return speculator
    return None

def process_file(file_name, df, columns):
    print(f"\nProcessing file: {file_name}")
    
    first_col, last_col = columns['first'], columns['last']
    
    if first_col not in df.columns or last_col not in df.columns:
        print(f"Warning: Required columns not found in {file_name}")
        print(f"Columns in file: {', '.join(df.columns)}")
        return
    
    df['full_name'] = df[first_col].astype(str) + ' ' + df[last_col].astype(str)
    matches = df['full_name'].apply(find_speculator)
    for speculator in matches.dropna().unique():
        speculator_files[speculator].add(file_name)
        print(f"Found {speculator} in {file_name}")

# Process each CSV file
for file_name, columns in csv_files.items():
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, low_memory=False)
            process_file(file_name, df, columns)
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
    else:
        print(f"File not found: {file_name}")

# Display results
print("\nSpeculator names found and their corresponding CSV files:")
for speculator, files in sorted(speculator_files.items()):
    if files:
        print(f"\n{speculator}:")
        for file in sorted(files):
            print(f"  - {file}")

# Count and display total number of speculators found
speculators_found = sum(1 for files in speculator_files.values() if files)
print(f"\nTotal number of speculators found: {speculators_found}")

# Save results to a CSV file
results = []
for speculator, files in speculator_files.items():
    if files:
        results.append({
            'Speculator': speculator,
            'Files': ', '.join(sorted(files))
        })

results_df = pd.DataFrame(results)
results_df.to_csv('speculator_file_matches.csv', index=False)
print("\nResults saved to 'speculator_file_matches.csv'")


# In[83]:


import pandas as pd
import re

# List of speculator names
speculators = [
    "Richard Platt", "William Duer", "William Constable", "Andrew Craigie",
    "Clement Biddle", "Elias Boudinot", "Robert Morris", "Gouverneur Morris",
    "Daniel Parker", "Herman LeRoy", "William Bayard", "John Delafield",
    "Watson and Greenleaf", "C. and J. Shaw", "Nicholas Low", "Robert Gilchrist",
    "Peter Stadnitski", "Matthys Ooster", "Karel D'Amour", "Kindreck Vollenhoven",
    "Hendrick Vollenhoven", "Etienne L'Espinasse", "Christian van Eighen",
    "Nicholas Van Staphorst", "Gerrit Nutges", "Johan van Franckenstein",
    "Richard Smith", "James Jarvis", "Christopher Gore", "Samuel Rogers",
    "Francis Baring", "Edmund Boehm", "Thomas Hinchman", 
    "Charles John Michael de Wolf", "Francis Vanderborcht", "James Seagrove",
    "Robert Hazlehurst & Co.", "Robert Hazlehurst", "Leonard Bleecker",
    "Nathaniel Prime", "Samuel Breck", "David Sears", "Nathan Bond",
    "William Philips", "William Philips, Jr.", "John Peck", "Jonathan Mason",
    "Jonathan Mason, Jr.", "William Burley", "John Sprague", "Mordecai Lewis", 
    "Matthew McConnell", "Blair McClenachan", "Solomon Lyons",
    "Charles Pettit", "John Olden", "John M. Taylor", "Walter Stewart",
    "Andrew Summers, Jr.", "Mrs. McClenachan", "Christopher Marshall",
    "Christopher Marshall, Jr.", "Charles Marshall", "Andrew Caldwell",
    "John Caldwell", "Nicholas Brown", "Philip Allen", "Zachariah Allen",
    "Jabez Bowen", "Clarke and Nightingale", "Nightingale", "Joseph Clarke",
    "Welcome Arnold", "John Harbach", "Hazard", "Addoms", "Robert Bridges", "Edward Fox",
    "Dr. Robert Blackwell", "Thomas Willing"
]

# File path
file_path = '/Applications/SPEOC-pt-1/cleaning_CD/pre1790/data/agg_debt_grouped.csv'

# Read the CSV file
df = pd.read_csv(file_path, low_memory=False)
print("File successfully loaded.")

def find_speculator(full_name):
    full_name = str(full_name).lower()
    for speculator in speculators:
        if re.search(r'\b' + re.escape(speculator.lower()) + r'\b', full_name):
            return speculator
    return None

# Combine first and last name columns
df['full_name'] = df['to whom due | first name'] + ' ' + df['to whom due | last name']

df['speculator'] = df['full_name'].apply(find_speculator)

speculator_sums = df[df['speculator'].notna()].groupby('speculator')['amount | dollars'].sum()

print("\nSpeculator Name : Total Dollar Value")
print("-" * 40)
for speculator, total_dollars in speculator_sums.items():
    print(f"{speculator}: ${total_dollars:.2f}")

# Save results to CSV
results_df = pd.DataFrame({'Speculator': speculator_sums.index, 'Total Dollar Value': speculator_sums.values})
results_df.to_csv('speculator_dollar_values.csv', index=False)
print("\nResults saved to 'speculator_dollar_values.csv'")

print(f"\nTotal number of speculators found: {len(speculator_sums)}")
print(f"Total dollar value across all speculators: ${speculator_sums.sum():.2f}")


# In[81]:


import pandas as pd
import os
import re

# List of speculator names
speculators = [
    "Richard Platt", "William Duer", "William Constable", "Andrew Craigie",
    "Clement Biddle", "Elias Boudinot", "Robert Morris", "Gouverneur Morris",
    "Daniel Parker", "Herman LeRoy", "William Bayard", "John Delafield",
    "Watson and Greenleaf", "C. and J. Shaw", "Nicholas Low", "Robert Gilchrist",
    "Peter Stadnitski", "Matthys Ooster", "Karel D'Amour", "Kindreck Vollenhoven",
    "Hendrick Vollenhoven", "Etienne L'Espinasse", "Christian van Eighen",
    "Nicholas Van Staphorst", "Gerrit Nutges", "Johan van Franckenstein",
    "Richard Smith", "James Jarvis", "Christopher Gore", "Samuel Rogers",
    "Francis Baring", "Edmund Boehm", "Thomas Hinchman", 
    "Charles John Michael de Wolf", "Francis Vanderborcht", "James Seagrove",
    "Robert Hazlehurst & Co.", "Robert Hazlehurst", "Leonard Bleecker",
    "Nathaniel Prime", "Samuel Breck", "David Sears", "Nathan Bond",
    "William Philips", "William Philips, Jr.", "John Peck", "Jonathan Mason",
    "Jonathan Mason, Jr.", "William Burley", "John Sprague", "Mordecai Lewis",
    "Matthew McConnell", "Blair McClenachan", "Solomon Lyons",
    "Charles Pettit", "John Olden", "John M. Taylor", "Walter Stewart",
    "Andrew Summers, Jr.", "Mrs. McClenachan", "Christopher Marshall",
    "Christopher Marshall, Jr.", "Charles Marshall", "Andrew Caldwell",
    "John Caldwell", "Nicholas Brown", "Philip Allen", "Zachariah Allen",
    "Jabez Bowen", "Clarke and Nightingale", "Nightingale", "Joseph Clarke",
    "Welcome Arnold", "John Harbach", "Hazard", "Addoms", "Robert Bridges", "Edward Fox",
    "Dr. Robert Blackwell", "Thomas Willing"
]

# Directory containing the CSV files
directory = '/Users/isabellasmojver/Downloads/'

# List of CSV files
csv_files = {
    'Pierce_Certs_cleaned_2019.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Value'},
    'liquidated_debt_certificates_DE.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'loan_office_certificates_9_states.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Specie Value'},
    'Marine_Liquidated_Debt_Certificates.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_CT.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_NH.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_NJ.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_NY.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_PA_stelle.csv': {'First': 'First', 'Last': 'Last', 'Dollars':'Dollars'},
    'liquidated_debt_certificates_PA_story.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_RI.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'},
    'liquidated_debt_certificates_MA_cleaned.csv': {'First': 'First', 'Last': 'Last', 'Dollars': 'Dollars'}
}

def find_speculator(name):
    name = str(name).lower()
    for speculator in speculators:
        if re.search(r'\b' + re.escape(speculator.lower()) + r'\b', name):
            return speculator
    return None

speculator_totals = {speculator: 0 for speculator in speculators}

for file_name, columns in csv_files.items():
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, low_memory=False)
            
            if not all(col in df.columns for col in columns.values() if col is not None):
                continue
            
            df = df.rename(columns={v: k for k, v in columns.items() if v is not None})
            
            if columns['Dollars'] is None:
                continue
            
            df['Dollars'] = pd.to_numeric(df['Dollars'], errors='coerce')
            
            df['Full Name'] = df['First'] + ' ' + df['Last']
            df['Speculator'] = df['Full Name'].apply(find_speculator)
            
            for speculator in speculators:
                mask = df['Speculator'] == speculator
                total = df.loc[mask, 'Dollars'].sum()
                if total > 0:
                    speculator_totals[speculator] += total
        
        except Exception as e:
            pass
    else:
        pass

print("\nSpeculator Name : Total Dollar Value")
print("-" * 40)
for speculator, total in sorted(speculator_totals.items(), key=lambda x: x[1], reverse=True):
    if total > 0:
        print(f"{speculator}: ${total:.2f}")

results_df = pd.DataFrame(list(speculator_totals.items()), columns=['Speculator', 'Total Dollar Value'])
results_df = results_df[results_df['Total Dollar Value'] > 0].sort_values('Total Dollar Value', ascending=False)
results_df.to_csv('speculator_dollar_values.csv', index=False)


# In[89]:


import pandas as pd
from IPython.display import display

# Create an empty DataFrame with the specified columns
df = pd.DataFrame(columns=[
    'Businessmen who wanted debt',
    'Who they contracted to obtain that debt',
    'How much they tried to obtain',
    'How much they obtained (according to our data)',
    'When they tried to do this',
    'Page number(s)'
])

businessmen = [
        "Richard Platt", "William Duer", "William Constable", "Andrew Craigie, Christopher Gore", 
        "Gouverneur Morris", "Charles John Michael de Wolf and Francis Vanderborcht", "Francis Baring, Edmund Boehm, Thomas Hinchman", 
        "Clement Biddle", "Clement Biddle", "Clement Biddle", "Elias Boudinot", "Peter Stadnitski", 
        "Matthys Ooster", "Karel D'Amour", "Kindreck Vollenhovem", "Hendrick Vollenhoven", "Etienne L'Espinasse", 
        "Christian van EIghen", "Mordecai Lewis", "Matthew McConnell", "Andrew Summers, Jr.", "Hazard and Addoms", 
        "Robert Bridges", "Edward Fox", "Reverend Dr. Robert Blackwell", "Robert Morris", "Thomas Willing",
        "Blair McClenachan", "Mrs. McClenachan", "Solomon Lyon", "John Olden", "John M. Taylor", "John Delafied", 
        "Charles Petit", "Nicholas Brown", "Philip Allen", "Joseph Clarke", "Nicholas Low", "Herman LeRoy", "William Bayard", 
        "Watson and Greenleaf", "C. and J. Shaw", "Robert Gilchrist", "Nicholas Van Staphorst", "Gerit Nutges", 
        "Johan van Franckenstein", "Daniel Parker", "Daniel Parker", "William Constable", "William Constable", "Leonard Bleecker", "Nathaniel Prime", "Samuel Breck", "William Philips", 
        "William Philips, Jr.", "Jonathan Mason", "Jonathan Mason, Jr.", "William Burley", "Nathan Bond", "David Sears", 
        "John Peck", "John Sprague", "John Harbach", "General Walter Stewart", "Christopher Marshall, Christopher Marshall, Jr., Charles Marshall", 
        "Andrew Caldwell and John Caldwell", "Zachariah Allen", "Jabez Bowen", 
        "Clarke and Nightingale", "Welcome Arnold"
]

contractors = [
        "Winthrop Sargent", "John Holker", "James Jarvis", "N/A", "Daniel Parker", 
        "Gouverneur Morris, Parker, Samuel Rogers", "Gouverneur Morris", "N/A", 
        "Richard Smith", "Robert Gilchrist", "N/A", "Daniel Parker, Andrew Craigie", 
        "Daniel Parker, Andrew Craigie", "Daniel Parker, Andrew Craigie", "Daniel Parker, Andrew Craigie", 
        "Daniel Parker", "Daniel Parker", "Daniel Parker", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", 
        "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", 
        "N/A", "N/A", "N/A", "N/A", "Daniel Parker", "Daniel Parker", "Daniel Parker", "Richard Smith", 
        "James Jarvis", "James Seagrove", "Robert Hazlehurst & Co.", "N/A", "N/A", "N/A", "N/A", "N/A", 
        "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
]

pages = [
    "253", "264", "257", "263", "270", "265", "265", "280", "269", "258", "284", "260", "260", "260", "260", 
    "262", "262", "262", "284", "284", "284", "284", "284", "284", "284", "284", "284", "284", "280", "279", 
    "280", "280", "280", "258", "280", "282", "281", "281", "258", "258", "258", "258", "258", "258", "262", 
    "262", "262", "262", "262", "272", "272", "272", "274", "274", "274", "274", "274", "274", "274", "274", 
    "274", "274", "274", "284", "280", "279", "279", "282", "281", "282", "281"
]

tried_to_obtain = [
    "N/A", "N/A", "N/A", "$100,000", "N/A", "$65,000", "$600,000", "$85,000", "N/A", "N/A",
    "$12,700 state, $36,000 Treasury", "At least $200,000", "At least $200,000", "At least $200,000", "At least $200,000",
    "$200,000", "$200,000", "$200,000", "$293,000 state, $10,500 Treasury", "$87,000 state, $14,000 Treasury",
    "$46,000 state, $13,000 Treasury", "$34,500 state, $19,500 Treasury", "$31,000 state, $18,000 Treasury",
    "$30,500 state, $28,600 Treasury", "$27,000 state, $64,000 Treasury", "$28,200 state",
    "$20,000 state, $20,000 Treasury", "$74,000", "$21,400", "$61,000", "$55,000", 
    "$50,000", "N/A", "$55,000", "$49,973 original, $13,408 transferred",
    "$19,865 original, $12,545 transferred", "$29,789", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
    "$1,200,000", "$1,200,000", "$1,200,000", "$250,000", "$300,000", "N/A", "$100,000", "$200,000 or $400,000",
    "$196,000", "$104,300", "$94,000", "$49,000", "$89,000", "$20,486", "$93,000", "$88,000",
    "$72,000", "$65,000", "$68,000", "$20,900 state, $63,600 Treasury", "N/A", "Over $50,000", "$53,000",
    "$16,420 original, $5,860 transferred", "$19,065", "$15,792", "$11,994"
]

amount_obtained = [
    "Richard Platt: $19,420", "William Duer: $231", "James Jarvis: $5,800", "N/A", "N/A",
    "Samuel Rogers: $13,021", "N/A", "Clement Biddle: $117,121", "Richard Smith: $884", "N/A",
    "Elias Boudinot: $57,858", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "$56,728", "Robert Bridges: $28,880", "N/A", "N/A",
    "Robert Morris: $406,751", "Thomas Willing: $1", "Blair McClenachan: $2,389", "N/A", "N/A",
    "John Olden: $2,000", "N/A", "John Delafield: $1,346", "Charles Petit: $82,500", "Nicholas Brown: $32,900",
    "Philip Allen: $17", "Joseph Clarke: $6,039", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "Daniel Parker: $4,300", "N/A", "N/A", "N/A",
    "Leonard Bleecker: $379", "N/A", "Samuel Breck: $96", "William Philips: $800", "N/A",
    "Jonathan Mason: $9,107", "N/A", "William Burley: $3,050", "Nathan Bond: $94", "N/A",
    "John Peck: $361", "John Sprague: $38,705", "N/A", "N/A", "Christopher Marshall: $11,000",
    "Andrew and John Caldwell: $96,040", "Zachariah Allen: $47.00", "N/A", "Nightingale: $866.85", "Welcome Arnold: $106"
]

when_tried = [
   "May 30, 1786", "Dec. 10, 1788", "Jan. 12, 1789", "Aug. 7, 1788", "May 1789", "Feb. 26, 1790", "1789",
    "N/A", "May 23, 1790", "Mar. 23, Dec. 24, 1789", "N/A", "1786",
    "1786", "1786", "1786", "1788", "1788",
    "1788", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "Aug. 1788", "Aug. 1788",
    "Aug. 1788", "May 27, 1788", "June 18, 1788", "Nov. 19, 1789", "Dec. 15, 1789", "Dec. 19, 1789",
    "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A", "N/A", "N/A",
    "N/A", "N/A", "N/A",
    "N/A", "N/A"
]

# Create a DataFrame with the businessmen names
df['Businessmen who wanted debt'] = businessmen

# Add creditors to the "Who they contracted to obtain that debt" column
# If there are fewer creditors than businessmen, the remaining rows will be NaN
df['Who they contracted to obtain that debt'] = pd.Series(contractors)

# Add page numbers to the "Page number(s)" column
df['Page number(s)'] = pd.Series(pages)

# Add "tried to obtain" amounts to the "How much they tried to obtain" column
df['How much they tried to obtain'] = pd.Series(tried_to_obtain)

# Add "when tried" dates to the "When they tried to do this" column
df['When they tried to do this'] = pd.Series(when_tried)

# Add "amount obtained" to the "How much they obtained (according to our data)" column
df['How much they obtained (according to our data)'] = pd.Series(amount_obtained)

# Reset the index to start from 1 and make it visible
df.index = range(1, len(df) + 1)
df.index.name = 'No.'

# Style the table for better readability
styled_df = df.style.set_properties(**{'text-align': 'left'})
styled_df = styled_df.set_table_styles([
    dict(selector='th', props=[('text-align', 'center')]),
    dict(selector='td', props=[('text-align', 'left')])
])

# Display the styled table
display(styled_df)


# In[ ]:




