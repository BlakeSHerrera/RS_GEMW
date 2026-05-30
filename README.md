# RuneScape Grand Exchange Market Watch

This project demonstrates use of industry-standard tools and best practices in data engineering.

## Technologies Used

This project uses:

- **Docker** for environment isolation
- **Python** and **dlt** for ingestion
- **SQL** and **dbt** for transformations
- **duckdb** as a storage engine.
- **pytest** and **dbt** for testing.

Things I would like to add:

- Basic orchestration via **Prefect** or **Airflow**.
- Tests integrated into **CI/CD**.

However, this project is not big enough to justify the time to put into these. I don't plan to expand on this project more.

## Project Structure

Data environments are isolated on the database level. Raw data is written to a raw database, while analytics is written to dev or prod databases. Python environments are managed with venv. Other environment variables are managed with a .env file.

## Facts and Dims

Tables are not explicitly labeled with fact or dim prefixes. Instead, I use an intuitive naming convention. Fact tables have signaling keywords that correspond to the type of Kimball fact table that they are; the words summary or snapshot correspond to Kimball snapshot fact tables, along with a word describing the grain such as daily or monthly. I would use a word like lifetime to denote an accumulating snapshot fact table, to indicate that the table structure is conducive to the lifecycle of a particular process. Finally, words such as transaction or event denote transaction fact tables. As you can see, dimensions have no special rules; they are often just plain nouns.

By placing the grain rules in the name, it makes it easier to see when something is going wrong. For example, if I had named the tables active_players and exchanges, then it is not obvious that joining them is mixing a daily grain with a weekly grain. Furthermore, by denoting it as a snapshot, it's clear that these are point-in-time measurements and therefore atomic data. It is also important to have good naming and metadata for the same reason.

Whether a table is a fact or a dimension is sometimes context-dependent. For example, the event table could be seen as a transaction fact table, but it can also fit into a dimensional model a s an outrigger to the date dimension. It can also simply be a disconnected reference table that is neither fact nor dim. Overall, it is less confusing to not draw tight boxes around naming.

## Notes

There is only volume data for 2023 exchanges and on.

Player counts and events pulled from inspecting https://www.ely.gg/rs_playercounts. The number of active players at any given time fluctuates. The curve of players at any given time follows a sinusoid pattern (https://www.misplaceditems.com/rs_tools/graph/). At the lowest is about 13.5k players and at the peak is 40k players. The given measurements from the website seem to fall short of the mean at 20k players, and an adjustment of about 25% brings it closer to average. This value more or less describes the "workforce" rather than number of people playing, since multiplying by 24 gives you the number of man-hours of gameplay. An average user's session is 3-4 hours based on market research.

## Lessons Learned

Docker requires extra configuration to work on Network Attached Storage devices mapped to a drive letter. This is because the wsl backend does not have the same mappings or credentials that the user does. Initially I did not realize my bind mounting was failing because it defaulted to run without the attached mount rather than generating any error. A special option had to be set to raise an error if the mount failed.

dbt's environment management is lacking. When a new model is created, the options are to either replicate the entire environment, wasting compute resources while everything is copied over, or to only initialize the changed model with everything else blank. References can defer to prod, but this means incremental models must do a costly full load. BI tools would not be able to connect for QA. Modern tools such as Snowflake's zero-copy cloning or SQLMesh's virtual data environmnets handle this.

Additionally, dbt treats everything as text rather than natively understanding SQL. That means that simple syntax errors won't be caught until models are actually running. The exchange summary table took about 30 seconds to run and it was annoying to realize I forgot a comma in the next model. I had to wait 30 seconds to realize these trivial errors, which is not scalable for larger workflows. There is an option to select a single model, but again this is less feasible when you have several to run. It will slow down a CI/CD process.

Metadata tends to live in disparate files for dbt, making it harder to maintain and track everything.
