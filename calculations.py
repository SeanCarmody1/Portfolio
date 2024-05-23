import os
import pandas as pd
import datetime
import numpy as np

class Calculations:
    def __init__(self, files):
        self.trips = self.produce_trips_table(files)
        self.daily_counts = self.calculate_daily_counts(self.get_trips())
        self.monthly_counts = self.calculate_monthly_counts(self.get_trips())
    
    def get_trips(self):
        return self.trips

    def get_daily_counts(self):
        return self.daily_counts

    def get_monthly_counts(self):
        return self.monthly_counts

    def produce_trips_table(self, files):
        all_trips = []
        for file in files:
            df = pd.read_csv(file)
            all_trips.append(df)
        trips_df = pd.concat(all_trips, ignore_index=True)
        trips_df['Starttime'] = pd.to_datetime(trips_df['Starttime'])
        trips_df['hour'] = trips_df['Starttime'].dt.hour  
        trips_df['month'] = trips_df['Starttime'].dt.strftime('%m/%Y')  
        print("Columns after adding 'hour':", trips_df.columns)  
        return trips_df  

    
    def calculate_daily_counts(self, trips):
        trips['Starttime'] = pd.to_datetime(trips['Starttime'])
        trips['day'] = trips['Starttime'].dt.strftime('%m/%d/%Y')
        filtered_trips = trips[~trips['From station id'].astype(str).str.contains('BIKE', na=False)]
        filtered_trips = filtered_trips[~filtered_trips['To station id'].astype(str).str.contains('BIKE', na=False)]
        from_counts = filtered_trips.groupby(['day', 'From station id']).size().reset_index(name='fromCNT')
        to_counts = filtered_trips.groupby(['day', 'To station id']).size().reset_index(name='toCNT')
        from_counts.rename(columns={'From station id': 'station_id'}, inplace=True)
        to_counts.rename(columns={'To station id': 'station_id'}, inplace=True)
        daily_counts = pd.merge(from_counts, to_counts, on=['day', 'station_id'], how='outer').fillna(0)
        daily_counts['fromCNT'] = daily_counts['fromCNT'].astype(int)
        daily_counts['toCNT'] = daily_counts['toCNT'].astype(int)
        filtered_trips = filtered_trips.sort_values(['Bikeid', 'Starttime'])
        filtered_trips['prev_to_station'] = filtered_trips.groupby('Bikeid')['To station id'].shift(1)
        filtered_trips['is_rebalancing'] = (filtered_trips['From station id'] != filtered_trips['prev_to_station']).astype(int)
        filtered_trips.loc[filtered_trips.groupby('Bikeid')['Starttime'].idxmin(), 'is_rebalancing'] = 0
        rebal_counts = filtered_trips.groupby(['day', 'From station id'])['is_rebalancing'].sum().reset_index(name='rebalCNT')
        rebal_counts.rename(columns={'From station id': 'station_id'}, inplace=True)
        daily_counts = pd.merge(daily_counts, rebal_counts, on=['day', 'station_id'], how='left').fillna(0)
        daily_counts['rebalCNT'] = daily_counts['rebalCNT'].astype(int)
        daily_counts['station_id'] = daily_counts['station_id'].astype(int)

        return daily_counts[['day', 'station_id', 'fromCNT', 'toCNT', 'rebalCNT']]

    def calculate_monthly_counts(self, trips):
        trips['Starttime'] = pd.to_datetime(trips['Starttime'])
        trips['month'] = trips['Starttime'].dt.strftime('%m/%Y')
        filtered_trips = trips[~trips['From station id'].astype(str).str.contains('BIKE', na=False)]
        filtered_trips = filtered_trips[~filtered_trips['To station id'].astype(str).str.contains('BIKE', na=False)]
        from_counts = filtered_trips.groupby(['month', 'From station id']).size().reset_index(name='fromCNT')
        to_counts = filtered_trips.groupby(['month', 'To station id']).size().reset_index(name='toCNT')
        from_counts.rename(columns={'From station id': 'station_id'}, inplace=True)
        to_counts.rename(columns={'To station id': 'station_id'}, inplace=True)
        monthly_counts = pd.merge(from_counts, to_counts, on=['month', 'station_id'], how='outer').fillna(0)
        monthly_counts['fromCNT'] = monthly_counts['fromCNT'].astype(int)
        monthly_counts['toCNT'] = monthly_counts['toCNT'].astype(int)
        filtered_trips = filtered_trips.sort_values(['Bikeid', 'Starttime'])
        filtered_trips['prev_to_station'] = filtered_trips.groupby('Bikeid')['To station id'].shift(1)
        filtered_trips['is_rebalancing'] = (filtered_trips['From station id'] != filtered_trips['prev_to_station']).astype(int)
        filtered_trips.loc[filtered_trips.groupby('Bikeid')['Starttime'].idxmin(), 'is_rebalancing'] = 0
        rebal_counts = filtered_trips.groupby(['month', 'From station id'])['is_rebalancing'].sum().reset_index(name='rebalCNT')
        rebal_counts.rename(columns={'From station id': 'station_id'}, inplace=True)
        monthly_counts = pd.merge(monthly_counts, rebal_counts, on=['month', 'station_id'], how='left').fillna(0)
        monthly_counts['rebalCNT'] = monthly_counts['rebalCNT'].astype(int)
        monthly_counts['station_id'] = monthly_counts['station_id'].astype(int)
        return monthly_counts[['month', 'station_id', 'fromCNT', 'toCNT', 'rebalCNT']]


        
if __name__ == "__main__":
    calculations = Calculations(['HealthyRideRentals2021-Q1.csv', 'HealthyRideRentals2021-Q2.csv', 'HealthyRideRentals2021-Q3.csv'])
    print("-------------- Trips Table ---------------")
    print(calculations.get_trips().head(10))
    print()
    print("-------------- Daily Counts ---------------")
    print(calculations.get_daily_counts().head(10))
    print()
    print("------------- Monthly Counts---------------")
    print(calculations.get_monthly_counts().head(10))
    print()