from orderbook_v35 import OrderBook
from ob_sim import OrderBookSimulator
import cProfile
import pstats
import pandas as pd

def _run_sim():
    simulator = OrderBookSimulator()
    simulator.run()
    print(f"max order id is {len(simulator.order_book.orders)}")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    _run_sim()

    profiler.disable()
    stats = pstats.Stats(profiler)

    data = []
    for key, value in stats.stats.items():
        filename, line_number, func_name = key
        ncalls, _, tottime, cumtime, _ = value
        
        percall_total = tottime / ncalls if isinstance(ncalls, int) and ncalls > 0 else 0
        percall_cum = cumtime / ncalls if isinstance(ncalls,int) and ncalls > 0 else 0

        data.append([filename, line_number, func_name, ncalls, tottime, percall_total, cumtime,percall_cum])

    df = pd.DataFrame(data, columns=['Filename', 'Line Number', 'Function', '# calls', 'Total time', 'Percall (Total)', 'Cum. time',"Percall (Cum.)"])

    df.to_excel('profile_output.xlsx', index=False)

