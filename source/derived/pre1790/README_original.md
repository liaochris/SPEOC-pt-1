# Cleaning Pre-1790 Debt Data 
The goal of this exercise was to clean the names of the individuals in the pre-1790 individual state debt files. There were many different kinds of issues we found with individuals' names. All of them can be found [here](https://docs.google.com/document/d/1pcSQfWNll6K9tl-_rB4lztN0TsZsclU9vOnbyQob-Zs/edit), along with comments and examples. In order to go about cleaning the individual debt files, ```@Snapwhiz914``` and ```@davidch2020``` decided to work on different parts of the cleaning process. 

## Setting up the Environment 
1. Clone this GitHub repository.
2. The latest version of Python is assumed to be installed. 
3. Enter your default terminal. 
4. Install all necessary packages: ```pip install -r requirements.txt```
*Note: When installing packages, make sure you are in the ```pre1790``` directory and using PIP v3.

## Running ```find-similar-names.ipynb```
**Goal**: Create separate .csv files for each state. These .csv files will contain a column for names in each state and another column with a list of similar names. These similar names are determined using fuzzy string matching. 
**Input**: ```agg_debt_grouped.csv```
**Output**: ```similar_names``` folder 

## Running ```combined.ipynb```
Run code cells from top-to-bottom. Here are the different sections of the code. More information in the headers. 

### Before Cleaning
**Goal**: Import all libraries and files. <br>
**Input**: ```final_agg_debt.csv``` type: CSV file <br>
**Output**: ```agg_debt``` type: Pandas dataframe

### Documenting Changes
**Goal**: We need to document changes we make to agg_debt.csv in a separate dataframe: name_changes. This way, we can double-check whether those changes were appropriate. <br>
**Input**: No inputs. <br>
**Output**: ```name_changes``` type: Pandas dataframe

| title_org   | title_new   | first_name_org   | last_name_org   | first_name_new   | last_name_new   | cleaning case   | file_loc   | org_index   |
|-------------|-------------|------------------|-----------------|------------------|-----------------|-----------------|------------|-------------|

Source: ```name_changes```

```python 
print(name_changes.to_markdown()) 
```

### Company Names
**Goal**: Some debt entries are actually company names or represent a group of people (example: ```James Vernon & Co.```).

|      | to whom due - first name   |
|-----:|:---------------------------|
| 5776 | Henry Wisner & Co          |
| 8879 | James Mc Farlane & others  |

Source: ```agg_debt```

```python
print(agg_debt['to whom due | first name'].loc[[5776, 8879]].to_markdown())
```

**Input**: ```agg_debt```, ```name_changes```<br>
**Output**: ```agg_debt```: Company names changed to people's names, ```name_changes``` + Company names

|    | first_name_org    |   last_name_org | first_name_new   | last_name_new   |
|---:|:------------------|----------------:|:-----------------|:----------------|
|  0 | Henry Wisner & Co |             nan | Henry            | Wisner          |

Source: ```name_changes```

```python
print(name_changes[['first_name_org', 'last_name_org', 'first_name_new', 'last_name_new']].head(1).to_markdown())
```

### Cleaning Entries with Two Names
<b>Goal: </b>There are debt entries that have two names in a single cell: ```NY_2422: Messes Williamson & Beckman```. The plan is to split the name across the first name and last name columns. <br>

|        | to whom due - first name            |
|-------:|:------------------------------------|
|    182 | Furman & Hunt                       |
| 178682 | William Rigden and Edward Middleton |

Source: ```agg_debt```

```python 
print(agg_debt['to whom due | first name'].loc[[182, 178682]].to_markdown())
```

**Input**: ```agg_debt```, ```name_changes``` <br>
**Output**: ```agg_debt```: Debt entries with two names reformatted, ```name_changes``` + Debt entries with two names

|      | first_name_org   |   last_name_org | first_name_new   | last_name_new      |
|-----:|:-----------------|----------------:|:-----------------|:-------------------|
| 1119 | Furman and Hunt  |             nan |                  | ['Furman', 'Hunt'] |

Source: ```name_changes```

```python
print(name_changes.loc[name_changes['first_name_org'] == 'Furman and Hunt'][['first_name_org', 'last_name_org', 'first_name_new', 'last_name_new']].head(1).to_markdown())
```

### Handle Abbreviations of Names
<b>Goal: </b>There are individuals who have a handwritten abbreviation of a name in their debt entry. Thanks to Chris, he found a website with all these [abbreviations](https://hull-awe.org.uk/index.php/Conventional_abbreviations_for_forenames). 

|        | to whom due - first name   | to whom due - last name   |
|-------:|:---------------------------|:--------------------------|
| 102117 | And                        | Wardleberger              |

Source: ```agg_debt```

```python 
print(agg_debt.loc[agg_debt['to whom due | first name'] == 'And'][['to whom due | first name', 'to whom due | last name']].head(1).to_markdown())
```

**Input**: ```agg_debt```, ```name_changes```, ```abbreviations``` dictionary <br>
**Output**: ```agg_debt```: Renamed abbreviations, ```name_changes``` + Abbreviations

|      | first_name_org   | last_name_org   | first_name_new   | last_name_new   |
|-----:|:-----------------|:----------------|:-----------------|:----------------|
| 3683 | And              | Wardleberger    | Andrew           | Wardleberger    |

Source: ```name_changes```

### Grouping Consecutive Names
<b>Goal: </b> By grouping consecutive names, standardizing names using Ancestry will go faster. <br>

|        | to whom due - first name   | to whom due - last name   |
|-------:|:---------------------------|:--------------------------|
| 107216 | James                      | Wood                      |
| 107217 | James                      | Wood                      |
| 107218 | James                      | Wood                      |
| 107219 | James                      | Wood                      |
| 107220 | James                      | Wood                      |
| 107221 | James                      | Wood                      |

```python
print(agg_debt.loc[107216:107221][['to whom due | first name', 'to whom due | last name']].to_markdown())
```

**Input**:```agg_debt``` (as ```og_df```) <br>
**Output**: ```agg_debt``` (as ```agg_df```): Consecutive names grouped together 

|       | to whom due - first name   | to whom due - last name   |
|------:|:---------------------------|:--------------------------|
| 50683 | James                      | Wood                      |

```python
print(agg_debt.loc[(agg_debt['to whom due | first name'] == 'James') & (agg_debt['to whom due | last name'] == 'Wood')][['to whom due | first name', 'to whom due | last name']].to_markdown())
```

### "Heirs of"/Estate of" prefix removal
<b>Goal: </b>Remove "Estate of", "Heirs of", "State of" prefixes in an entry, and marks "State of" entries as organizations

|       | to whom due - first name   | to whom due - last name |
|------:|:---------------------------|:------------------------|
| 1891  | Estate of Abigail Champney  |                         |

```python
print(agg_debt.loc[(agg_debt['to whom due | first name'] == 'Estate of Abigail Champney')][['to whom due | first name', 'to whom due | last name']].to_markdown())
```

**Input**:```agg_debt``` <br>
**Output**: ```agg_debt```: Rows with prefixes removed and names placed in thier correct column, ```name_changes```

|       | to whom due - first name   | to whom due - last name   |
|------:|:---------------------------|:--------------------------|
| 1891  | Abigail                    | Champney                  |

```python
print(agg_debt.loc[(agg_debt['to whom due | first name'] == 'Abigail') & (agg_debt['to whom due | last name'] == 'Champney')][['to whom due | first name', 'to whom due | last name']].to_markdown())
```

### Ancestry Search : ```ancestry_search_david.ipynb```
<b>Goal: </b>Multiple different spellings of a name can be referring to the same identity. We will use a phonetics library and Ancestry to fix this. An example: ```David Schaffer``` and ```David Schafer``` from `MA`. There is a possibility that both of these individuals are the same, but were incorrectly spelled. 

**Input**: ```agg_debt```, ```name_changes```
**Output**: ```ancestry_name_changes```, ```agg_debt``` : Ancestry name fixes, ```name_changes``` + Ancestry name fixes 

## Areas of Future Improvement and Research

**Optimized Parallelization**
Current parallelization code:
```python
df_split = np.array_split(similar_names_df, cpu_count())  
print(len(df_split))

# Initialize a parallelization job 
ancestry_calls = [delayed(ancestry_wrap)(df_split[i], driver_objs[i]) for i in range(7)]
results = Parallel(n_jobs=-1, backend="threading")(ancestry_calls) 
```

I am currently splitting up the dataframe into equal, smaller dataframes. Each CPU core will handle one smaller dataframe. However, this can be optimized. Once a core is done with its assigned smaller dataframe, it can help with another core's smaller dataframe. This way, performance remains constant. 

**Improved Data Storage**
Currently, we store name changes in a dictionary structured as such:
```
{[title1, title1, fn1, ln1, fn0, ln0, 6, org_file1, org_index1, state], ...}
```

However, I realize that this is not flexible. Sometimes, we need more information. A better way is to store the entire row instead of the row's information. Another way is to store the index (from ```agg_debt```) of the row. 










