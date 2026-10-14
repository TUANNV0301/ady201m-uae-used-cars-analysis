# SQLite database

`uae_used_cars.db` is generated from `data/raw/uae_used_cars_10k.csv` by `scripts/database/database_setup.py`.

## Tables

- `car_listing`: one row per listing; contains year, price AED, mileage, vehicle descriptors and foreign keys.
- `make`, `body_type`, `emirate`: normalized lookup dimensions.

Foreign keys connect each listing to its make, body type and emirate. Indexes support filtering on year, price and mileage. `Cylinders` is nullable because 155 values are missing/unknown after normalization.

Run `schema.sql` for DDL and `queries.sql` for example analytical queries. The Python notebook connects through `sqlite3` and reads grouped results with pandas.
