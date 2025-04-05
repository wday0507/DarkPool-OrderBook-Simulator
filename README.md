# **Order Book Simuation**

## **Project Overview**

## **Project Motivation**
I completed this project in order to develop and demonstrate my skills in python, data structures and algorithms as well as improving my understanding of market microstructure.

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
This file test the logic of all 16 matching functions. Specifically it tests:
       - Full matching
       - Partial matching
       - FIFO - do orders match with the earliest order when choosing between 2 orders at the same price
       - Price priorty - do orders always match at the best possible price
       - Darkpool logic - do visible (darkpool) orders always match opposing visible (darkpool) orders

### **ob_sim**
This file generates random bid and ask orders so we can visualise the matching that takes place in the order book. The file concurrently genreates ordesr, removes expired orders, and generates the orderbook visualisation. The user can choose between an orderbook graph and chart (discussed below).

### **ob_profiler**
This file generates an excel workbook that breaks down the simulation time into how much time was spent in each function, this is useful for optimising code performance.



## **Outputs**

### **Order Book Graph**
The below chart depicts the cumulative quantities of visible orders at each given price level. 

![image](https://github.com/user-attachments/assets/a47bf610-43f6-4efb-a2f6-02fe93ab04fd)


### **Order Book Table**

The below table shows a summary of the 8 most competitive bid and ask orders in the order book and their respective quantities.

![image](https://github.com/user-attachments/assets/cef939f2-c233-462a-83d3-563a7ae0f901)


### **Profiling Results**
The below is a screenshot of the profiling results from the ob_profiler file. This decomposes the 60 second orderbook simulation into the time spent in each function. 
This was very useful for streamlining my code, for example FOK orders require calculating the available quantity in the book that can match with this order. Initially, I crudelly used a sum() list comprehension over both the visible and darkpool orderbooks to calculate the avialable quantity. The profiling results highlighted how time consuming this was, which was concerning since only 5% of orders are FOK, I changed my approach to only iterate over the orderbook and stop when I knew there was at least as much available quantity in the book as the order required. This makes a big difference when the orderbook grows very large.


![image](https://github.com/user-attachments/assets/11a31476-8231-4fe6-808b-18d373525a60)


## **How to run the project**

## **Design Choices**
Data Structures
1/ Order Book (bids, asks, darkpool bids, darkpool asks)
The order book uses a sorted list to store active orders, maintaining an efficient structure for price priority with minimal memory overhead. Each order is represented by its essential attributes (order ID, price, timestamp). The sorted list provides O(log n) time complexity for insertion and deletion, making it more efficient than a simple list when managing a large volume of orders.
................ why is it better than a heap

2/ Orders
All active and inactive orders are stored in a dictionary. This allows for constant time access to any order's attributes.


## **Future Improvements**
1/ Language Limitation
This project is implemented in Python, because I am currently focused on developing my proficiency in the language. While Python is excellent for development and readability, it is not the best option for high frequency trading systems. An obvious future enhancement would be to write the code in a compiled language (e.g. C or C++), which would provide significant speed improvements and better control over memory management.

2/ Extend Matching Logic
To further enhance realism, advanced order behaviors could be added:
       - New Order Types: Add support for stop orders (triggered when price crosses a threshold) and iceberg orders (only partially visible in the book, with hidden size revealed over time). 
       - Order Modification and cancellation: Enable live adjustment or cancellation of active orders, where participants react to changing market conditions.


3. User Interaction
The simulation runs autonomously by generating random orders. An improvement would be allowing users to interact with the order book in real time, for example:
       - Manually submitting buy/sell orders via a simple interface
       - Observing immediate feedback and position changes
       - This would transform the project from a passive simulation to an interactive trading demonstration

## **Contact Info**
email: william.day@live.com
