from typing import Literal
import time
from sortedcontainers import SortedList

class Order:
    def __init__(self, price: float, quantity: int, side: str, order_time: int, order_id: int, order_type: str, darkpool: bool, expiry_time: int, expected_price=None):
        self.price = price
        self.quantity = quantity
        self.side = side
        self.order_time = order_time
        self.order_id = order_id  
        self.order_type = order_type
        self.darkpool = darkpool
        self.expiry_time = expiry_time
        self.expected_price = expected_price

class OrderBook:
    def __init__(self):
        self.bids = SortedList(key=lambda x: (-x[1], x[2]))
        self.asks = SortedList(key=lambda x: (x[1], x[2]))
        self.darkpool_bids = SortedList(key=lambda x: (-x[1], x[2]))
        self.darkpool_asks = SortedList(key=lambda x: (x[1], x[2]))
        self.orders = {}
        self.order_id = 0
        self.total_slippage = 0
        self.total_executed_quantity = 0 

    def add_order(self, price: float, quantity: int, side: Literal["Bid", "Ask"],order_time, order_type: Literal["Market", "Limit", "FOK", "IOC"], darkpool: bool = False):
            
        assert isinstance(price, (int, float)) and price > 0, "Price must be +ve"
        assert isinstance(quantity, int) and quantity > 0, "Quantity must be +ve"
        assert side in {"Bid", "Ask"}, "side must be 'Bid' / 'Ask'."
        assert order_type in {"Market", "Limit", "FOK", "IOC"}, "Invalid order type, must be -> Market / Limit /FOK / IOC"
        assert isinstance(darkpool, bool), "darkpool must be a boolean type"
        
        self.order_id += 1
        expiry_duration = 30 # INPUT
        expiry_time = order_time + expiry_duration
        order = Order(price, quantity, side, order_time, self.order_id, order_type, darkpool, expiry_time) 
        self.orders[self.order_id] = order
        
        return self._order_routing(order)

    def _add_bid_market_darkpool(self, order):
        self._process_order(order)
        self._add_to_book(self.darkpool_bids, order)

    def _add_bid_market_visible(self, order):
        order.expected_price = self.asks[0][1] if self.asks else None
        self._process_order(order)
        self._add_to_book(self.bids, order)

    def _add_bid_limit_darkpool(self, order):
        self._process_order(order)
        self._add_to_book(self.darkpool_bids, order)

    def _add_bid_limit_visible(self, order):
        self.orders[self.order_id] = order
        self._process_order(order)
        self._add_to_book(self.bids, order)

    def _add_bid_fok_darkpool(self, order):
        total_available = self._available_quantity(order)
        if total_available < order.quantity:
            return 
        self._process_order(order)

    def _add_bid_fok_visible(self, order):
        total_available = self._available_quantity(order)
        if total_available < order.quantity:
            return  
        self._process_order(order)

    def _add_bid_ioc_darkpool(self, order):
        self._process_order(order)

    def _add_bid_ioc_visible(self, order):
        self._process_order(order)

    def _add_ask_market_darkpool(self, order):
        self._process_order(order)
        self._add_to_book(self.darkpool_asks, order)

    def _add_ask_market_visible(self, order):
        order.expected_price = self.bids[0][1] if self.bids else None
        self._process_order(order)
        self._add_to_book(self.asks, order)

    def _add_ask_limit_darkpool(self, order):
        self._process_order(order)
        self._add_to_book(self.darkpool_asks, order)

    def _add_ask_limit_visible(self, order):
        self._process_order(order)
        self._add_to_book(self.asks, order)

    def _add_ask_fok_darkpool(self, order):
        total_available = self._available_quantity(order)
        if total_available < order.quantity:
            return  
        self._process_order(order)

    def _add_ask_fok_visible(self, order):
        total_available = self._available_quantity(order)
        if total_available < order.quantity:
            return  
        self._process_order(order)

    def _add_ask_ioc_darkpool(self, order):
        self._process_order(order)

    def _add_ask_ioc_visible(self, order):
        self._process_order(order)


    # helper functions
    def _order_routing(self,order):
        routing_table = {
            ("Bid", "Market", True): self._add_bid_market_darkpool,
            ("Bid", "Market", False): self._add_bid_market_visible,
            ("Bid", "Limit", True): self._add_bid_limit_darkpool,
            ("Bid", "Limit", False): self._add_bid_limit_visible,
            ("Bid", "FOK", True): self._add_bid_fok_darkpool,
            ("Bid", "FOK", False): self._add_bid_fok_visible,
            ("Bid", "IOC", True): self._add_bid_ioc_darkpool,
            ("Bid", "IOC", False): self._add_bid_ioc_visible,
            ("Ask", "Market", True): self._add_ask_market_darkpool,
            ("Ask", "Market", False): self._add_ask_market_visible,
            ("Ask", "Limit", True): self._add_ask_limit_darkpool,
            ("Ask", "Limit", False): self._add_ask_limit_visible,
            ("Ask", "FOK", True): self._add_ask_fok_darkpool,
            ("Ask", "FOK", False): self._add_ask_fok_visible,
            ("Ask", "IOC", True): self._add_ask_ioc_darkpool,
            ("Ask", "IOC", False): self._add_ask_ioc_visible}

        key = (order.side, order.order_type, order.darkpool)
        return routing_table[key](order)

    def _available_quantity(self,order):
        total_available = 0
        required_qty = order.quantity

        _opposite_book = self._opposite_book(order)

        for order_id, price, _  in _opposite_book:
            if (order.side == "Bid" and price > order.price) or (order.side == "Ask" and price < order.price):
                break  
            total_available += self.orders[order_id].quantity
            if total_available >= required_qty:
                return total_available  
        
        _alternative_opposite_book = self._alternative_opposite_book(order)

        if total_available < required_qty:
            for order_id, price, _ in _alternative_opposite_book:
                if (order.side == "Bid" and price > order.price) or (order.side == "Ask" and price < order.price):
                    break
                total_available += self.orders[order_id].quantity
                if total_available >= required_qty:
                    return total_available  

        return total_available

    def _opposite_book(self, order):
        opposite_book_map = {
            ("Bid", True): self.darkpool_asks,
            ("Bid", False): self.asks,
            ("Ask", True): self.darkpool_bids,
            ("Ask", False): self.bids}
        
        return opposite_book_map[(order.side, order.darkpool)] 
    
    def _alternative_opposite_book(self, order):
        alt_opposite_book_map = {
            ("Bid", True): self.asks,
            ("Bid", False): self.darkpool_asks,
            ("Ask", True): self.bids,
            ("Ask", False): self.darkpool_bids}
        
        return alt_opposite_book_map[(order.side, order.darkpool)] 

    def _process_order(self, order):
        _book_sequence = self._book_sequence(order)

        for book in _book_sequence:
            self._process_book(order, book)
            if order.quantity <= 0:
                break
    
    def _book_sequence(self, order):
        if order.side == "Bid":
            return [self.darkpool_asks, self.asks] if order.darkpool else [self.asks, self.darkpool_asks]
        else:
            return [self.darkpool_bids, self.bids] if order.darkpool else [self.bids, self.darkpool_bids]

    def _process_book(self, order, _opposite_book):
        while _opposite_book and order.quantity > 0:
            best_order_id, best_price, best_order_time  = _opposite_book[0]
            best_order = self.orders[best_order_id]

            if order.order_type == "Market":
                if not order.darkpool:
                    executed_quantity = min(best_order.quantity, order.quantity)
                    executed_price = best_price 
                    self._track_slippage(order, executed_price, executed_quantity)
                self._match(order, best_order, _opposite_book)
            else:
                if self._check_price(order,best_price):
                    self._match(order, best_order, _opposite_book)
                else:
                    break

    def _match(self, order, best_order, _opposite_book):
        if best_order.quantity > order.quantity:
            best_order.quantity -= order.quantity
            order.quantity = 0
        elif best_order.quantity == order.quantity:
            del _opposite_book[0] 
            order.quantity = 0
        else:
            order.quantity -= best_order.quantity
            del _opposite_book[0] 

    def _track_slippage(self, order, executed_price, executed_quantity):
        if not order.expected_price:
            return
        
        self.total_slippage += abs(executed_price - order.expected_price) * executed_quantity
        self.total_executed_quantity += executed_quantity

    def _check_price(self,order,best_price):
        return (order.price >= best_price) if order.side == "Bid" else (order.price <= best_price)

    def _add_to_book(self, book, order):
        if order.quantity > 0:
            book.add((self.order_id, order.price, order.order_time)) 

    def remove_expired_orders(self):
        for book in [self.bids, self.asks, self.darkpool_bids, self.darkpool_asks]:
            for order in list(book):
                if time.time() >= self.orders[order[0]].expiry_time:  
                    book.discard(order)  
