# Data-Warehouse-Framework

framework

## Global default parameters

yesterday=
executor=hive
  
## Dependency

pip install python-dotenv

## Usage

```shell
python main.py
python main.py --help
python main.py --version
python main.py warehouse
python main.py warehouse dim_date
python main.py warehouse dim_date start_date=2010-01-01 end_date=2029-12-31
python main.py warehouse ods_yb_master_info 
python main.py utils to_excel --sql="select * from dim_date" -o output/dim_date.xlsx  --verbose
python main.py utils get_schema
python main.py utils get_schema dim
```
