How we assigned seating at our wedding

Usage below:

```
import Seater
import pandas as pd

guest_list = pd.read_csv(<file>)

table_numbers, seats_available = [i for i in range(1,14)], [6,8,8,8,13,12,8,8,8,8,8,8,6]
tables = Seater._run(guest_list,table_numbers,seats_available)
Seater.convert_tables_to_df(tables)
```