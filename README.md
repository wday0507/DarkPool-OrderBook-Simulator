# **Order Book Simuation**

## **Project Overview**

## **Project Motivation**

## **File Descriptions**
### **orderbook_v35**
This file is the main file of the project. It contains classes for orders and orderbooks. 

The Order class  creates order objects.
Orders can be:
       - Bid / Ask (side)
       - Market / Limit / Fill-or-Kill / Immediate-or-Cancel (order type)
       - Visible / Darkpool (order visibility to market participants)

The Orderbook class deals with processing orders, matching and maintaining the order book. 
The key data structures are:
      - A list of bid orders
      - A list of ask orders
      - A list of darkpool bid orders
      - A list of darkpool ask orders
      - A dictionary of all orders (active and inactive)

Visisble and darkpool orders are separated in this way because I assume visible orders always try and match with visible orders before darkpool orders (ditto for darkpool orders). 
The orderbook lists store:
        - order id (for unique identification)
        - price (so orders can be sorted by price)
        - time (if orders have the same price, they must respect the FIFO principle)
        
These are the order attributes that are essential for placing orders in the book correctly. The dictionary of all orders is accessed to obtain other attributes such as quantity, expirty time, order_type, etc...
      
The Orderbook class has 16 separate functions to process specific order types. 2 sides, 4 order types, 2 visiblity options -> 16.

Each of the 16 functions works differently, but they all contain the same core logic:
       1/ match order with opposing side orders from the visible book (for visisble orders, vice versa for darkpool orders)
       2/ if part of the order is not filled, match with opposing side of the darkpool book (for visisble orders, vice versa for darkpool orders)
       3/ if part of the order is not filled, add it to the orderbook

Some unique features of the matching logic include (but is not limited to):
              - Visisble market orders -> track slipapge to measure market liquidity
              - Limit orders -> only match with prices equal to or better than the order price
              - FOK orders -> calcualte the sum of availble asks (for bid orders) that are available to match with before proceeding

### **test_orderbook**

### **ob_sim**

### **ob_profiler**



## **Outputs**

### **Order Book Graph**

### **Order Book Table**

### **Profiling Results**


## **How to run the project**

## **Design Choices**

## **Future Improvements**

## **Contact Info**
