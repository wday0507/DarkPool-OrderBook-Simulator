from orderbook_v35 import OrderBook

class OrderBookTester:
    def __init__(self, orderbook_class):
        self.ob = orderbook_class()
    
    def _reset(self):
        self.ob = OrderBook()  
    
    def _run_tests(self):
        tests = [
            ("test_add_bid_market_darkpool", self._test_add_bid_market_darkpool),
            ("test_add_bid_market_visible", self._test_add_bid_market_visible),
            ("test_add_bid_limit_darkpool", self._test_add_bid_limit_darkpool),
            ("test_add_bid_limit_visible", self._test_add_bid_limit_visible),
            ("test_add_bid_fok_darkpool", self._test_add_bid_fok_darkpool),
            ("test_add_bid_fok_visisble", self._test_add_bid_fok_visisble),
            ("test_add_bid_ioc_darkpool", self._test_add_bid_ioc_darkpool),
            ("test_add_bid_ioc_visible", self._test_add_bid_ioc_visible),
            ("test_add_ask_market_darkpool", self._test_add_ask_market_darkpool),
            ("test_add_ask_market_visible", self._test_add_ask_market_visible),
            ("test_add_ask_limit_darkpool", self._test_add_ask_limit_darkpool),
            ("test_add_ask_limit_visible", self._test_add_ask_limit_visible),
            ("test_add_ask_fok_darkpool",self._test_add_ask_fok_darkpool),
            ("test_add_ask_fok_visible", self._test_add_ask_fok_visible),
            ("test_add_ask_ioc_darkpool", self._test_add_ask_ioc_darkpool),
            ("test_add_ask_ioc_visible", self._test_add_ask_ioc_visible)]
        
        results = []

        for name, test in tests:
            result = test()
            results.append((name, result))

        if all(result for _, result in results):
            print("Passed")
        
    def _test_add_bid_market_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Market", darkpool=True)
        assert self.ob.bids == [] and self.ob.asks == [] and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-market-darkpool -> Full matching not working"  

        # Partial Matching
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=7, order_time=5, side="Bid", order_type="Market", darkpool=True)
        assert self.ob.orders[2].quantity == 2 and self.ob.darkpool_bids == [(2,100,5)] and len(self.ob.darkpool_bids) == 1 and len(self.ob.bids) == 0 and len(self.ob.asks) == 0, "bid-market-darkpool -> Partial matching not working"

        # FIFO
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=6, side="Bid", order_type="Market", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.orders[2].order_time == 5 and len(self.ob.darkpool_bids) == 0 and len(self.ob.bids) == 0, "Bid-market-darkpool -> FIFO logic is not working"  

        # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=5, order_time=1, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=99, quantity=5, order_time=3, side="Bid", order_type="Market", darkpool=True)
        assert self.ob.orders[1].price == 101, "bid-market-darkpool -> price priority logic not working"

        # Darkpool / Visible Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=11, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=12, side="Bid", order_type="Market", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.darkpool_asks) == 0 and self.ob.orders[1].quantity == 5 and len(self.ob.asks) == 1, "bid-market-darkpool -> darkpool / visible priority logic not working"  

        return True

    def _test_add_bid_market_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=101, quantity=5, order_time=2, side="Ask", order_type="Market", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [] and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-market-visible -> Full matching not working"  

        # Partial Matching
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=7, order_time=10, side="Bid", order_type="Market", darkpool=False)
        assert self.ob.orders[2].quantity == 2 and self.ob.bids == [(2,100,10)] and len(self.ob.bids) == 1 and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-market-visible -> Partial matching not working"

        # FIFO
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=6, side="Bid", order_type="Market", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.orders[2].order_time == 5 and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [] and self.ob.darkpool_bids == [], "bid-market-visible -> FIFO not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=5, order_time=1, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=99, quantity=5, order_time=3, side="Bid", order_type="Market", darkpool=False)
        assert self.ob.orders[1].price == 101, "bid-market-visible -> price priority logic not working"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=11, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=12, side="Bid", order_type="Market", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and self.ob.orders[1].quantity == 5 and len(self.ob.darkpool_asks) == 1, "bid-market-visible -> darkpool/visible priority logic not working"  

        return True
    
    def _test_add_bid_limit_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="Limit", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-limit-darkpool -> Full Matching of bid limit order not working"

        # Partial Matching
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=4, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Bid", order_type="Limit", darkpool=True)
        assert self.ob.darkpool_bids == [(2,100,5)] and self.ob.orders[2].quantity == 2 and len(self.ob.darkpool_bids) == 1 and len(self.ob.darkpool_asks) == 0, "bid-limit-darkpool -> Partial execution of bid limit order not working"
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Bid", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1, "bid-limit-darkpool -> FIFO execution for limit bid orders not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.darkpool_asks == [(1,101,6)] and self.ob.orders[1].price == 101 and len(self.ob.darkpool_bids) == 0, "bid-limit-darkpool -> price priority for ask limit visible not working"

        # Limit order logic
        self._reset()
        self.ob.add_order(price=101, quantity=5, order_time=9, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Bid", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and len(self.ob.darkpool_asks) == 1, "bid-limit-darkpool -> Limit bid should not execute if no suitable ask price available"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.asks) == 1 and len(self.ob.darkpool_asks) == 0, "bid-limit-darkpool -> darkpool / visible priority logic not working"

        return True

    def _test_add_bid_limit_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="Limit", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "bid-limit-visible -> Full Matching of bid limit order not working"

        # Partial Matching
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=4, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Bid", order_type="Limit", darkpool=False)
        assert self.ob.bids == [(2,100,5)] and self.ob.orders[2].quantity == 2 and len(self.ob.bids) == 1 and len(self.ob.asks) == 0, "bid-limit-visible -> Partial execution of bid limit order not working"
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Bid", order_type="Limit", darkpool=False)
        assert len(self.ob.asks) == 1, "bid-limit-visible -> FIFO execution for limit bid orders not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="Limit", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.asks == [(1,101,6)] and self.ob.orders[1].price == 101 and len(self.ob.bids) == 0, "bid-limit-visible -> price priority for ask limit visible not working"

        # Limit order logic
        self._reset()
        self.ob.add_order(price=101, quantity=5, order_time=9, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Bid", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 1 and len(self.ob.asks) == 1, "bid-limit-visible ->  limit bid should not execute if no suitable ask price available"

        # darkpool / visible logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_asks) == 1, "bid-limit-visible -> Visible orders should execute before darkpool"


        return True

    def _test_add_bid_fok_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=37, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=29, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=66, order_time=3, side="Bid", order_type="FOK", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-fok-darkpool -> Full Matching not working"

        # Partial Matching
        # N/A
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Bid", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.darkpool_asks == [(3,100,8)] and self.ob.orders[3].quantity == 10, "bid-fok-darkpool -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.darkpool_asks == [(1,101,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.darkpool_bids) == 0, "bid-fok-darkpool -> price priority not working"

        # FOK order logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=9, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Bid", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.darkpool_asks) == 1, "bid-fok-darkpool -> FOK logic not working"

        # Darkpool / Visible Logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.asks) == 1 and len(self.ob.darkpool_asks) == 0, "bid-fok-darkpool -> Visible / darkpool logic not working "
        return True

    def _test_add_bid_fok_visisble(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=37, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=29, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=66, order_time=3, side="Bid", order_type="FOK", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "bid-fok-visible -> Full Matching not working"

        # Partial Matching
        # N/A
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Bid", order_type="FOK", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.asks == [(3,100,8)] and self.ob.orders[3].quantity == 10, "bid-fok-visible -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="FOK", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.asks == [(1,101,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.bids) == 0, "bid-fok-visible -> price priority logic not working"

        # # FOK order logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=9, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Bid", order_type="FOK", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 1, "bid-fok-visible -> FOKlogic not working"

        # Visible / Darkpool Logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="FOK", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_asks) == 1, "bid-fok-visible -> Visible / darkpool priority logic not working"

        return True

    def _test_add_bid_ioc_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=102, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=7, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=109, order_time=3, side="Bid", order_type="IOC", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-ioc-darkpool -> Full Matching not working"

        # Partial Matching
        # N/A

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Bid", order_type="IOC", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.darkpool_asks == [(3,100,8)] and self.ob.orders[3].quantity == 10, "bid-ioc-darkpool -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="IOC", darkpool=True)
        assert len(self.ob.darkpool_asks) == 1 and self.ob.darkpool_asks == [(1,101,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.darkpool_bids) == 0, "bid-ioc-darkpool -> price priority not working"

        # # IOC order logic
        self._reset()
        self.ob.add_order(price=100, quantity=4, order_time=9, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Bid", order_type="IOC", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "bid-ioc-darkpool -> IOC logic not working"

        # Visible / Darkpool logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="IOC", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.asks) == 1 and len(self.ob.darkpool_asks) == 0, "bid-ioc-darkpool -> Visible / darkpool priority logic not working" 

        return True

    def _test_add_bid_ioc_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=102, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=7, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=109, order_time=3, side="Bid", order_type="IOC", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "bid-ioc-visible -> Full Matching not working"

        # Partial Matching
        # N/A

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Bid", order_type="IOC", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.asks == [(3,100,8)] and self.ob.orders[3].quantity == 10, "bid-ioc-visible -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=3, order_time=6, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=5, order_time=8, side="Bid", order_type="IOC", darkpool=False)
        assert len(self.ob.asks) == 1 and self.ob.asks == [(1,101,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.bids) == 0, "bid-ioc-visible -> price priority not working"

        # # IOC order logic
        self._reset()
        self.ob.add_order(price=100, quantity=4, order_time=9, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Bid", order_type="IOC", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "bid-ioc-visible -> IOC logic not working"

        # Darkpool / Visible Logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Ask", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Bid", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_asks) == 1, "bid-ioc-visible -> Visible / darkpool priority logic not working" 


        return True

    def _test_add_ask_market_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Market", darkpool=True)
        assert self.ob.bids == [] and self.ob.asks == [] and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-market-darkpool -> Full matching not working"  

        # Partial Matching
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=7, order_time=5, side="Ask", order_type="Market", darkpool=True)
        assert self.ob.orders[2].quantity == 2 and self.ob.darkpool_asks == [(2,100,5)] and len(self.ob.darkpool_asks) == 1 and len(self.ob.bids) == 0 and len(self.ob.asks) == 0, "ask-market-darkpool -> Partial matching not working"

        # FIFO
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=6, side="Ask", order_type="Market", darkpool=True)
        assert len(self.ob.darkpool_asks) == 0 and self.ob.orders[2].order_time == 5 and len(self.ob.darkpool_bids) == 1 and len(self.ob.bids) == 0, "ask-market-darkpool -> FIFO not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=99, quantity=5, order_time=1, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=101, quantity=5, order_time=3, side="Ask", order_type="Market", darkpool=True)
        assert self.ob.orders[1].price == 99, "ask-market-darkpool -> price priority not working"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=11, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=12, side="Ask", order_type="Market", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.darkpool_asks) == 0 and len(self.ob.bids) == 1, "ask-market-darkpool -> darkpool / visible priority not working"  


        return True

    def _test_add_ask_market_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Ask", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Market", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [] and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-market-visible -> Full matching not working"  

        # Partial Matching
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=4, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=7, order_time=5, side="Ask", order_type="Market", darkpool=False)
        assert self.ob.orders[2].quantity == 2 and self.ob.asks == [(2,100,5)] and len(self.ob.asks) == 1 and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-market-visible -> Partial matching not working"

        # FIFO
        self._reset()                                          
        self.ob.add_order(price=100, quantity=5, order_time=14, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=15, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=16, side="Ask", order_type="Market", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.orders[2].order_time == 15 and self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-market-visible -> FIFO not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=101, quantity=5, order_time=1, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=99, quantity=5, order_time=3, side="Ask", order_type="Market", darkpool=False)
        assert self.ob.orders[1].price == 101, "ask-market-visible -> price priority not working"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=10, side="Bid", order_type="Market", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=11, side="Bid", order_type="Market", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=12, side="Ask", order_type="Market", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_bids) == 1, "ask-market-visible -> Visible / darkpool priority logic not working"  

        return True

    def _test_add_ask_limit_darkpool(self):
        #Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="Limit", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-limit-dakrpool -> Full Matching not working"

        # Partial Matching
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=4, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Ask", order_type="Limit", darkpool=True)
        assert self.ob.darkpool_asks == [(2,100,5)]and self.ob.orders[2].quantity == 2 and len(self.ob.darkpool_asks) == 1 and len(self.ob.darkpool_bids) == 0, "ask-limit-dakrpool -> Partial execution not working" 

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1, "ask-limit-dakrpool -> FIFO execution for limit ask orders not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and self.ob.darkpool_bids == [(1,100,6)] and self.ob.orders[1].price == 100 and len(self.ob.darkpool_asks) == 0, "ask-limit-dakrpool -> price priority not working"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.bids) == 1 and len(self.ob.darkpool_asks) == 0, "ask-limit-dakrpool -> Visible / dakrpool priority logic not working"

        # Limit Order Logic
        self._reset()
        self.ob.add_order(price=1000, quantity=5, order_time=9, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=1001, quantity=5, order_time=10, side="Ask", order_type="Limit", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and len(self.ob.darkpool_asks) == 1, "ask-limit-dakrpool -> Limit order logic not working"

        return True
    
    def _test_add_ask_limit_visible(self):
        #Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="Limit", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "ask-limit-visible -> Full Matching not working"

        # Partial Matching
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=4, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=5, side="Ask", order_type="Limit", darkpool=False)
        assert self.ob.asks == [(2,100,5)]and self.ob.orders[2].quantity == 2 and len(self.ob.asks) == 1 and len(self.ob.bids) == 0, "ask-limit-visible -> Partial execution not working" 

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 1, "ask-limit-visible -> FIFO not working"

        # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.bids == [(1,100,6)] and self.ob.orders[1].price == 100 and len(self.ob.asks) == 0, "ask-limit-visible -> price priority not working"

        # Visible / Darkpool Priority
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_bids) == 1, "ask-limit-visible -> Visible / darkpool priority logic not working"

        # Limit Order Logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=9, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=5, order_time=10, side="Ask", order_type="Limit", darkpool=False)
        assert len(self.ob.bids) == 1 and len(self.ob.asks) == 1, "ask-limit-visible -> Limit order logic not working"

        return True

    def _test_add_ask_fok_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=47, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=29, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=76, order_time=3, side="Ask", order_type="FOK", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-fok-darkpool -> Full Matching not working"

        # Partial Matching
        # N/A
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100,quantity=20, order_time=6,side="Bid",order_type="Limit",darkpool=True)
        self.ob.add_order(price=100,quantity=20,order_time=7,side="Bid",order_type="Limit",darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Ask", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and self.ob.darkpool_bids == [(3,100,8)] and self.ob.orders[3].quantity == 10, "ask-fok-darkpool -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and self.ob.darkpool_bids == [(1,100,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.darkpool_asks) == 0, "ask-fok-darkpool -> price priority not working"

        # # FOK order logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=9, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Ask", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_asks) == 0 and len(self.ob.darkpool_bids) == 1, "ask-fok-darkpool -> FOK logic not working"

        # Darkpool / visible logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="FOK", darkpool=True)
        assert len(self.ob.darkpool_bids) == 0 and len(self.ob.bids) == 1 and len(self.ob.darkpool_asks) == 0, "ask-fok-darkpool -> Visible / darkpool priority logic not working"


        return True

    def _test_add_ask_fok_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=47, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=29, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=76, order_time=3, side="Ask", order_type="FOK", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "ask-fok-visible -> Full Matching not working"

        # Partial Matching
        # N/A
        
        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Ask", order_type="FOK", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.bids == [(3,100,8)] and self.ob.orders[3].quantity == 10, "ask-fok-visible -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="FOK", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.bids == [(1,100,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.asks) == 0, "ask-fok-visible -> price priority not working"

        # # FOK order logic
        self._reset()
        self.ob.add_order(price=100, quantity=5, order_time=9, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Ask", order_type="FOK", darkpool=False)
        assert len(self.ob.asks) == 0 and len(self.ob.bids) == 1, "ask-fok-visible -> FOK logic not working"

        # Darkpool / visible logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="FOK", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_bids) == 1, "ask-fok-visible -> Visible / darkpool priority logic not working"

        return True

    def _test_add_ask_ioc_darkpool(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=1102, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=17, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=1119, order_time=3, side="Ask", order_type="IOC", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-ioc-darkpool -> Full Matching not working"

        # Partial Matching
        # N/A

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Ask", order_type="IOC", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and self.ob.darkpool_bids == [(3,100,8)] and self.ob.orders[3].quantity == 10 and self.ob.darkpool_asks == [], "ask-ioc-darkpool -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="IOC", darkpool=True)
        assert len(self.ob.darkpool_bids) == 1 and self.ob.darkpool_bids == [(1,100,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.darkpool_asks) == 0, "ask-ioc-darkpool -> price priority not working"

        # # IOC order logic
        self._reset()
        self.ob.add_order(price=100, quantity=4, order_time=9, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Ask", order_type="IOC", darkpool=True)
        assert self.ob.darkpool_bids == [] and self.ob.darkpool_asks == [], "ask-ioc-darkpool -> IOC logic not working"

        # darkpool / visible logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="IOC", darkpool=True)
        assert len(self.ob.bids) == 1 and len(self.ob.darkpool_bids) == 0 and len(self.ob.darkpool_asks) == 0, "ask-ioc-darkpool -> Visible / darkpool logic not working" 


        return True

    def _test_add_ask_ioc_visible(self):
        # Full Matching
        self._reset()
        self.ob.add_order(price=100, quantity=1102, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=17, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=1119, order_time=3, side="Ask", order_type="IOC", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "ask-ioc-visible -> Full Matching not working"

        # Partial Matching
        # N/A

        # FIFO
        self._reset()
        self.ob.add_order(price=100, quantity=20, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=20, order_time=8, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=50, order_time=10, side="Ask", order_type="IOC", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.bids == [(3,100,8)] and self.ob.orders[3].quantity == 10 and self.ob.asks == [], "ask-ioc-visible -> FIFO not working"

        # # Price Priority
        self._reset()
        self.ob.add_order(price=100, quantity=3, order_time=6, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=101, quantity=3, order_time=7, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=8, side="Ask", order_type="IOC", darkpool=False)
        assert len(self.ob.bids) == 1 and self.ob.bids == [(1,100,6)] and self.ob.orders[1].quantity == 1 and len(self.ob.asks) == 0, "ask-ioc-visible -> price priority not working"

        # # IOC order logic
        self._reset()
        self.ob.add_order(price=100, quantity=4, order_time=9, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=6, order_time=10, side="Ask", order_type="IOC", darkpool=False)
        assert self.ob.bids == [] and self.ob.asks == [], "ask-ioc-visible -> IOC logic not working"

        # Darkpool / visible logic
        self._reset() 
        self.ob.add_order(price=100, quantity=5, order_time=1, side="Bid", order_type="Limit", darkpool=True)
        self.ob.add_order(price=100, quantity=5, order_time=2, side="Bid", order_type="Limit", darkpool=False)
        self.ob.add_order(price=100, quantity=5, order_time=3, side="Ask", order_type="IOC", darkpool=False)
        assert len(self.ob.bids) == 0 and len(self.ob.asks) == 0 and len(self.ob.darkpool_bids) == 1, "ask-ioc-visible -> Visible / darkpool priority logic not working" 

        return True

    

tester = OrderBookTester(OrderBook)
tester._run_tests()
