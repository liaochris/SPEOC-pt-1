using CSV, DataFrames, DataFramesMeta, Gadfly, XLSX, Dates, Compose, Plots

function clean_df(df) 
    df[:, :dollars] = replace(df[:, :dollars], "NaN" => missing) # replace "NaN" with missing
    df[:, :cents] = replace(df[:, :cents], "NaN" => missing) # replace "NaN" with missing
    df[:, :dollars] = replace(df[:, :dollars], missing => 0)  # replace missing with 0 
    df[:, :cents] = replace(df[:, :cents], missing => 0)  # replace missing with 0 
    df 
end 

function group_by_year(df) 
    gdf = @by(df, :year,
        :total_amt = sum(:dollars) + sum(:cents)  # calculate total amount of debt 
    )
    sort!(gdf) # sort by year 
    replace!(gdf.year, "missing" => "no year") # change missing values to string to allow for plotting
    return gdf 
end

function group_by_year_month(df)
    gdf = @by(df, [:year, :month],
        :total_amt = sum(:dollars) + sum(:cents)  # calculate total amount of debt 
    )
    
    return gdf 
end

#plot debt redeemed per year saved as svg 
function plot_debt(df::DataFrame, state, type)
    set_default_plot_size(40cm, 22.5cm)

    if type == "year"
        p_debt_date = Gadfly.plot(
            df,
            x=:year,
            y=:total_amt,
            Geom.bar,
            Guide.xlabel("Year"),
            Guide.ylabel("Total Debt (in dollars)"),
            Guide.title(uppercase(state)*" Debt Redeemed Per Year"),
            Gadfly.Theme(background_color = "white")
        )
        img = SVG("output/analysis/pre1790/debt_per_year/year/" * uppercase(state) * "_debt_redeemed_per_year.svg", 40cm, 22.5cm) 
        draw(img, p_debt_date)  
    elseif type == "year_month"
        p_debt_date = Gadfly.plot(
            df,
            x=:year_month,
            y=:total_amt,
            Geom.bar,
            Guide.xlabel("Year"),
            Guide.ylabel("Total Debt (in dollars)"),
            Guide.title(uppercase(state)*" Debt Redeemed Per Year/Month"),
            Gadfly.Theme(background_color = "white")
        )

        img = SVG("output/analysis/pre1790/debt_per_year/year_month/" * uppercase(state) * "_debt_redeemed_per_year_month.svg", 40cm, 22.5cm) 
        draw(img, p_debt_date)  
    end

    println(state)

end 

function group_post1795(state_df) 
    # filtering dataframes using multiple conditions 
    state_df_post1795 = @subset(state_df, :year_month .> DateTime(1795)) # filter out years before 1795
    state_df_post1795.total_amt = replace(state_df_post1795.total_amt, missing => 0) # replace missing values with 0
    state_df_sum = sum(state_df_post1795.total_amt) # sum total debt redeemed after 1795

    # remove rows where year is greater than 1795 
    state_df = @subset(state_df, :year_month .< DateTime(1795))
    
    # change datetime object to string 
    state_df.year_month = Dates.format.(state_df.year_month, "yyyy-mm")
    
    push!(state_df, [state_df_sum, "post-1795"], promote=true) # add total debt redeemed after 1795 to dataframe
    return state_df
end 

function handle_missing_info(state_df)
    missing_info = @rsubset(state_df, ismissing(:year) || ismissing(:month)) # filter out rows with missing year or month\
    missing_info_sum = 0
    if nrow(missing_info) > 0
        missing_info_sum = sum(missing_info.dollars + missing_info.cents) # sum total debt redeemed with missing year or month
    end 
    return missing_info_sum
end 

# import cd_info 
cd_info = DataFrame(CSV.File("output/derived/pre1790/cd_info.csv"))
# store total amount and years of all states in a new dataframe 
all_states = DataFrame([[], []], [:year_month, :total_amt])

# loop through cd_info per state 
for i in 1:nrow(cd_info)
    state_df = DataFrame() # create new dataframe for each state
    state_row = cd_info[i, :]
    state_excel = XLSX.readxlsx(state_row[:file_path])
    state_sheet = state_excel["Sheet1"]
    
    # get year columns --> merge years columns into one column 
    year_col_indexes = split(state_row[:year_col], ",")
    for year_col_index in year_col_indexes
        year_col_range = year_col_index*string(state_row[:first_row])*":"*year_col_index*string(state_row[:last_row])
        year_col = state_sheet[year_col_range]
        
        if nrow(state_df) == 0 # if state_df is empty, create year column 
            state_df.year = vec(year_col)
        else 
            state_df.year .= coalesce(state_df.year, vec(year_col)) # append year col to state dataframe
        end 
    end
    
    # get month columns --> merge month columns into one column
    month_col_indexes = split(state_row[:month_col], ",")
    for month_col_index in month_col_indexes
        month_col_range = month_col_index*string(state_row[:first_row])*":"*month_col_index*string(state_row[:last_row])
        month_col = state_sheet[month_col_range]

        if !("month" in names(state_df)) 
            state_df.month = vec(month_col)
        else
            state_df.month .= coalesce(state_df.month, vec(month_col)) # append month col to state dataframe
        end 
    end
    
    # add dollar amount column to states dataframe 
    dollar_indexes = split(state_row[:dollars_col], ",") 
    for dollar_index in dollar_indexes
        dollar_col_range = dollar_index*string(state_row[:first_row])*":"*dollar_index*string(state_row[:last_row])
        dollar_col = state_sheet[dollar_col_range]
        state_df.dollars = vec(dollar_col)
    end

    # add cents amount column to states dataframe 
    if !ismissing(state_row[:cents_col]) # handle excel spreadsheets with no cents column 
        cents_indexes = split(state_row[:cents_col], ",")
        for cents_index in cents_indexes
            cents_col_range = cents_index*string(state_row[:first_row])*":"*cents_index*string(state_row[:last_row])
            cents_col = state_sheet[cents_col_range]
            state_df.cents = vec(cents_col) ./ 100 # convert cents to decimal
        end 
    else 
        state_df.cents = zeros(nrow(state_df)) # create column of zeros to allow for summing
    end

    state_df = clean_df(state_df) # clean dataframe to removeq missing values from :dollars and :cents columns
    missing_info_sum = handle_missing_info(state_df) # get total value of rows with missing info 
    dropmissing!(state_df, [:year, :month]) # drop rows with missing values in year, month columns

    state_df.year = string.(state_df.year)
    state_df.month = string.(state_df.month)

    # add state label 
    state_df.state = fill(state_row[:state], nrow(state_df))

    state_df_clean = clean_df(state_df) # clean table to remove missing values
    state_gdf = group_by_year_month(state_df_clean) # group by year and month and sum debt 

    # create new column that merges year and month 
    state_gdf.year_month = string.(state_gdf[:, :year], "-", state_gdf[:, :month])

    # convert year_month column to datetime object 
    state_gdf.year_month = DateTime.(state_gdf.year_month, DateFormat("yyyy-mm"))
    sort!(state_gdf, :year_month) # sort by year_month column   

    # remove year and month columns 
    select!(state_gdf, Not([:year, :month]))

    all_states = vcat(all_states, state_gdf) # append state dataframe to all_states dataframe

    state_gdf = group_post1795(state_gdf) # filter out years before 1795
    push!(state_gdf, [missing_info_sum, "missing info"], promote=true) # add total debt redeemed with missing info to dataframe

    plot_debt(state_gdf, state_row[:state], "year_month") # plot debt redeemed per year saved as svg
    #plot_debt(state_gdf, state_row[:state], "year") # plot debt redeemed per year saved as svg

    println(last(state_gdf, 5)) 
end 


# plot united states 
all_states = @by(all_states, :year_month, :total_amt = sum(:total_amt)) # group by year and month and sum debt
all_states = all_states[!, [:total_amt, :year_month]] # swap columns
sort!(all_states, :year_month) # sort by year_month column
all_states = group_post1795(all_states) # filter out years before 1795

# import pre-1790 debt data 
# get unique dates 
# group by year - sum debt 
# plot debt redeemed per year saved as svg 

pre1790 = DataFrame(CSV.File("output/derived/pre1790/pre1790_cleaned.csv"))
pre1790.year = pre1790[:, "date of the certificate | year"]

# fix cents column in pre1790_cleaned.csv 
pre1790[:, "amount | 90th"] = getindex.(split.(pre1790[:, "amount | 90th"], "."), 1)
pre1790[:, "amount | 90th"] = replace.(pre1790[:, "amount | 90th"], "/" => "")
pre1790.cents = parse.(Float64, pre1790[:, "amount | 90th"]) ./ 100

pre1790.total_amt = pre1790[:, "amount | dollars"] + pre1790[:, "cents"]
pre1790.dollars = pre1790[:, "amount | dollars"]

pre1790.cents = ifelse.(pre1790.cents .>= 100, 0, pre1790.cents)

#clean 
pre1790_clean = clean_df(pre1790)

#group by year and sum 
pre1790_clean.year = coalesce.(pre1790_clean.year, 0)
pre1790_clean.year = Int.(pre1790_clean.year)
pre1790_clean.year = string.(pre1790_clean.year)
pre1790_gdf = group_by_year(pre1790_clean)
pre1790_gdf[1, "year"] = "no year"
sort!(pre1790_gdf)

pre1790_gdf.total_amt = pre1790_gdf.total_amt ./ 1e6 # convert to millions

#plot 
p_bar = bar(pre1790_gdf.year, pre1790_gdf.total_amt, 
    title = "Debt Certificate Total Per Year",
    xlabel = "Year",
    ylabel = "Amount (in million dollars)",
    legend = false,
    background_color = "white",
    yaxis=[0, 30],
    top_margin=5mm,
)

# round to 2 decimal places
pre1790_gdf.total_amt = round.(pre1790_gdf.total_amt, digits=2)
annotate!(pre1790_gdf.year, pre1790_gdf.total_amt, pre1790_gdf.total_amt, annotationfontsizes=8, annotationvalign=:bottom)

savefig(p_bar, "output/analysis/pre1790/debt_per_year/pre1790_debt_certificate_amts_per_year.svg")

#plot 
total_amt = sum(pre1790_gdf.total_amt)
pre1790_gdf.percent = pre1790_gdf.total_amt ./ total_amt

p_bar = bar(pre1790_gdf.year, pre1790_gdf.percent, 
    title = "Percent of Debt Certificate Total Per Year",
    xlabel = "Year",
    ylabel = "Amount (Percentage of Total)",
    legend = false,
    background_color = "white",
    yaxis=[0, 0.5],
    top_margin=5mm
)

# round to 2 decimal places
pre1790_gdf.percent = round.(pre1790_gdf.percent, digits=2)
annotate!(pre1790_gdf.year, pre1790_gdf.percent, pre1790_gdf.percent, annotationfontsizes=8, annotationvalign=:bottom)

savefig(p_bar, "output/analysis/pre1790/debt_per_year/pre1790_debt_certificate_percent_per_year.svg")
