import csv
import pandas as pd
import sqlite3

def main():
    conn = sqlite3.connect('./used_cars.db')
    c = conn.cursor()
    _init_db(conn)
    insert_data(conn)
    
def clean(make_file=False):
    df = pd.read_csv(r'./data/data_engineering_dataset.csv', names = ['VIN', 'CarYear', 'Color', 'VehBody', 'EngineType', 'Make', 'Miles', 'Odometer','Brand', 'VehType', 'LocationNum', 'CarType', 'EngineLiters','FuelType', 'Transmission', 'SaleLoc', 'PurchVal'], skiprows = 1)

    #Remove first set of duplicate data
    cleaned_df = df.drop(df.index[0:11387])
    #Reset index
    cleaned_df.reset_index(inplace=True, drop=True)
    #Remove second set of duplicated data
    cleaned_df = cleaned_df.drop(df.index[11387:11394])
    #Reset index
    cleaned_df.reset_index(inplace=True, drop=True)
    cleaned_df.head()

    cleaned_df['Color'] = cleaned_df['Color'].str.upper()
    cleaned_df['VIN'] = cleaned_df['VIN'].str.upper()
    cleaned_df['Make'] = cleaned_df['Make'].str.rstrip()
    cleaned_df['EngineLiters'] = cleaned_df['EngineLiters'].str.strip('L')

    if make_file:
        cleaned_df.to_csv('./data/data_engineering_dataset_cleaned.csv', index=False)
    return cleaned_df
    
def _init_db(conn):
    
    c = conn.cursor()
    
    c.execute('''DROP TABLE IF EXISTS vehicle''')
    c.execute('''DROP TABLE IF EXISTS sale''')
    c.execute('''DROP TABLE IF EXISTS store''')
    
    # Create table - VEHICLE
    c.execute('''CREATE TABLE vehicle 
                 ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [VIN] text not null unique, [CarYear] integer, [Color] text, [Make] text, [VehBody] text, [EngineType] text, [EngineLiters] integer, [CarType] text, [Brand] text, [VehType] text, [FuelType] text, [Transmission] text)''')
              
    # Create table - SALE
    c.execute('''CREATE TABLE sale
                 ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [VIN] text, [LocationNum] integer, [Vehicle_id] integer, [Store_id] integer, [SaleLoc] integer, [Odometer] text, [PurchVal] integer, [ColorSold] text)''')
            
    # Create table - STORE
    c.execute('''CREATE TABLE store
             ([id] INTEGER PRIMARY KEY AUTOINCREMENT, [LocationNum] integer not null unique)''')
    
    conn.commit()
    c.close()
    
def insert_data(conn):
    
    c= conn.cursor()

    df = clean()
    vehicles_df = df[['VIN', 'CarYear', 'Color', 'Make', 'VehBody', 'EngineType', 'Make', 'Brand', 'VehType', 'EngineLiters', 'FuelType', 'Transmission', 'CarType']]
    vehicles_df.drop_duplicates(subset='VIN', inplace = True)
    vehicles_df.to_sql('vehicle', conn, if_exists='append', index=False)
    
    stores_df = df[['LocationNum']]
    stores_df.drop_duplicates(subset='LocationNum', inplace=True)
    stores_df.sort_values(by=['LocationNum'], inplace = True)
    stores_df.to_sql('store', conn, if_exists='append', index=False)
    
    sales_df = df[['VIN', 'LocationNum', 'SaleLoc', 'Odometer', 'PurchVal', 'Color']]
    sales_df.rename(columns = {'Color' : 'ColorSold'}, inplace = True)
    sales_df.to_sql('sale', conn, if_exists='append', index=False)
    
    c.execute('''UPDATE sale SET Vehicle_id = (SELECT id FROM vehicle WHERE sale.VIN = vehicle.VIN);
                     ''')
    conn.commit()
    c.execute('''UPDATE sale SET Store_id = (SELECT id FROM store WHERE sale.LocationNum = store.LocationNum);
                     ''')
    conn.commit()
    c.executescript('''BEGIN TRANSACTION;
                    CREATE TEMPORARY TABLE sale_backup(id, Vehicle_id, Store_id, SaleLoc, Odometer, PurchVal, ColorSold);
                    INSERT INTO sale_backup SELECT id, Vehicle_id, Store_id, SaleLoc, Odometer, PurchVal, ColorSold FROM sale;
                    DROP TABLE sale;
                    CREATE TABLE sale(id INTEGER PRIMARY KEY AUTOINCREMENT, Vehicle_id integer, Store_id integer, SaleLoc integer, Odometer text, PurchVal integer, ColorSold text);
                    INSERT INTO sale SELECT id, Vehicle_id, Store_id, SaleLoc, Odometer, PurchVal, ColorSold FROM sale_backup;
                    DROP TABLE sale_backup;
                    COMMIT;''')
    
    
if __name__ == "__main__":
    clean(True)