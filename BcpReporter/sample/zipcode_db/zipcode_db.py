import pandas as pd
import os
from collections import namedtuple

ZipcodeInfo = namedtuple("ZipcodeInfo", ["postal_code", "latitude", "longitude"])

class ZipcodeDB:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path, dtype={"postal_code": str})
        else:
            self.df = pd.DataFrame(columns=["postal_code", "latitude", "longitude"])
    
    def save(self):
        self.df.to_csv(self.csv_path, index=False, encoding="utf-8")

    def add_or_update(self, postal_code, latitude, longitude):
        if postal_code in self.df["postal_code"].values:
            self.df.loc[self.df["postal_code"] == postal_code, ["latitude", "longitude"]] = [latitude, longitude]
        else:
            new_row = pd.DataFrame([{
                "postal_code": postal_code,
                "latitude": latitude,
                "longitude": longitude
            }])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save()

    def get(self, postal_code):
        result = self.df[self.df["postal_code"] == postal_code]
        if not result.empty:
            row = result.iloc[0]
            return ZipcodeInfo(postal_code=row["postal_code"], latitude=row["latitude"], longitude=row["longitude"])
        return None

    def remove(self, postal_code):
        self.df = self.df[self.df["postal_code"] != postal_code]
        self.save()

    def list_all(self):
        return self.df.copy()
