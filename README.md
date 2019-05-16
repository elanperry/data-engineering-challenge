# Data Engineering Code Challenge

## My Solution

The API was made using Python and Flask and a SQLite database. Since the intended userbase for the API is other developers, the front end is very basic and interaction is conducted through REQUESTS. This sets up a framework for which developers can fetch JSON formatted data from the database and utilize it in their own applications. 

### Installation

#### Docker

To deploy the app to a docker container first build the image using:

`sudo docker build -t used-cars-api:latest .`

You can then deply a container with:

`sudo docker run --net host -p 5000:5000 used-cars-api`

From here you should be able to navigate to `localhost:5000` if working correctly, you will see a landing page with "Used Car Sales Data" at the top.

#### If not using Docker

You will need python3 installed on your system, install dependencies using `pip install -r requirements.txt` and launch the app through `api.py`

From here you should be able to navigate to `localhost:5000` if working correctly, you will see a landing page with "Used Car Sales Data" at the top. 

## My Approach

I started this challenge with some exploration of the dataset, this process is detailed in the jupyter notebook `data-exploration.ipynb`. As stated in the challenge description, this dataset is quite messy. I designed some ETL steps to clean up the data and prepare it for insertion in the SQLite database. In summary, there appeared to be lots of duplicated records in the csv file, as if someone had accidentally copy pasted the entire contents into the middle of the file. I decided to remove the duplicated data then performed some standard cleaning operations such as standardizing string case, stripping off extra whitespace etc... These methods can be found in `etl.py` which gets called by the `create_db()` method in `db.py`. Upon initialization, Flask also uses these methods to create the SQLite database if one does not exist.

The Flask API server is launched using `api.py` and is exposed on port 5000 by default. It can be accessed via URL, in browser or using `curl` for example. Data is returned in JSON format.

Database schema design is outlined in the pdf files found under `schema-designs`. I realized late into the challenge that my design could be improved, at that point I was too far into the challenge to implement the redesign into the API. However, I would argue that the original design is a workable solution for the current dataset. The redesigned schema would scale more effectively and could accomodate additional datapoints I could forsee being added in the future.

## API Documentation

### 'GET' Methods

#### 'GET' All 

`/api/v1/resources/{endpoint}/all`

This will return all records for a given endpoint in JSON format.

Potential endpoints include:
	sales: "sales" records.
	vehicles: "vehicles" records.
	stores: "stores" records.
	vehicles_sold: "JOIN" operation on all 3 tables, resembles data from the original csv file. 

#### 'GET' Filter 

`/api/v1/resources/{endpoint}`

This will return filtered records for a given endpoint based on query parameters in JSON format.

Parameters can be specified and added to the end of the URL. 

Example:`localhost:5000/api/v1/resources/sales?id=9&purch_val=9000&sale_loc=9`

Parameters:
	id: optional
	purch_val: optional
	sale_loc: optional

Potential endpoints include:
	sales: "sales" records.

#### 'GET' COUNT 

`/api/v1/resources/{endpoint}/count/{method}`

This will return counts for a given endpoint based on an aggregate method.

Examples:
`/api/v1/resources/sales/count/by_store`: returns count of sales grouped by store location. 
`/api/v1/resources/vehicles_sold/count/by_brand`: returns count of vehicles sold grouped by vehicle brand.

#### 'GET' AVERAGE 

`/api/v1/resources/{endpoint}/average/{method}`

This will return counts for a given endpoint based on an aggregate method.

Examples:
`/api/v1/resources/sales/average/purchase_by_store`: returns average purchase price grouped by store location.

### 'POST' Methods

`/api/v1/resources/{endpoint}/insert`

This will insert new records for a given endpoint based on query parameters.

Parameters can be specified and added to the end of the URL.

Potential endpoints include:
	sales: "sales" records.
	vehicles: "vehicles" records.
	stores: "stores" records.

#### 'POST' Insert Sale Record

Parameters:
	vin: *required*
	location_num: *required*
	purch_val: optional
	sale_loc: optional
	odometer: optional
	color_sold: optional

#### 'POST' Insert Vehicle Record

Parameters:
	vin: optional
    	car_year: optional
    	color: optional
    	make: optional
    	veh_body: optional
    	engine_type: optional
    	engine_liters: optional
    	car_type: optional
    	brand: optional
    	veh_type: optional
    	fuel_type: optional
    	transmission: optional 
 
#### 'POST' Insert Store Record

Parameters:
	location_num: optional
 
### 'PUT' Methods

`/api/v1/resources/{endpoint}/update`

This will existing records for a given endpoint based on query parameters.

Parameters can be specified and added to the end of the URL.

Potential endpoints include:
	sales: "sales" records.
	vehicles: "vehicles" records.

#### 'PUT' Update Sale Record

Parameters:
	id: *required*
	purch_val: optional
	sale_loc: optional
	odometer: optional
	color_sold: optional

#### 'PUT' Insert Vehicle Record

Parameters:
	id: *required*
	vin: optional
    	car_year: optional
    	color: optional
    	make: optional
    	veh_body: optional
    	engine_type: optional
    	engine_liters: optional
    	car_type: optional
    	brand: optional
    	veh_type: optional
    	fuel_type: optional
    	transmission: optional

### 'DELETE' Methods

`/api/v1/resources/{endpoint}/delete`

This will delete existing records for a given endpoint based on query parameters.

Parameters can be specified and added to the end of the URL.

Potential endpoints include:
	sales: "sales" records.

#### 'DELETE' Delete Sale Record

Parameters:
	id: *required*

# Data Engineering Code Challenge	

## Introduction

Imagine that you work in the technology department of used car dealership chain and you've been tasked to develop a solution
that enables other developers to get access to a messy dataset. The information in the dataset will be used for two main tasks:
 
1. Generating reports regarding monthly purchases of vehicles by store
2. Fetching information about specific vehicles, as well as vehicles coming from specific stores 

Your goal is to design a solution that allows other users to programmatically access the information contained in the
dataset in an easy way.   

#### Skills assessment

The purpose of this code challenge is to assess:

* Your ability to work with messy data
* Your understanding of SQL databases, including but not limited to: schema design, query patterns, and normalization
* Your knowledge of API design and general software engineering skills

## Actual Task

Create a RESTful API to interact with the dataset. Make sure to include the following functionality:

* Standard CRUD operations on a particular data point
* Ability to fetch aggregate data on a dimension of your choice. Ideas are: number of vehicles purchased per store, 
* Filtering based on price and store location
average purchase price per store, sorted list of most commonly sold makes/brands, etc. 
* Must use a SQL-based database, we recommend SQLite to minimize development overhead

A few notes:
* Focus on how you'd design a schema that enables evolution over time with minimal overhead
* Keep performance considerations in mind when designing indexes, and make sure to document the trade-offs that your decisions will entail

## Data

The [data](data/data_engineering_dataset.csv) you will use for this code challenge is a historical snapshot of vehicles that have been sold by a used car dealership across multiple stores. 

### Data dictionary 

| Column Title    | Column Description                                 |
| --------------- | -------------------------------------------------- |
| VIN             | Vehicle Identification Number (Unique vehicle ID)  | 
| CarYear         | Model year of vehicle                              | 
| Color           | Color of vehicle                                   |
| VehBody         | Body type                                          |
| EngineType      | Engine size in cylinders                           |
| Make            | Model name                                         |
| Miles           | Odometer reading at time of inventory              |
| SaleType        | (R) for resale, (N) for new vehicle                |
| Odometer        | Accuracy of odometer reading                       |
| Brand           | Vehicle make                                       |
| VehType         | Passenger, Truck, or Motorcycle                    |
| LocationNum     | ID number of store that acquired vehicle           |
| CarType         | Vehicle segment type                               |
| EngineLiters    | Engine displacement in Liters                      |
| FuelType        | Fuel type of vehicle                               |
| Transmission    | Transmission type of vehicle                       |
| SaleLoc         | ID number of dealership that sold vehicle          |
| PurchVal        | Purchase price of vehicle                          |

