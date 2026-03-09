using VegaLite, VegaDatasets

us10m = dataset("us-10m")

p = @vlplot(
    width = 640, 
    height = 360, 
    title = "US Map by county",
    projection = {type="albersUsa"},
    data = {
        values = us10m,
        format = {
            type = :topojson, 
            feature = :counties 
        }
    },
    mark = {
        type = :geoshape,
        fill = :lightgray,
        stroke = :white
    }
)

save("p_us_states.svg", p)

canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "map of texas",
    projection = {type="albersUsa"},
)

st_map = @vlplot(
    data = {
        values = us10m,
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    transform = [
        {filter = {field = :id, equal = "2"}}
    ],
    mark = {
        type = :geoshape,
        fill = :lightgray,
        stroke = :white
    }
)

p = canvas + st_map 


capitals = dataset("us-state-capitals")

canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "map of texas",
    projection = {type="albersUsa"},
)

usmap = @vlplot(
    data = {
        values = us10m,
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    mark = {
        type = :geoshape,
        fill = :lightgray,
        stroke = :white
    }
)

capitalmap = @vlplot(
    data = capitals, 
    mark = :circle, 
    latitude = "lat:q",
    longitude = "lon:q",
    color = {value = :red} 
)

capitalnames = @vlplot(
    data = capitals, 
    mark = {
        type = :text,
        dy = 8,
        fontSize = 6 
    }, 
    latitude = "lat:q",
    longitude = "lon:q",
    text = "city:n",
) 


p = canvas + usmap + capitalmap + capitalnames



unemployment = dataset("unemployment") 
vscodedisplay(unemployment) 

canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "unemployment",
    projection = {type="albersUsa"},
)

usmap = @vlplot(
    data = {
        values = us10m, 
        format = {
            type = :topojson, 
            feature = :counties 
        }
    }, 
    transform = [
        {
            lookup = :id, 
            from = {
                data = unemployment, 
                key = :id, 
                fields = [:rate]
            }
        }
    ], 
    mark = :geoshape,
    color = "rate:q" 
)

p = canvas + usmap 

world110m = dataset("world-110m")
canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "world map by country",
    projection = {type=:equalEarth}
)

worldmap = @vlplot(
    data = {
        values = world110m, 
        format = {
            type = :topojson, 
            feature = :countries 
        }
    }, 
    mark = {type = :geoshape, fill = :lightgray, stroke = :white},
    color = {value = :lightgray} 
)

p = canvas + worldmap

using DataFrames, CSV, DataFramesMeta 

# import pre-1790 debt data 
pre1790 = DataFrame(CSV.File("output/derived/pre1790/pre1790_cleaned.csv"))

# clean cents column and sum dollars and cents 
pre1790[:, "amount | 90th"] = getindex.(split.(pre1790[:, "amount | 90th"], "."), 1)
pre1790[:, "amount | 90th"] = replace.(pre1790[:, "amount | 90th"], "/" => "")
pre1790.cents = parse.(Float64, pre1790[:, "amount | 90th"]) ./ 100
pre1790.cents = ifelse.(pre1790.cents .>= 100, 0, pre1790.cents)
pre1790.total_amt = pre1790[:, "amount | dollars"] + pre1790[:, "cents"]
pre1790.dollars = pre1790[:, "amount | dollars"]

# create new dataframe only states and total amount 
select_headers = ["state", "total_amt"]
dropmissing!(pre1790, :state) # remove rows with missing states 
pre1790_states = select(pre1790, select_headers)

# group by state and sum total amount 
pre1790_states = @by(pre1790_states, :state, :total_amt = sum(:total_amt))

# drop cs and f 
pre1790_states = filter(row -> row.state != "cs" && row.state != "f", pre1790_states)
# add numeric code for each state 
pre1790_states.id = [33, 34, 36, 25, 10, 9, 51, 42, 24, 37, 13, 44] 
pre1790_states 


canvas_d = @vlplot(
    width = 640, 
    height = 360, 
    title = "Pre-1790 Debt By State (in dollars)",
    projection = {type="albersUsa"} 
)

usmap_d = @vlplot(
    data = {
        values = us10m, 
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    transform = [
        {
            lookup = :id, 
            from = {
                data = pre1790_states, 
                key = :id, 
                fields = [:total_amt]
            }
        }
    ], 
    mark = :geoshape,
    color = "total_amt:q" 
)

p_d = canvas_d + usmap_d  

# save
save("output/analysis/pre1790/p_pre1790_dollars.svg", p_d)

# map of states by percentage 
pre1790_states.percentage = pre1790_states.total_amt ./ sum(pre1790_states.total_amt) * 100

canvas_p = @vlplot(
    width = 640, 
    height = 360, 
    title = "Pre-1790 Debt By State (in percentage)",
    projection = {type="albersUsa"} 
)

usmap_p = @vlplot(
    data = {
        values = us10m, 
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    transform = [
        {
            lookup = :id, 
            from = {
                data = pre1790_states, 
                key = :id, 
                fields = [:percentage]
            }
        }
    ], 
    mark = :geoshape,
    color = "percentage:q" 
)

p_p = canvas_p + usmap_p

# save 
save("output/analysis/pre1790/p_pre1790_per.svg", p_p)

# compare to post-1790 debt data 
post1790 = DataFrame(CSV.File("output/derived/post1790_cd/final_data_CD.csv"))

# group by state and sum 
post1790_states = @by(post1790, "Group State", :total_amt = sum(:final_total_adj))
dropmissing!(post1790_states, "Group State") # remove rows with missing states

# add numeric code for each state
post1790_states.id = [36, 44, 9, 33, 34, 24, 45, 42, 13, 25, 37, 10, 51, 50]

# graph 
canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "Post-1790 Debt By State",
    projection = {type="albersUsa"} 
)

usmap = @vlplot(
    data = {
        values = us10m, 
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    transform = [
        {
            lookup = :id, 
            from = {
                data = post1790_states, 
                key = :id, 
                fields = [:total_amt]
            },
        }
    ], 
    mark = :geoshape,
    color = "total_amt:q"
)

p_post = canvas + usmap 


save("output/analysis/pre1790/p_post1790.svg", p_post)

minimum(post1790_states.total_amt)

using XLSX 

pierce_certs_org = DataFrame(XLSX.readtable("source/raw/pre1790/orig/Pierce_Certs_cleaned_2019.xlsx", "Pierce_Certs_cleaned_2019"))
# keep state and value columns 
pierce_certs = select(pierce_certs_org, ["State", "Value"])
# drop missing states
dropmissing!(pierce_certs, :State)
# replace missing values with 0 
pierce_certs.Value = coalesce.(pierce_certs.Value, 0)
# remove cs and f 
pierce_certs = filter(row -> row.State != "CS" && row.State != "F", pierce_certs)

# group by state and sum value 
pierce_certs_gdf = @by(pierce_certs, :State, :Value = sum(:Value))
sort!(pierce_certs_gdf, :Value, rev = true) # sort by value descending

# add numeric code for each state
pierce_certs_gdf.id = [25, 42, 9, 36, 51, 24, 34, 33, 37, 10, 13, 44]
pierce_certs_gdf

canvas = @vlplot(
    width = 640, 
    height = 360, 
    title = "Pierce Certificates by State",
    projection = {type="albersUsa"} 
)

usmap = @vlplot(
    data = {
        values = us10m, 
        format = {
            type = :topojson, 
            feature = :states 
        }
    }, 
    transform = [
        {
            lookup = :id, 
            from = {
                data = pierce_certs_gdf, 
                key = :id, 
                fields = [:Value]
            }
        }
    ], 
    mark = :geoshape,
    color = "Value:q" 
)

p = canvas + usmap 

save("output/analysis/pre1790/pierce/p_pierce_certs.png", p)

pierce_certs_org.Value = coalesce.(pierce_certs_org.Value, 0)
pierce_certs_reg = @by(pierce_certs_org, "To Whom Issued", :Value = sum(:Value), :Group = first(:Group), :State = first(:State))

pierce_certs_reg.regiment = pierce_certs_reg[:, "To Whom Issued"]
pierce_certs_reg = @by(pierce_certs_reg, "Group", :Value = sum(:Value), :regiment = first(:regiment), :State = first(:State))
# remove semi-colon 
pierce_certs_reg.regiment = replace.(pierce_certs_reg.regiment, ";" => ":")

# create new column of percent owned 
pierce_certs_reg.percent_owned = (pierce_certs_reg.Value ./ sum(pierce_certs_reg.Value)) * 100

sort!(pierce_certs_reg, :Value, rev = true) # sort by value descending

# save 
CSV.write("output/analysis/pre1790/pierce/pierce_certs_reg.csv", pierce_certs_reg)

# graph percent owned by regiment 
