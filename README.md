# **Order Book Simuation**

## **Project Overview**
This project simulates an electronic order book, it handles limit, market, FOK and IOC order types. It supports both visible and dark pool orders, and matches orders based on price priority and FIFO rules. It also includes
- a testing file to ensure robustness
- a profiling tool for performance analysis.
- a simulation module that generates random orders for visualisation

It is implemented in Python, with efficient data structures such as sorted lists and dictionaries for managing orders.

&nbsp;<br>

## **Project Motivation**
I completed this project in order to develop and demonstrate my skills in python, data structures and algorithms as well as improving my understanding of market microstructure.

&nbsp;<br>

## **File Descriptions**
### **orderbook_v35**
This is the main module of the project. It contains classes for orders and orderbooks. 

The Order class creates order objects. Orders can be:
- Side: Bid / Ask
- Type: Market / Limit / Fill or Kill (FOK) / Immediate or Cancel (IOC)
- Visibility: Visible / Dark pool

&nbsp;<br>
The Orderbook class deals with processing orders, matching and maintaining the order book. 
The key data structures are:
- A list of bid orders
- A list of ask orders
- A list of darkpool bid orders
- A list of darkpool ask orders
- A dictionary of all orders (active and inactive)

&nbsp;<br>
Visible and dark pool orders are separated to reflect the assumption that:
- Visible orders prioritize matching against visible orders.
- Dark pool orders prioritize matching against dark pool orders.

&nbsp;<br>
Each order stored in the book contains:
- Order ID (unique identification of orders)
- Price (for sorting orders by price)
- Timestamp (for FIFO ordering at equal prices)
        
The dictionary of all orders is accessed to obtain other attributes such as quantity, expiry time, order type, etc...

&nbsp;<br>
There are 16 order matching functions to handle different combinations of:
- 2 sides (Bid/Ask)
- 4 order types (Market, Limit, FOK, IOC)
- 2 visibility levels (Visible, Darkpool)

&nbsp;<br>
Each function follows a general pattern:
- Attempt to match the order with the opposing side of the visible book (or dark pool book, depending on order visibility).
- If the order is not filled, attempt to match with the opposing side of the darkpool book (or vice versa).
- If still unfilled, add the remaining order to the book.

&nbsp;<br>
Some unique features of individual matching functions include (but is not limited to):
- Visisble market orders -> track slipapge to measure market liquidity
- Limit orders -> only match with prices equal to or better than the order price
- FOK orders -> calculate availble matchable volume before processing the order to ensure full fill

&nbsp;<br>
### **test_orderbook**
This file test the logic of all 16 matching functions. Specifically it tests:
- Full matching - orders are fully matched if possible
- Partial matching - orders can be partially filled if there isn’t enough liquidity to fill the entire order.
- FIFO - orders match with the earliest order when choosing between 2 orders at the same price
- Price priorty - orders always match at the best possible price
- Darkpool logic - orders always match with opposing orders of the same visiblity first

&nbsp;<br>
### **ob_sim**
This file generates random bid and ask orders to simulate and visualise order book activity. It concurrently generates orders, removes expired orders, and updates the orderbook visualisation. The user can choose between a graph view and chart view (discussed below).

&nbsp;<br>
### **ob_profiler**
This file produces an excel workbook that breaks down total simulation time by function call. It’s useful for optimising the code.

&nbsp;<br>
## **Outputs**

### **Order Book Graph**
The chart below displays the cumulative quantities of visible orders at each price level. When the simulation is run, it updates in real time.

![image](https://github.com/user-attachments/assets/a47bf610-43f6-4efb-a2f6-02fe93ab04fd)

&nbsp;<br>
### **Order Book Table**

The table below shows a summary of the 8 most competitive bid and ask orders in the order book and their respective quantities. When the simulation is run, this updates in real time.

![image](https://github.com/user-attachments/assets/cef939f2-c233-462a-83d3-563a7ae0f901)

&nbsp;<br>
### **Profiling Results**
Below is a screenshot of the profiling results from the ob_profiler file. It decomposes the 60 second order book simulation into the time spent in each function. This was useful for streamlining my code.

For example, FOK orders require calculating the available quantity in the book that can match with the order. Initially, I used a crude sum() list comprehension over both the visible and dark pool order books to calculate the available quantity. The profiling results highlighted how time-consuming this approach was, which was concerning, especially since only 5% of orders are FOK.

To optimise, I changed the approach to iterate over the order book and stop once I knew there was at least as much available quantity as required by the order. This change significantly improved performance, especially as the order book grows larger.

![image](https://github.com/user-attachments/assets/11a31476-8231-4fe6-808b-18d373525a60)

&nbsp;<br>
## **How to run the project**

1/ Clone Repository
Clone the repository to your local machine

git clone https://github.com/wday0507/DarkPool-OrderBook-Simulator.git

and then navigate to project directory with the actual path to where you cloned the project

cd C:\Users\**********\DarkPool-OrderBook-Simulator

&nbsp;<br>

2/ Install Dependencies

pip install -r requirements.txt

&nbsp;<br>

3/ Running the code

To run the files, execute the following:

Simulation -> python ob_sim.py

Testing workbook -> python test_orderbook.py

Profiling code -> python ob_profiler.py

&nbsp;<br>

## **Design Choices**
&nbsp;<br>
1/ Active Order Book 
&nbsp;<br>

The order book uses a sorted list to store active orders. A sorted list is a list data structure that automatically keeps its elements in order according to a given sorting critera, in this case, by price then time.

A sorted list is useful in an order book because it ensures that you can easily access the highest bid and the lowest ask without having to search through the entire list. It also makes insertion efficient O(log n), ensuring that the order book can scale efficiently with a large volume of orders.

Initially, I started this project by experimenting with more basic data structures, like list and dictionaries, to store orders. Both these structures come with significant drawbacks:
- List: insertion and deletion of orders would take O(n) time because you'd need to search through the entire lis. Finding the best order would also require scanning the entire list each time.
- Dictionary: allows for constant time access to orders, but it doesnt maintain any order, making it ineffective for an order book where price priority is critical.

The sorted list improves upon these by providing an efficient way to keep the orders sorted at all times, allowing you to quickly access the best prices for matching and manage insertion and deletion in O(log n) time.

As the project progressed, I experimented with both a sorted list and a heap to manage the order book. Conceptually, both structures seemed to fulfill the core requirements of order matching, as they both provide efficient insertion and deletion with price priority. However, through performance testing, I found that sorted lists slightly outperformed heaps in my specific use case.

&nbsp;<br>

2/ Global Order Dictionary

All active and inactive orders are stored in a dictionary. This enables constant time access to any order's attributes. The dictionary structure is ideal for fast lookups and ensures efficient management of orders across different states (active, inactive, filled, visisble, darkpool etc..).

&nbsp;<br>
## **Future Improvements**
1/ Language Limitation

This project is implemented in Python, because I am currently focused on developing my proficiency in the language. While Python is excellent for development and readability, it is not the best option for high frequency trading systems. An obvious future enhancement would be to write the code in a compiled language (e.g. C or C++), which would provide significant speed improvements and better control over memory management.

&nbsp;<br>


2/ Extend Matching Logic

To further enhance realism, advanced order features could be added:
- New Order Types: Add support for stop orders (triggered when price crosses a threshold) and iceberg orders (only partially visible in the book, with hidden size revealed over time)
- Order Modification and cancellation: Enable live adjustment or cancellation of active orders, where participants react to changing market conditions

&nbsp;<br>


3/ User Interaction

The simulation runs autonomously by generating random orders. An improvement would be allowing users to interact with the order book in real time, for example:
- Manually submitting buy/sell orders via an interface
- Observing immediate feedback and position changes. This would transform the project from a passive simulation to an interactive trading demonstration

&nbsp;<br>
## **Contact Info**
email: william.day@live.com
