## 0.3.0

### Features
* new **peg order module** added for peg orders.
* peg to market order added with basic arguments
* new **models** module added. This contains basic model for converting and manipulating data
* new **utils** module added that contains utility and helper functions. Functions added
	* create_basic_positions_from_orders_dict
	* dict_filter
	* tick 
	* stop_loss_step_decimal
* mandatory arguments for order placement for zerodha broker added. `order_place, order_modify, order_cancel` would now add default arguments for the broker automatically (such as variety);you could override them with kwargs.
* cover_orders function added to broker class, this checks for all valid orders and place stop loss in case of non-matching orders


## 0.2.0

### Features
* **BREAKING CHANGE:** Database model changed
* `Order, CompoundOrder` models changed from dataclass to pydantic models
* database class changed to sqlite_utils from native python sqlite3 for better reading and writing, connection now returns `sqlite_utils.Database` instead of `sqlite3.Connection`.
* #3 `Order` could now be directly added using the `add` method and this inherits the sqlite3 database from the compound order if no connection is specified
* #8 save method added to save orders to database in bulk
* #6 maximum limit for modifications to an order added

### Fixes
* close_all_positions bug fixed by changing status to upper case and including canceled and rejected orders in completed orders
* cancel_all_orders do not cancel already completed orders

### Internals

* `_attrs` now made part of model instead of a property
* tests updated to reflect the new database type


## 0.1.4
* modify order to accept any parameter

## 0.1.3
* save to database on execution

## 0.1.2
* fixes in brokers
* order arguments during execution in compound orders

## 0.1.1
* database support for saving orders added
