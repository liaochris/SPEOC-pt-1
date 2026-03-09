## Data

1. No cleaning pipeline exists for assumed state debt data yet. The pipeline should mirror the post-1790 continental debt pipeline structure.
2. Incorporate Society of the Cincinnati membership as a variable in analyses. The Society of the Cincinnati was an organization of Revolutionary War officers founded in 1783; membership may correlate with delegate debt holdings or voting behavior. Use the Wikipedia list of original members as the data source: https://en.wikipedia.org/wiki/List_of_original_members_of_the_Society_of_the_Cincinnati
3. I want to improve raw name parsing to account for both the executors, and the person who they are executing on behalf of. The steps roughly follow as such
  - Amend relevant files in `source/raw/pre1790/corrections` and `source/raw/post1790/corrections` 
  - Distinguish between executors and original owners in  `source/derived` downstream code
4. I want to provide more detailed instructions on all the raw data in my dataset 
  - there should be `docs` folder with documentation the raw data
  - there should be a 
5. Reduce reundancy
  - Can I consolidate stateshape_1790 and nhgis_state_1790

## Cleaning

1. One aspect of the cleaning process is to aggregate names that may be similar. This is done with the `pre1790` and `post1790` data. I think there are a few aspects of this that could be cleaner
  - I think that the aggregation should be done `postscrape`, once we have more information about how different names might map to the same identity in a census database. This is done `postscrape` for the `post1790_cd` data but `prescrape` (in part) for the `pre1790` data, see `source/derived/prescrape/pre1790/find_similar_names.py`
  - I think we should also use a principled way of determining when two names spelled differently correspond to the same person. Right now, we adopt a mix of a) fuzzy matching, b) manual work, and c) reliance on the census data. This principled way should also be applied in the same way to the `pre1790` and `post1790` data. 
2. Another aspect of the cleaning process is to separate text descriptions of debtholders into the names of the debtholder within that text. I think it would be helpful, for ease of understanding how the data is cleaned, to standardize the corrections made (if possible). 
  - From the list of all names, see which ones are "suspicious" names that don't seem like names but could become names (if you remove extraneous text or separate out other names for example), and update the relevant file in source/raw/pre1790/corrections to turn the "suspicious" names into actual names



## Architecture


