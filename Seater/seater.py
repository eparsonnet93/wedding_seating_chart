import pandas as pd
import numpy as np


__all__ = ('_table', 'assign_seats', 'convert_tables_to_df', '_run')

class _table():
    
    def __init__(self, number, n):
        self.available_seats = n
        self.orig_available_seats = n
        self.number = number
        self.seating_chart = set()
        return
    
    def add_group(self, group:set):
        if len(group)<=self.available_seats:
            self.seating_chart = self.seating_chart.union(group)
            self.available_seats = self.orig_available_seats - len(self.seating_chart)
        else:
            raise ValueError('Not enough seats at this table')

    def __repr__(self):
        return 'Table ' + str(self.number) + ': ' +self.seating_chart.__repr__()

    
def assign_seats(guest_list:'DataFrame', tables:list, family_first:bool=False, family_table_index=None):
    
    if type(family_table_index) == type(None): # used to assign families to a smaller number of tables, if preferred
        family_table_index = [i for i in range(len(tables))]
    
    groups = dict()

    for i in range(len(guest_list)):
        row = guest_list.iloc[i]
        groupn = row.Groups
        if groupn in groups.keys():
            groups[groupn].add(row['First, last'])
        else:
            groups.update({groupn:set([row['First, last']])})

    group_names_list = list(groups.keys())
    group_names_list.remove('a1') # wedding party
    group_names_list = np.random.choice(group_names_list,size=len(group_names_list)) # randomize order of placement to avoid any bias
    group_names_list = np.concatenate((['a1'], group_names_list)) # put wedding party back first
    
    gnl_fam, gnl_friend = [],[]
    
    if family_first:
        for gn in group_names_list:
            if 'a' in gn:
                gnl_fam.append(gn)
            else:
                gnl_friend.append(gn)
        group_names_list = np.concatenate((gnl_fam, gnl_friend))

    for group_n in groups:
        group = groups[group_n]
        if family_first and 'a' in group_n:
            family_tables = []
            for index in family_table_index:
                family_tables.append(tables[index])
            random_table_order = np.random.choice(family_tables, len(family_tables))
        else:
            random_table_order = np.random.choice(tables, len(tables))
        success = False
        for ix, table in enumerate(random_table_order):
            if success:
                continue
            try:
                table.add_group(group)
                success = True
            except ValueError:
                continue
        if not success:
            raise ValueError('Unable to match. Please try again')

    return tables

def convert_tables_to_df(tables):
    out = dict()
    for table in tables:
        out.update({table.number:list(table.seating_chart)})

    max_len = max(len(v) for v in out.values())
    padded_data = {k: v + [np.nan] * (max_len - len(v)) for k, v in out.items()}
    return pd.DataFrame(padded_data)

def _run(guest_list, table_numbers:list, seats_available:list, 
         family_first=False, family_table_index=None, max_attempts=100):
    success = False
    attempts = 0
    while not success:
        try:
            tables = [_table(a,b) for a,b in zip(table_numbers, seats_available)]
            tables = assign_seats(
                guest_list, tables, family_first=family_first, family_table_index=family_table_index
            )
            success=True
        except ValueError:
            attempts += 1
            if attempts > max_attempts:
                break
            continue
    if not success:
        raise ValueError('unable to find a solution')
    return tables