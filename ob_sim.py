from orderbook_v35 import OrderBook  
import time
from datetime import datetime
import threading
import random
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.animation import FuncAnimation
import bisect


class OrderBookSimulator:
    def __init__(self):
        self.order_book = OrderBook()
    
    def _generate_random_order(self):
        side = random.choices(["Bid", "Ask"],weights=[0.55,0.45],k=1)[0]  
        price = round(random.triangular(80,105,98),2) if side == "Bid" else round(random.triangular(95,120,102),2)  
        quantity = random.randint(1,10)  
        order_type = random.choices(["Market","Limit","FOK", "IOC"],weights=[0.15,0.75,0.05,0.05],k=1)[0]  
        darkpool = random.choices([True, False],weights=[0.2,0.8],k=1)[0]  
        
        return price, quantity, side, time.time(), order_type, darkpool

    def _generate_orders(self):
        while True:
            order_params = self._generate_random_order()
            self.order_book.add_order(*order_params)
            time.sleep(0.0001) 

    def _remove_expired_orders(self):
        while True:
            self.order_book.remove_expired_orders()
            time.sleep(30)  
   
   # Plotting
    def _plot_order_book_graph(self):
        fig, ax = plt.subplots(figsize=(10, 6))

        def _update_plot(frame):
            bid_prices,_, bid_cumsum, ask_prices,_, ask_cumsum, average_slippage = self._get_order_book_data()

            ax.clear()

            if bid_prices:
                ax.step(bid_prices, bid_cumsum, color='green', linewidth=2, label="bids", where='post')
                ax.fill_between(bid_prices, bid_cumsum, alpha=0.3, step='post', color='green')

            if ask_prices:
                ax.step(ask_prices, ask_cumsum, color='red', linewidth=2, label="asks", where='post')
                ax.fill_between(ask_prices, ask_cumsum, alpha=0.3, step='post', color='red')
            
            best_bid = bid_prices[0] if bid_prices else None
            best_ask = ask_prices[0] if ask_prices else None

            mid_price = round((best_bid + best_ask) / 2,2) if (best_bid and best_ask) else 0
            spread = round(best_ask - best_bid,2) if mid_price else 0

            imbalance = round((bid_cumsum[-1] - ask_cumsum[-1]) / (bid_cumsum[-1] + ask_cumsum[-1]),2)
            imbalance_description = self._get_imbalance_description(imbalance)

            slippage_percent = (average_slippage / mid_price) * 100 if (average_slippage and mid_price) else 0

            annotations = []
            if best_bid:
                annotations.append(f"Best Bid: {best_bid}")
            if best_ask:
                annotations.append(f"Best Ask: {best_ask}")
            if spread:
                annotations.append(f"Spread: {spread}")

            annotations1 = []
            if imbalance:
                annotations1.append(f"Imbalance: {imbalance} ({imbalance_description})")
            if average_slippage:
                annotations1.append(f"Slippage: {average_slippage} ({slippage_percent:.2f}% of Mid Price)")    

            ax.text(0.5, 0.95, ' | '.join(annotations), transform=ax.transAxes, fontsize=10, ha='center', bbox=dict(facecolor='white', edgecolor='black'))
            ax.text(0.5, 0.85, ' | '.join(annotations1), transform=ax.transAxes, fontsize=10, ha='center', bbox=dict(facecolor='white', edgecolor='black'))

            ax.set_xlabel("price")
            ax.set_ylabel("cumulative quantity")
            ax.set_title("Order Book Depth Chart")
            ax.legend()

        ani = FuncAnimation(fig, _update_plot, interval=2000) 
        plt.show()

    def _get_order_book_data(self,depth=None):
        bid_prices,bid_quantities, ask_prices, ask_quantities = [], [], [], []

        for order_id, price,_ in self.order_book.bids:
            if self.order_book.orders[order_id].expiry_time < time.time():
                continue
            quantity = self.order_book.orders[order_id].quantity  
            idx_bid = self._bisect_left_reverse(bid_prices, price) 
            bid_prices.insert(idx_bid, price)
            bid_quantities.insert(idx_bid, quantity)
            if depth is not None and len(bid_prices) > depth:
                break

        for order_id, price, _  in self.order_book.asks:
            if self.order_book.orders[order_id].expiry_time < time.time():
                continue
            quantity = self.order_book.orders[order_id].quantity  
            idx_ask = bisect.bisect_right(ask_prices, price)
            ask_prices.insert(idx_ask, price)
            ask_quantities.insert(idx_ask, quantity)
            if depth is not None and len(ask_prices) > depth:
                break

        bid_cumsum = np.cumsum(bid_quantities)
        ask_cumsum = np.cumsum(ask_quantities)

        average_slippage = round(self.order_book.total_slippage / self.order_book.total_executed_quantity if (self.order_book.total_slippage and self.order_book.total_executed_quantity) else 0,2)


        return bid_prices,bid_quantities, bid_cumsum, ask_prices,ask_quantities, ask_cumsum, average_slippage

    def _plot_order_book_table(self):
        while True:
            self._build_order_book_table()
            time.sleep(2)

    def _build_order_book_table(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        bid_prices,bid_quantities, bid_cumsum, ask_prices,ask_quantities, ask_cumsum, average_slippage = self._get_order_book_data(depth=8)

        mid_price = round((bid_prices[0] + ask_prices[0]) / 2,2) if (bid_prices and ask_prices) else 0
        spread = round(ask_prices[0] - bid_prices[0],2) if mid_price else 0

        imbalance = round((bid_cumsum[-1] - ask_cumsum[-1]) / (bid_cumsum[-1] + ask_cumsum[-1]),2) if (bid_cumsum.size > 0 and ask_cumsum.size > 0) else 0
        imbalance_description = self._get_imbalance_description(imbalance)

        slippage_percent = (average_slippage / mid_price) * 100 if (average_slippage and mid_price) else 0


        print("Order Book Depth")
        print("\n" + "-" * 70)

        print("\nAsks:")
        print("{:<15} | {:<20} | {:<20}".format("Price", "Quantity", "Cumulative Quantity"))
        for price, qty, cum_qty in zip(ask_prices[::-1], ask_quantities[::-1], ask_cumsum[::-1]):
            print(f"{price:<15.2f} | {qty:<20.0f} | {cum_qty:<20.0f}")

        print("\n" + "-" * 70,"\n")
        print(f"Mid Price: {mid_price}   |   Spread: {spread}")
        print("\n")
        print(f"Imbalance: {imbalance} ({imbalance_description})   |   Slippage: {average_slippage} ({slippage_percent:.2f}% of Mid Price)")
        print("\n" + "-" * 70,"\n")

        print("Bids:")
        print("{:<15} | {:<20} | {:<20}".format("Price", "Quantity", "Cumulative Quantity"))
        for price, qty, cum_qty in zip(bid_prices, bid_quantities, bid_cumsum):
            print(f"{price:<15.2f} | {qty:<20.0f} | {cum_qty:<20.0f}")
        
        print("\n" + "-" * 70,"\n")


    # Helpers
    def _bisect_left_reverse(self, arr, x):
        low, high = 0, len(arr)
        while low < high:
            mid = (low + high) // 2
            if arr[mid] < x:  
                high = mid
            else:
                low = mid + 1
        return low

    def _get_imbalance_description(self, imbalance):
        if imbalance > 0.2:
            return "Very Bullish"
        elif imbalance > 0.05:
            return "Bullish"
        elif imbalance > -0.05:
            return "Neutral Market"
        elif imbalance > -0.2:
            return "Bearish"
        else:
            return "Very Bearish" 

    # Simulation
    def run(self):
        threading.Thread(target=self._generate_orders, daemon=True).start()
        threading.Thread(target=self._remove_expired_orders, daemon=True).start()
        threading.Thread(target=self._plot_order_book_graph, daemon=True).start()          # keep this thread or the below
        # threading.Thread(target=self._plot_order_book_table, daemon=True).start()

        start_time = time.time()
        duration = 60  # Run for 60 seconds (1 minute)     #  INPUT #
        while time.time() - start_time < duration:
            time.sleep(2)  

        print("Simulation complete")

if __name__ == "__main__":
    simulator = OrderBookSimulator()
    simulator.run()

