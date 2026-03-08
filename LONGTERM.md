## DATA
1. No cleaning pipeline exists for assumed state debt data yet. The pipeline should mirror the post-1790 continental debt pipeline structure.
2. Incorporate Society of the Cincinnati membership as a variable in analyses. The Society of the Cincinnati was an organization of Revolutionary War officers founded in 1783; membership may correlate with delegate debt holdings or voting behavior. Use the Wikipedia list of original members as the data source: https://en.wikipedia.org/wiki/List_of_original_members_of_the_Society_of_the_Cincinnati
3. I want to improve raw name parsing to account for both the executors, and the person who they are executing on behalf of. The steps roughly follow as such
  - Necessary files in `source/raw/pre1790/corrections` and `source/raw/post1790/corrections` should be amended
  - Downstream code in `source/derived` should be updated to distinguish between executors and original owners

## ARCHITECTURE