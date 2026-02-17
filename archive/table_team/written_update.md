# Table Creation

Please see the file 'DataTable_0709_2'. 
The codes produce a table from the 'final_data_CD.csv' file.

The table now has some interactive features:
1) Filtering options under all columns.
     Eg. Enter "NY" under the "Group State" column
     Eg. Enter ">100" under the "Unpaid Interest" column
2) A dropdown list to display either the 4 charts grouped by states or the other 4 charts grouped by occupation.
3) Derived 4 bar charts according to the filter & dropdown list.
     X-axis for all 4 charts: different states / occupation (depends on the selection in dropdown list), eg. x-axis would be        “NY”, “RI”, “CT” if select 'Group by States'.
     Y-axis: FV of 6p debt, FV of 6p deferred debt, Unpaid Interest, Final Total
4) A slider bar to select how many values to display on the bar charts.
     Eg. Display the  bar chart of the 10 occupations which bought the most debt.

Things we are working on:
1) Styling. (Trying to be consistent with the style of the map team)
2) Dropping irrelevant columns in the dataset. (after confirming with Chris)


## Creating About Us and Project Description Pages

Description.


### Adding Changes to the Web App

We have taken the above codes, modifications, and efforts to create a web app with more visualizations and descriptions. '3-trial-app.py' has a fully functional web app with tables and pages. The separate pages were added first with their respective page layouts, then the table customization for the main/home page.
Some problems we've encountered and things we need to work on:
1) Integrating the separate pages into the existing web app creates an issue of not being apple to separate the map and table creation from the other pages. We plan to investigate further how to isolate code onto the home page.
2) Hoping to figure out how to put the table code into the app in the next few days especially once the app is fully functional on its own as a multi-page app
3) Adding some overall aesthetic pizzaz to the web app
