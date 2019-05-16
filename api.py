import flask
from flask import request, jsonify
import sqlite3
import db

app = flask.Flask(__name__)
app.config["DEBUG"] = True
	
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Car Sales Data</h1>
<p>A prototype API for used car sales data.</p>'''

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

################################################################################
################################################################################
####                               `GET` OPERATIONS                               ####
################################################################################
################################################################################
	
@app.route('/api/v1/resources/sales/all', methods=['GET'])
def sales_all():
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('SELECT * FROM sale;').fetchall()

    return jsonify(all)
	
@app.route('/api/v1/resources/vehicles/all', methods=['GET'])
def vehicles_all():
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('SELECT * FROM vehicle;').fetchall()

    return jsonify(all)
		
@app.route('/api/v1/resources/stores/all', methods=['GET'])
def stores_all():
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('SELECT * FROM store;').fetchall()

    return jsonify(all)
	
@app.route('/api/v1/resources/vehicles_sold/all', methods=['GET'])
def vehicles_sold_all():
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('''SELECT sale.id, sale.SaleLoc, sale.Odometer, sale.PurchVal, 
                            sale.ColorSold, vehicle.VIN, vehicle.CarYear, vehicle.CarType, vehicle.Color as VehicleColor,
                            vehicle.EngineLiters, vehicle.EngineType, vehicle.FuelType,
                            vehicle.Make, vehicle.Transmission, vehicle.Brand, vehicle.VehBody, 
                            vehicle.VehType, store.LocationNum
                            FROM sale
                            LEFT JOIN vehicle on sale.Vehicle_id = vehicle.id
                            LEFT JOIN store on sale.Store_id = store.id;''').fetchall()

    return jsonify(all)

@app.route('/api/v1/resources/sales', methods=['GET'])
def sales_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    print(id)
    purch_val = query_parameters.get('purch_val')
    sale_loc = query_parameters.get('sale_loc')

    query = "SELECT * FROM sale WHERE"
    to_filter = []

    if id:
        query += ' id=' + id + ' AND'
    if purch_val:
        query += ' PurchVal=? AND'
        to_filter.append(purch_val)
    if sale_loc:
        query += ' SaleLoc=' + sale_loc + ' AND'
    if not (id or purch_val or sale_loc):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('used_cars.db')
    conn.set_trace_callback(print)
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

@app.route('/api/v1/resources/sales/count/by_store', methods=['GET'])
def sales_count_by_store():
    
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('''SELECT SaleLoc, COUNT(Vehicle_id) as Vehicles_Sold
                                FROM sale
                                GROUP BY SaleLoc
                                ORDER BY Vehicles_Sold DESC;''').fetchall()

    return jsonify(all)
    
@app.route('/api/v1/resources/sales/average/purchase_by_store', methods=['GET'])
def purchase_average_by_store():
    
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('''SELECT AVG(PurchVal) as Purchase_Average, SaleLoc
                                FROM sale
                                GROUP BY SaleLoc
                                ORDER BY Purchase_Average DESC;''').fetchall()

    return jsonify(all)
    
@app.route('/api/v1/resources/vehicles_sold/count/by_brand', methods=['GET'])
def vehicles_sold_by_brand():
    
    conn = sqlite3.connect('used_cars.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all = cur.execute('''SELECT Brand, COUNT(Brand) as Number_Sold
                                FROM sale
                                LEFT JOIN vehicle ON sale.Vehicle_id = vehicle.id
                                GROUP BY Brand
                                ORDER BY Number_Sold DESC;''').fetchall()

    return jsonify(all)
           	
################################################################################
################################################################################
####                              `POST` OPERATIONS                                ####
################################################################################
################################################################################

@app.route('/api/v1/resources/sales/insert', methods=['POST'])
def sale_insert():
    query_parameters = request.args

    vin = query_parameters.get('vin')
    location_num = query_parameters.get('location_num')
    vehicle_id = vehicle_id_lookup(vin)
    if vehicle_id is None:
        return 'Invalid VIN, vehicle not found in the database.'
    store_id = store_id_lookup(location_num)
    if store_id is None:
        return 'Invalid Location Number, sales location not found in the database.'
    sale_loc = query_parameters.get('sale_loc')
    odometer = query_parameters.get('odometer')
    purch_val = query_parameters.get('purch_val')
    color_sold = query_parameters.get('color_sold')

    query = '''INSERT INTO sale (Vehicle_id, Store_id, SaleLoc, Odometer, PurchVal, ColorSold)
    VALUES (?, ?, ?, ?, ?, ?);'''
    to_insert = [vehicle_id, store_id, sale_loc, odometer, purch_val, color_sold]

    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    cur.execute(query, to_insert)
    conn.commit()
    id = cur.lastrowid
    cur.close()
    
    return f'Record {id} successfully inserted!'
	
@app.route('/api/v1/resources/vehicles/insert', methods=['POST'])
def vehicle_insert():
    query_parameters = request.args

    vin = query_parameters.get('vin')
    car_year = query_parameters.get('car_year')
    color = query_parameters.get('color').upper()
    make = query_parameters.get('make').upper()
    veh_body = query_parameters.get('veh_body')
    engine_type = query_parameters.get('engine_type')
    engine_liters = query_parameters.get('engine_liters')
    car_type = query_parameters.get('car_type')
    brand = query_parameters.get('brand').upper()
    veh_type = query_parameters.get('veh_type')
    fuel_type = query_parameters.get('fuel_type')
    transmission = query_parameters.get('transmission')
    
    query = '''INSERT INTO vehicle (VIN, CarYear, Color, Make, VehBody, EngineType, EngineLiters, CarType, Brand, VehType, FuelType, Transmission)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
    to_insert = [vin, car_year, color, make, veh_body, engine_type, engine_liters, car_type, brand, veh_type, fuel_type, transmission]

    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    try :
        cur.execute(query, to_insert)
        conn.commit()
    except: 
        return 'Insertion of vehicle record failed.'
    id = cur.lastrowid
    cur.close()
    
    return f'Record {id} successfully inserted!'
		
@app.route('/api/v1/resources/stores/insert', methods=['POST'])
def store_insert():
    query_parameters = request.args

    location_num = query_parameters.get('location_num')
    
    query = '''INSERT INTO store (LocationNum)
    VALUES (?);'''
    to_insert = [location_num]

    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    try :
        cur.execute(query, to_insert)
        conn.commit()
    except: 
        return 'Insertion of store record failed.'
    id = cur.lastrowid
    cur.close()
    
    return f'Record {id} successfully inserted!'

################################################################################
################################################################################
####                              `PUT` OPERATIONS                             ####
################################################################################
################################################################################

@app.route('/api/v1/resources/sales/update', methods=['PUT'])
def sale_update():
    query_parameters = request.args
    
    id = query_parameters.get('id')
    if id is None:
        return 'Must specify an id to update.'
    sale_loc = query_parameters.get('sale_loc')
    odometer = query_parameters.get('odometer')
    purch_val = query_parameters.get('purch_val')
    color_sold = query_parameters.get('color_sold')

    query = '''UPDATE sale SET SaleLoc=:sale_loc, Odometer=:odometer, PurchVal=:purch_val, ColorSold=:color_sold where id=:id;'''
    to_update = {'id' : id,
                        'sale_loc' : sale_loc,
                        'odometer' : odometer,
                        'purch_val' : purch_val,
                        'color_sold' : color_sold
                        }
                        
    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    cur.execute(query, to_update)
    conn.commit()
    id = cur.lastrowid
    cur.close()
    
    return f'Record {id} successfully updated!'
	
@app.route('/api/v1/resources/vehicles/update', methods=['PUT'])
def vehicle_update():
    query_parameters = request.args
    
    id = query_parameters.get('id')
    if id is None:
        return 'Must specify an id to update.'
    car_year = query_parameters.get('car_year')
    color = query_parameters.get('color').upper()
    make = query_parameters.get('make').upper()
    veh_body = query_parameters.get('veh_body')
    engine_type = query_parameters.get('engine_type')
    engine_liters = query_parameters.get('engine_liters')
    car_type = query_parameters.get('car_type')
    brand = query_parameters.get('brand').upper()
    veh_type = query_parameters.get('veh_type')
    fuel_type = query_parameters.get('fuel_type')
    transmission = query_parameters.get('transmission')

    query = '''UPDATE vehicle SET CarYear=:car_year, Color=:color, Make=:make, VehBody=:veh_body,
                   EngineType=:engine_type, EngineLiters=:engine_liters, CarType=:car_type, Brand=:brand,
                   VehType=:veh_type, FuelType=:fuel_type, Transmission=:transmission where id=:id;'''
    
    to_update = {'id' : id,
                        'car_year' : car_year,
                        'color' : color,
                        'make' : make,
                        'veh_body' : veh_body,
                        'engine_type' : engine_type,
                        'engine_liters' : engine_liters,
                        'car_type' : car_type,
                        'brand' : brand,
                        'veh_type' : veh_type,
                        'fuel_type' : fuel_type,
                        'transmission' : transmission
                        }
                        
    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    cur.execute(query, to_update)
    conn.commit()
    id = cur.lastrowid
    cur.close()
    
    return f'Record {id} successfully updated!'
		    
################################################################################
################################################################################
####                              `DELETE` OPERATIONS                              ####
################################################################################
################################################################################

@app.route('/api/v1/resources/sales/delete', methods=['DELETE'])
def sale_delete():
    query_parameters = request.args
    
    id = query_parameters.get('id')
    if id is None:
        return 'Must specify an id for a row to delete.'

    query = 'DELETE FROM sale WHERE id=' + id + ';'

    conn = sqlite3.connect('used_cars.db')
    cur = conn.cursor()
    try: 
        cur.execute(query)
    except:
        return 'Given id not found in table.'
    conn.commit()
    cur.close()
    
    return f'Record {id} successfully deleted!'

################################################################################
################################################################################
####                              HELPER FXNS                              ####
################################################################################
################################################################################

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        
    return d

def vehicle_id_lookup(vin):
    conn = sqlite3.connect('used_cars.db')
    conn.set_trace_callback(print)
    cur = conn.cursor()
    query = 'SELECT id FROM vehicle WHERE VIN = ?;'
    v = (vin,)
    r = cur.execute(query, v).fetchone()
    cur.close()
    
    if r is not None:
        return int(r[0])
    else:
        return None
    
def store_id_lookup(location_num):
    conn = sqlite3.connect('used_cars.db')
    conn.set_trace_callback(print)
    cur = conn.cursor()
    query = 'SELECT id FROM store WHERE LocationNum = ?;'
    location = (location_num,)
    r = cur.execute(query, location).fetchone()
    cur.close()
    
    if r is not None:
        return int(r[0])
    else:
        return None
    

if __name__ == '__main__':
    try: 
        conn = sqlite3.connect('file:used_cars.db?mode=rw', uri=True)
    except:
        db.create_db()
    app.run()